from datetime import datetime
from collections import deque
import copy

class Registro:
    def __init__(self, cpf: str, nome: str, data_nascimento: str, deletado=False):
        self.cpf = cpf  # chave de ordenação
        self.nome = nome
        self.data_nascimento = datetime.strptime(data_nascimento, "%d/%m/%Y")
        self.deletado = deletado  # flag para marcar registro deletado

    def __lt__(self, outro):
        # Comparação baseada no CPF
        return self.cpf < outro.cpf

    def __eq__(self, outro):
        return self.cpf == outro.cpf

    def __str__(self):
        status = "DELETADO" if self.deletado else "ATIVO"
        return f"CPF: {self.cpf}, Nome: {self.nome}, Nasc: {self.data_nascimento.strftime('%d/%m/%Y')} - {status}"

    def zerar(self):
        # Marca o registro como deletado e limpa os dados
        self.cpf = ""
        self.nome = ""
        self.data_nascimento = None
        self.deletado = True

class No:
    def __init__(self, registro: Registro, posicao: int):
        self.registro = registro
        self.posicao = posicao  # posição do registro na EDL
        self.esquerda = None
        self.direita = None

class ArvoreBinariaBusca:
    def __init__(self, registros_iter=None):
        self.raiz = None
        if registros_iter:
            for reg, pos in registros_iter:
                self.inserir(reg, pos)

    def copiar_no(self, no):
        if no is None:
            return None
        novo_no = No(copy.deepcopy(no.registro), no.posicao)
        novo_no.esquerda = self.copiar_no(no.esquerda)
        novo_no.direita = self.copiar_no(no.direita)
        return novo_no

    def __deepcopy__(self, memo):
        nova_abb = ArvoreBinariaBusca()
        nova_abb.raiz = self.copiar_no(self.raiz)
        return nova_abb

    def inserir(self, registro: Registro, posicao: int):
        if self.raiz is None:
            self.raiz = No(registro, posicao)
        else:
            self._inserir(self.raiz, registro, posicao)

    def _inserir(self, no_atual: No, registro: Registro, posicao: int):
        if registro < no_atual.registro:
            if no_atual.esquerda is None:
                no_atual.esquerda = No(registro, posicao)
            else:
                self._inserir(no_atual.esquerda, registro, posicao)
        elif registro > no_atual.registro:
            if no_atual.direita is None:
                no_atual.direita = No(registro, posicao)
            else:
                self._inserir(no_atual.direita, registro, posicao)
        else:
            print(f"Chave {registro.cpf} já existe na ABB. Ignorando inserção.")

    def buscar(self, chave: str):
        return self._buscar(self.raiz, chave)

    def _buscar(self, no_atual: No, chave: str):
        if no_atual is None:
            return None
        if chave == no_atual.registro.cpf:
            return no_atual
        elif chave < no_atual.registro.cpf:
            return self._buscar(no_atual.esquerda, chave)
        else:
            return self._buscar(no_atual.direita, chave)

    def _minimo(self, no):
        while no.esquerda is not None:
            no = no.esquerda
        return no

    def remover(self, chave: str):
        self.raiz = self._remover(self.raiz, chave)

    def _remover(self, no, chave):
        if no is None:
            return None
        if chave < no.registro.cpf:
            no.esquerda = self._remover(no.esquerda, chave)
        elif chave > no.registro.cpf:
            no.direita = self._remover(no.direita, chave)
        else:
            # Nó encontrado
            if no.esquerda is None:
                return no.direita
            elif no.direita is None:
                return no.esquerda
            else:
                # Nó com dois filhos: buscar sucessor
                sucessor = self._minimo(no.direita)
                no.registro = sucessor.registro
                no.posicao = sucessor.posicao
                no.direita = self._remover(no.direita, sucessor.registro.cpf)
        return no

    def destruir(self):
        self.raiz = None  # Em Python, garbage collector cuida da memória

    # Percursos
    def pre_ordem(self):
        resultado = []
        self._pre_ordem(self.raiz, resultado)
        return resultado

    def _pre_ordem(self, no, resultado):
        if no:
            resultado.append(no.registro)
            self._pre_ordem(no.esquerda, resultado)
            self._pre_ordem(no.direita, resultado)

    def em_ordem(self):
        resultado = []
        self._em_ordem(self.raiz, resultado)
        return resultado

    def _em_ordem(self, no, resultado):
        if no:
            self._em_ordem(no.esquerda, resultado)
            resultado.append(no.registro)
            self._em_ordem(no.direita, resultado)

    def pos_ordem(self):
        resultado = []
        self._pos_ordem(self.raiz, resultado)
        return resultado

    def _pos_ordem(self, no, resultado):
        if no:
            self._pos_ordem(no.esquerda, resultado)
            self._pos_ordem(no.direita, resultado)
            resultado.append(no.registro)

    def percurso_largura(self):
        resultado = []
        if self.raiz is None:
            return resultado
        fila = deque()
        fila.append(self.raiz)
        while fila:
            no = fila.popleft()
            resultado.append(no.registro)
            if no.esquerda:
                fila.append(no.esquerda)
            if no.direita:
                fila.append(no.direita)
        return resultado

