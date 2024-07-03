import datetime
from abc import ABC, abstractmethod

# Classe Cliente
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

# Classe PessoaFisica
class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

# Classe Conta
class Conta:
    def __init__(self, cliente, numero):
        self.saldo = 0.0
        self.numero = numero
        self.agencia = "0001"
        self.cliente = cliente
        self.historico = Historico()

    def saldo(self):
        return self.saldo

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)

    def sacar(self, valor):
        if valor > self.saldo:
            print("Saldo insuficiente!")
            return False
        self.saldo -= valor
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Deposite apenas valores positivos!")
            return False
        self.saldo += valor
        return True

# Classe ContaCorrente
class ContaCorrente(Conta):
    def __init__(self, cliente, numero, limite=500, limite_saques=3):
        super().__init__(cliente, numero)
        self.limite = limite
        self.limite_saques = limite_saques

# Classe Historico
class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(transacao)

    def listar_transacoes(self):
        for transacao in self.transacoes:
            print(transacao)

# Interface Transacao
class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass

# Classe Deposito
class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(f"Depósito: R${self.valor:.2f} - {datetime.datetime.now()}")

# Classe Saque
class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(f"Saque: R${self.valor:.2f} - {datetime.datetime.now()}")

# Funções para gerenciamento de clientes e contas
clientes = []
contas = []

def buscar_cliente_por_cpf(cpf):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def criar_usuario(nome, data_nascimento, cpf, endereco):
    if buscar_cliente_por_cpf(cpf) is not None:
        return "Usuário com este CPF já cadastrado."
    cliente = PessoaFisica(endereco, cpf, nome, data_nascimento)
    clientes.append(cliente)
    return "Usuário criado com sucesso!"

def criar_conta_corrente(cpf):
    cliente = buscar_cliente_por_cpf(cpf)
    if cliente is None:
        return "Usuário não encontrado."
    numero_conta = len(contas) + 1
    conta = ContaCorrente(cliente, numero_conta)
    cliente.adicionar_conta(conta)
    contas.append(conta)
    return f"Conta criada com sucesso! Agência: {conta.agencia}, Número da conta: {conta.numero}"

def depositar(cliente, conta, valor):
    deposito = Deposito(valor)
    cliente.realizar_transacao(conta, deposito)

def sacar(cliente, conta, valor):
    saque = Saque(valor)
    cliente.realizar_transacao(conta, saque)

def exibir_extrato(conta):
    print(f"Extrato da conta {conta.numero}:")
    conta.historico.listar_transacoes()
    print(f"Saldo atual: R${conta.saldo:.2f}")

# Menu principal
def main():
    menu = """
    Seja bem-vindo! Escolha a opção desejada:

    [1] Criar usuário
    [2] Criar conta corrente
    [3] Depositar
    [4] Sacar
    [5] Extrato
    [0] Sair

    => """

    while True:
        opcao = input(menu)

        if opcao == "1":
            nome = input("Nome: ")
            data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
            cpf = input("CPF: ")
            endereco = input("Endereço (logradouro, número, bairro, cidade/estado): ")
            print(criar_usuario(nome, data_nascimento, cpf, endereco))
        elif opcao == "2":
            cpf = input("CPF do usuário: ")
            print(criar_conta_corrente(cpf))
        elif opcao == "3":
            cpf = input("CPF do usuário: ")
            cliente = buscar_cliente_por_cpf(cpf)
            if cliente:
                numero_conta = int(input("Número da conta: "))
                conta = next((c for c in cliente.contas if c.numero == numero_conta), None)
                if conta:
                    valor = float(input("Digite o valor a ser depositado: "))
                    depositar(cliente, conta, valor)
                else:
                    print("Conta não encontrada.")
            else:
                print("Cliente não encontrado.")
        elif opcao == "4":
            cpf = input("CPF do usuário: ")
            cliente = buscar_cliente_por_cpf(cpf)
            if cliente:
                numero_conta = int(input("Número da conta: "))
                conta = next((c for c in cliente.contas if c.numero == numero_conta), None)
                if conta:
                    valor = float(input("Digite o valor a ser sacado: "))
                    sacar(cliente, conta, valor)
                else:
                    print("Conta não encontrada.")
            else:
                print("Cliente não encontrado.")
        elif opcao == "5":
            cpf = input("CPF do usuário: ")
            cliente = buscar_cliente_por_cpf(cpf)
            if cliente:
                numero_conta = int(input("Número da conta: "))
                conta = next((c for c in cliente.contas if c.numero == numero_conta), None)
                if conta:
                    exibir_extrato(conta)
                else:
                    print("Conta não encontrada.")
            else:
                print("Cliente não encontrado.")
        elif opcao == "0":
            print("Obrigado por usar o sistema bancário. Até logo!")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()

