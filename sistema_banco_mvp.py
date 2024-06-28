import datetime

saldo = 0
limite_saque = 500
limite_diario_saque = 1500
numero_saques = 0
limite_saques_diarios = 3
extrato = []

menu = """
Seja bem-vindo! Escolha a opção desejada:

[1] Depositar
[2] Sacar
[3] Extrato
[0] Sair

=> """


def depositar(valor):
    global saldo, extrato
    if valor > 0:
        saldo += valor
        extrato.append(f"Depósito: R${valor:.2f} - {datetime.datetime.now()}")
        print(f"Depósito de R${valor:.2f} realizado com sucesso!")
    else:
        print("Favor depositar apenas valores inteiros e positivos.")


def sacar(valor):
    global saldo, numero_saques, extrato
    if numero_saques >= limite_saques_diarios:
        print("Operação não realizada, número de saques diários excedido.")
    elif valor > limite_saque:
        print("Não é possível realizar este saque, o limite por saque é de R$500.")
    elif (valor + sum([float(trans.split("R$")[1]) for trans in extrato if
                       'Saque' in trans and trans.split()[-1][:10] == datetime.datetime.now().strftime(
                               '%Y-%m-%d')])) > limite_diario_saque:
        print("Operação não realizada, o valor de limite diário é de R$1500.")
    elif saldo >= valor:
        saldo -= valor
        numero_saques += 1
        extrato.append(f"Saque: R${valor:.2f} - {datetime.datetime.now()}")
        print(f"Saque de R${valor:.2f} realizado com sucesso!")
    else:
        print("Saldo insuficiente!")


def exibir_extrato():
    global saldo, extrato
    if not extrato:
        print("Nenhuma movimentação realizada.")
    else:
        print("Extrato:")
        for transacao in extrato:
            print(transacao)
        print(f"\nSaldo atual: R${saldo:.2f}")


while True:
    opcao = input(menu)

    if opcao == "1":
        try:
            valor = int(input("Digite o valor a ser depositado: "))
            depositar(valor)
        except ValueError:
            print("Favor depositar apenas valores inteiros e positivos.")
    elif opcao == "2":
        try:
            valor = int(input("Digite o valor a ser sacado: "))
            sacar(valor)
        except ValueError:
            print("Favor sacar apenas valores inteiros e positivos.")
    elif opcao == "3":
        exibir_extrato()
    elif opcao == "0":
        print("Obrigado por usar o sistema bancário. Até logo!")
        break
    else:
        print("Opção inválida, tente novamente.")
