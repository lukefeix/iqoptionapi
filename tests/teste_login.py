

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # raiz do projeto

from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
from tabulate import tabulate
from colorama import init, Fore, Back

API = ''
init(autoreset=True)
green = Fore.GREEN
yellow = Fore.YELLOW
red = Fore.RED
white = Fore.WHITE
greenf = Back.GREEN
yellowf = Back.YELLOW
redf = Back.RED
blue = Fore.BLUE

print(green+'''
      
    ██╗     ██╗   ██╗ ██████╗ █████╗ ███████╗     ██████╗ ██████╗ ██████╗ ███████╗
    ██║     ██║   ██║██╔════╝██╔══██╗██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
    ██║     ██║   ██║██║     ███████║███████╗    ██║     ██║   ██║██║  ██║█████╗  
    ██║     ██║   ██║██║     ██╔══██║╚════██║    ██║     ██║   ██║██║  ██║██╔══╝  
    ███████╗╚██████╔╝╚██████╗██║  ██║███████║    ╚██████╗╚██████╔╝██████╔╝███████╗
    ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝'''+yellow+'''
                                                                                
                            https://www.youtube.com/@lucascode

''')

print(yellow + '***************************************************************************************\n\n')



email = ''
senha = ''


def conexao():
    global API
    print(yellow+'Iniciando Conexão com a IQ_Option')
    API = IQ_Option(email,senha)

    check, reason = API.connect()
    if check:
        print(green + '\nConectado com sucesso')
    else:
        if reason == '{"code":"invalid_credentials","message":"You entered the wrong credentials. Please ensure that your login/password is correct."}':
            print(red+'\nEmail ou senha incorreta')
            sys.exit()
        elif reason == "2FA":
            
            codigo = input('>> Sua conta tem autenticação de 2 fatores, digite o código enviado no seu email ou celular: ')
            while True:
                status, reason = API.connect(codigo)

                if status:
                    print(green + '\nConectado com sucesso')
                    break
                else:
                    codigo = input('O código digitado está errado, digite novamente: ')


        else:
            print(red+ '\nHouve um problema na conexão')

            print(reason)
            sys.exit()

def tipo_conta():
    ### Função para Selecionar demo ou real ###
    while True:
        escolha = input(green+'\n>>'+ white +' Selecione a conta em que deseja conectar:\n'+
                                green+'>>'+ white +' 1 - Demo\n'+
                                green+'>>'+ white +' 2 - Real\n'+
                                green+'>>'+ white +' 3 - Torneio\n'+
                                green+'-->'+ white +' ')
        
        escolha =  int(escolha)

        if escolha == 1:
            conta = 'PRACTICE'
            print('Conta demo selecionada')
            break
        if escolha == 2:
            conta = 'REAL'
            print('Conta real selecionada')
            break
        if escolha == 3:
            conta = 'TOURNAMENT'
            print('Conta torneio selecionada')
            break
        else:
            print(red+'Escolha incorreta! Digite 1, 2 ou 3')
            
    API.change_balance(conta)

def dados_conta():
    print('>> Puxando dados da conta:')
    perfil = API.get_profile_ansyc()
    cifrao = str(perfil['currency_char'])
    nome = str(perfil['name'])

    valorconta = float(API.get_balance())

    print('\nOlá, ',nome, '\nSeja bem vindo.')
    print('Seu Saldo na conta é de', cifrao,valorconta)

def puxa_abertos():

    print('>> Puxando pares abertos        ',end = '\r')
    abertos = API.get_all_open_time()   # {'binary'/'turbo'/'digital': {par: {'open': True/False}}}
    lucros = API.get_all_profit()       # {par: {'binary': 0.86, 'turbo': 0.87}}

    payouts = {}
    pares = []

    pares2 = []
    pares3 = []


    for tipo in ['binary','turbo','digital']:
        payouts[tipo]={}
        for par in abertos[tipo]:
            if par not in pares:
                pares.append(par)
            if abertos[tipo][par]['open']:
                if tipo =='binary' or tipo =='turbo':
                    if par not in pares2:
                        pares2.append(par)
                    payouts[tipo][par] = round(lucros[par][tipo] * 100) if tipo in lucros[par] else 0
                if tipo =='digital':
                    pares3.append(par)
                    payouts[tipo][par] = 'Aberto'
            else:
                payouts[tipo][par] = 'Fechado' if tipo == 'digital' else 0

    print(f'Existem {len(pares3)} abertos nas digitais')
    print(f'Existem {len(pares2)} abertos nas binarias')

    pays= []
    for par in pares:
        try:
            turbo = payouts['turbo'][par]
        except:
            turbo = 0

        try:
            digi = payouts['digital'][par]
        except:
            digi = '-'
        try:
            bin = payouts['binary'][par]
        except:
            bin = 0

        pays.append([par,bin,turbo,digi])


    print(tabulate(pays,headers=['PAR','BINARY','TURBO','DIGITAL'], tablefmt="simple_grid", numalign="center"))


