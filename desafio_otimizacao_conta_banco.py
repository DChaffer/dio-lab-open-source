import datetime

# Listas para armazenar usuários e contas
usuarios = []
contas = []

# Funções utilitárias

def buscar_usuario_por_cpf(cpf):
    for usuario in usuarios:
        if usuario['cpf'] == cpf:
            return usuario
    return None

# Funções de operações bancárias

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    if numero_saques >= limite_saques:
        return saldo, extrato, "Operação não realizada, número de saques diários excedido."
    elif valor > limite:
        return saldo, extrato, "Não é possível realizar este saque, o limite por saque é de R$500."
    elif saldo >= valor:
        saldo -= valor
        numero_saques += 1
        extrato.append(f"Saque: R${valor:.2f} - {datetime.datetime.now()}")
        return saldo, extrato, f"Saque de R${valor:.2f} realizado com sucesso!"
    else:
        return saldo, extrato, "Saldo insuficiente!"

def depositar(saldo, valor, extrato):
    if valor > 0:
        saldo += valor
        extrato.append(f"Depósito: R${valor:.2f} - {datetime.datetime.now()}")
        return saldo, extrato, f"Depósito de R${valor:.2f} realizado com sucesso!"
    else:
        return saldo, extrato, "Favor depositar apenas valores inteiros e positivos."

def exibir_extrato(saldo, *, extrato):
    if not extrato:
        return "Nenhuma movimentação realizada."
    else:
        extrato_str = "Extrato:\n"
        for transacao in extrato:
            extrato_str += transacao + "\n"
        extrato_str += f"\nSaldo atual: R${saldo:.2f}"
        return extrato_str

# Funções para criar usuários e contas

def criar_usuario(nome, data_nascimento, cpf, endereco):
    if buscar_usuario_por_cpf(cpf) is not None:
        return "Usuário com este CPF já cadastrado."
    usuario = {
        'nome': nome,
        'data_nascimento': data_nascimento,
        'cpf': cpf,
        'endereco': endereco
    }
    usuarios.append(usuario)
    return "Usuário criado com sucesso!"

def criar_conta_corrente(cpf):
    usuario = buscar_usuario_por_cpf(cpf)
    if usuario is None:
        return "Usuário não encontrado."
    agencia = "0001"
    numero_conta = len(contas) + 1
    conta = {
        'agencia': agencia,
        'numero_conta': numero_conta,
        'usuario': usuario
    }
    contas.append(conta)
    return f"Conta criada com sucesso! Agência: {agencia}, Número da conta: {numero_conta}"

# Menu e fluxo principal

def main():
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
    [4] Criar usuário
    [5] Criar conta corrente
    [0] Sair

    => """

    while True:
        opcao = input(menu)

        if opcao == "1":
            try:
                valor = int(input("Digite o valor a ser depositado: "))
                saldo, extrato, msg = depositar(saldo, valor, extrato)
                print(msg)
            except ValueError:
                print("Favor depositar apenas valores inteiros e positivos.")
        elif opcao == "2":
            try:
                valor = int(input("Digite o valor a ser sacado: "))
                saldo, extrato, msg = sacar(
                    saldo=saldo, valor=valor, extrato=extrato,
                    limite=limite_saque, numero_saques=numero_saques,
                    limite_saques=limite_saques_diarios
                )
                print(msg)
            except ValueError:
                print("Favor sacar apenas valores inteiros e positivos.")
        elif opcao == "3":
            print(exibir_extrato(saldo, extrato=extrato))
        elif opcao == "4":
            nome = input("Nome: ")
            data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
            cpf = input("CPF: ")
            endereco = input("Endereço (logradouro, número, bairro, cidade/estado): ")
            print(criar_usuario(nome, data_nascimento, cpf, endereco))
        elif opcao == "5":
            cpf = input("CPF do usuário: ")
            print(criar_conta_corrente(cpf))
        elif opcao == "0":
            print("Obrigado por usar o sistema bancário. Até logo!")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