# Classe para o arquivo de registros (EDL linear)
class ArquivoRegistros:
    def __init__(self):
        self.registros = []

    def inserir(self, registro: Registro):
        self.registros.append(registro)
        return len(self.registros) - 1  # retorna a posição do registro inserido

    def buscar_por_posicao(self, posicao: int):
        if 0 <= posicao < len(self.registros):
            return self.registros[posicao]
        return None

    def deletar(self, posicao: int):
        if 0 <= posicao < len(self.registros):
            self.registros[posicao].zerar()

    def __len__(self):
        return len(self.registros)

    def __str__(self):
        return "\n".join(f"{i}: {str(reg)}" for i, reg in enumerate(self.registros))

# Sistema gerenciador usando ABB como índice e arquivo de registros
class SistemaGerenciadorBD:
    def __init__(self):
        self.arquivo = ArquivoRegistros()
        self.indice = ArvoreBinariaBusca()

    def inserir_registro(self, registro: Registro):
        posicao = self.arquivo.inserir(registro)
        self.indice.inserir(registro, posicao)

    def remover_registro_por_cpf(self, cpf: str):
        no = self.indice.buscar(cpf)
        if no:
            self.arquivo.deletar(no.posicao)
            self.indice.remover(cpf)
            print(f"Registro com CPF {cpf} removido.")
        else:
            print(f"Registro com CPF {cpf} não encontrado.")

    def buscar_registro_por_cpf(self, cpf: str):
        no = self.indice.buscar(cpf)
        if no:
            registro = self.arquivo.buscar_por_posicao(no.posicao)
            if registro and not registro.deletado:
                return registro
            else:
                return None
        else:
            return None

    def criar_arquivo_ordenado(self):
        registros_ordenados = []
        def em_ordem_nos(no):
            if no:
                em_ordem_nos(no.esquerda)
                registros_ordenados.append(self.arquivo.buscar_por_posicao(no.posicao))
                em_ordem_nos(no.direita)
        em_ordem_nos(self.indice.raiz)
        return registros_ordenados

# Exemplo de uso
if __name__ == "__main__":
    sgbd = SistemaGerenciadorBD()

    # Inserir registros
    sgbd.inserir_registro(Registro("12345678901", "Maria Silva", "15/03/1985"))
    sgbd.inserir_registro(Registro("98765432100", "João Souza", "22/07/1990"))
    sgbd.inserir_registro(Registro("11122233344", "Ana Paula", "05/01/1975"))
    sgbd.inserir_registro(Registro("55566677788", "Carlos Lima", "10/10/1980"))

    # Buscar registro
    cpf_busca = "98765432100"
    print(f"\nBuscando registro com CPF {cpf_busca}:")
    resultado = sgbd.buscar_registro_por_cpf(cpf_busca)
    if resultado:
        print(resultado)
    else:
        print("Registro não encontrado.")

    # Remover registro
    cpf_remover = "11122233344"
    print(f"\nRemovendo registro com CPF {cpf_remover}:")
    sgbd.remover_registro_por_cpf(cpf_remover)

    # Tentar buscar registro removido
    print(f"\nBuscando registro com CPF {cpf_remover} após remoção:")
    resultado = sgbd.buscar_registro_por_cpf(cpf_remover)
    if resultado:
        print(resultado)
    else:
        print("Registro não encontrado.")

    # Mostrar arquivo linear (EDL)
    print("\nArquivo de registros (EDL):")
    print(sgbd.arquivo)

    # Mostrar percurso em ordem da ABB (índice)
    print("\nPercurso em ordem da ABB (chaves):")
    for reg in sgbd.indice.em_ordem():
        print(reg)

    # Criar arquivo ordenado
    print("\nArquivo de registros ordenado pela chave (CPF):")
    arquivo_ordenado = sgbd.criar_arquivo_ordenado()
    for reg in arquivo_ordenado:
        print(reg)