def puxa_payout():
    lucros = API.get_all_profit()   # mesma puxada do puxa_abertos: {par: {'binary': 0.86, 'turbo': 0.87}}

    for par in ['EURUSD-OTC', 'EURUSD-op']:
        print(f'>> Puxando payout do {par}')
        binary = round(lucros[par]['binary'] * 100) if 'binary' in lucros[par] else 0
        turbo = round(lucros[par]['turbo'] * 100) if 'turbo' in lucros[par] else 0
        digital = API.get_digital_payout(par, 5)   # espera até ~5s; 0 se não vier
        time.sleep(1)   # deixa chegar alguma resposta atrasada antes do próximo par
        print(f'   Binary: {binary}%  |  Turbo: {turbo}%  |  Digital: {digital}%\n')

def puxa_candles():

    print('>> PUXANDO ULTIMAS 5 VELAS DO PAR EURUSD')

    velas = API.get_candles('EURUSD-OTC', 60, 5, time.time())
    hora0 = datetime.fromtimestamp(velas[-5]['from']).strftime('%H:%M')
    hora1 = datetime.fromtimestamp(velas[-4]['from']).strftime('%H:%M')
    hora2 = datetime.fromtimestamp(velas[-3]['from']).strftime('%H:%M')
    hora3 = datetime.fromtimestamp(velas[-2]['from']).strftime('%H:%M')
    hora4 = datetime.fromtimestamp(velas[-1]['from']).strftime('%H:%M')

    velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
    velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'
    velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'
    velas[-4] = 'Verde' if velas[-4]['open'] < velas[-4]['close'] else 'Vermelha' if velas[-4]['open'] > velas[-4]['close'] else 'Doji'
    velas[-5] = 'Verde' if velas[-5]['open'] < velas[-5]['close'] else 'Vermelha' if velas[-5]['open'] > velas[-5]['close'] else 'Doji'

    cores = velas[-5] ,velas[-4], velas[-3] ,velas[-2] ,velas[-1] 

    if  velas[-5] =='Verde':
        Vela0 = Back.GREEN+ '       '
    elif  velas[-5] =='Vermelha':
        Vela0 = Back.RED+ '       '
    elif  velas[-5] =='Doji':
        Vela0 = Back.WHITE+ '       '
        
    if  velas[-4] =='Verde':
        Vela1 = Back.GREEN+ '       '
    elif  velas[-4] =='Vermelha':
        Vela1 = Back.RED+ '       '
    elif  velas[-4] =='Doji': 
        Vela1 = Back.WHITE+ '       '
        
    if  velas[-3] =='Verde':
        Vela2 = Back.GREEN+ '       '
    elif  velas[-3] =='Vermelha':
        Vela2 = Back.RED+ '       '
    elif  velas[-3] =='Doji':
        Vela2 = Back.WHITE+ '       '
        
    if  velas[-2] =='Verde':
        Vela3 = Back.GREEN+ '       '
    elif  velas[-2] =='Vermelha':
        Vela3 = Back.RED+ '       '
    elif  velas[-2] =='Doji':
        Vela3 = Back.WHITE+ '       '
        
    if velas[-1] =='Verde': 
        Vela4 = Back.GREEN+ '       '
    elif velas[-1] =='Vermelha':
        Vela4 = Back.RED+ '       '
    elif velas[-1] =='Doji':
        Vela4 = Back.WHITE+ '       '

    print('\n')
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('  ', Vela0, ' ', Vela1, ' ', Vela2, ' ', Vela3, ' ', Vela4)
    print('   ', str(hora0), '   ', str(hora1), '   ', str(hora2), '   ', str(hora3), '   ', str(hora4))
    print('')              
                  
def buy_checkwin():
    print('>> FUNÇÃO PARA ABRIR ORDEM E CHEcAR RESULTADO')
    entrada = 10
    exp = 1
    par = 'EURUSD-op'
    direcao = 'call'


    check, id = API.buy(entrada, par, direcao, exp)

    if check:
        print('\nEntrada realizada com o ID:',str(id))
        print('Aguardando resultado...\n')

        status , resultado = API.check_win_v4(id)

        if resultado > 0:
            print(f'{yellow} ↪ {white}Resultado da ordem:\n   Par: {par}  |  {green}Resultado: WIN{white}   |  Lucro: {str(round(resultado,2))}\n')
        elif resultado == 0:
            print(f'{yellow} ↪ {white}Resultado da ordem:\n   Par: {par}  |  {yellow}Resultado: EMPATE{white}   |  Lucro: {str(round(resultado,2))}\n')
        else:
            print(f'{yellow} ↪ {white}Resultado da ordem:\n   Par: {par}  |  {red}Resultado: LOSS{white}   |  Lucro: {str(round(resultado,2))}\n')
    else:
        print(id)



conexao()
print(yellow + '\n\n***************************************************************************************\n\n')

tipo_conta()
print(yellow + '\n\n***************************************************************************************\n\n')

dados_conta()
print(yellow + '\n\n***************************************************************************************\n\n')

puxa_abertos()
print(yellow + '\n\n***************************************************************************************\n\n')

puxa_payout()
print(yellow + '\n\n***************************************************************************************\n\n')

puxa_candles()
print(yellow + '\n\n***************************************************************************************\n\n')

buy_checkwin()
print(yellow + '\n\n***************************************************************************************\n\n')
