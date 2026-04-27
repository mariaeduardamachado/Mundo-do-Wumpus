from dataclasses import dataclass, field
import random
import time
from collections import deque

TAMANHO = 6

DIRECOES = ["N", "L", "S", "O"]  # Norte, Leste, Sul, Oeste
DELTA = {
    "N": (-1, 0),
    "L": (0, 1),
    "S": (1, 0),
    "O": (0, -1),
}

NOMES_ACOES = {
    "F": "Mover_para_frente",
    "D": "Virar_a_direita",
    "P": "Pegar_objeto",
    "T": "Atirar_flecha",
    "S": "Subir",
}


def posicao_texto(pos):
    """Converte posição interna 0..5 para posição exibida 1..6."""
    return f"[{pos[0] + 1},{pos[1] + 1}]"


@dataclass
class Agente:
    pos: tuple = (0, 0)       # [1,1] na visualização
    direcao: int = 1          # começa olhando para Leste
    pontuacao: int = 0
    vivo: bool = True
    saiu: bool = False
    ouro: int = 0
    flechas: int = 2          # como existem 2 Wumpus, usei 2 flechas
    visitadas: set = field(default_factory=lambda: {(0, 0)})
    ultimo_impacto: bool = False
    ouviu_grito: bool = False
    causa_morte: str = ""


class MundoWumpus:
    def __init__(self, tamanho=TAMANHO, seed=None):
        self.tamanho = tamanho
        self.random = random.Random(seed)

        self.wumpus = set()
        self.pocos = set()
        self.ouros = set()
        self.morcegos = set()

        self._sortear_elementos()

    def _sortear_elementos(self):
        celulas = [
            (linha, coluna)
            for linha in range(self.tamanho)
            for coluna in range(self.tamanho)
            if (linha, coluna) != (0, 0)
        ]

        sorteadas = self.random.sample(celulas, 11)

        self.wumpus = set(sorteadas[0:2])
        self.pocos = set(sorteadas[2:6])
        self.ouros = set(sorteadas[6:9])
        self.morcegos = set(sorteadas[9:11])

    def dentro_do_mapa(self, pos):
        return 0 <= pos[0] < self.tamanho and 0 <= pos[1] < self.tamanho

    def adjacentes(self, pos):
        resultado = []
        for dl, dc in DELTA.values():
            nova = (pos[0] + dl, pos[1] + dc)
            if self.dentro_do_mapa(nova):
                resultado.append(nova)
        return resultado

    def perceber(self, agente):
        percepcoes = []

        if any(casa in self.wumpus for casa in self.adjacentes(agente.pos)):
            percepcoes.append("Fedor do Wumpus")

        if any(casa in self.pocos for casa in self.adjacentes(agente.pos)):
            percepcoes.append("Brisa")

        if any(casa in self.morcegos for casa in self.adjacentes(agente.pos)):
            percepcoes.append("Barulho de morcego")

        if agente.pos in self.ouros:
            percepcoes.append("Brilho do ouro")

        if agente.ultimo_impacto:
            percepcoes.append("Impacto na parede")

        if agente.ouviu_grito:
            percepcoes.append("Grito do Wumpus morto")

        if not percepcoes:
            percepcoes.append("Nenhuma percepção")

        return percepcoes

    def executar_acao(self, agente, acao):
        agente.ultimo_impacto = False
        agente.ouviu_grito = False

        if acao == "F":
            self.mover_para_frente(agente)
        elif acao == "D":
            self.virar_a_direita(agente)
        elif acao == "P":
            self.pegar_objeto(agente)
        elif acao == "T":
            self.atirar_flecha(agente)
        elif acao == "S":
            self.subir(agente)
        else:
            print("Ação inválida.")

    def mover_para_frente(self, agente):
        agente.pontuacao -= 1

        direcao = DIRECOES[agente.direcao]
        dl, dc = DELTA[direcao]
        nova_pos = (agente.pos[0] + dl, agente.pos[1] + dc)

        if not self.dentro_do_mapa(nova_pos):
            agente.ultimo_impacto = True
            print("O agente bateu em uma parede.")
            return

        agente.pos = nova_pos
        agente.visitadas.add(agente.pos)
        self._resolver_sala_atual(agente)

    def virar_a_direita(self, agente):
        agente.pontuacao -= 1
        agente.direcao = (agente.direcao + 1) % 4

    def pegar_objeto(self, agente):
        agente.pontuacao -= 1

        if agente.pos in self.ouros:
            self.ouros.remove(agente.pos)
            agente.ouro += 1
            agente.pontuacao += 1000
            print("O agente pegou uma pedra de ouro!")
        else:
            print("Não existe ouro nesta sala.")

    def atirar_flecha(self, agente):
        agente.pontuacao -= 1

        if agente.flechas <= 0:
            print("O agente não possui mais flechas.")
            return

        agente.flechas -= 1
        agente.pontuacao -= 10

        direcao = DIRECOES[agente.direcao]
        dl, dc = DELTA[direcao]

        linha, coluna = agente.pos

        while True:
            linha += dl
            coluna += dc
            pos = (linha, coluna)

            if not self.dentro_do_mapa(pos):
                print("A flecha bateu na parede e não acertou nada.")
                return

            if pos in self.wumpus:
                self.wumpus.remove(pos)
                agente.ouviu_grito = True
                print("A flecha acertou e matou um Wumpus!")
                return

    def subir(self, agente):
        agente.pontuacao -= 1

        if agente.pos == (0, 0):
            agente.saiu = True
            print("O agente saiu da caverna.")
        else:
            print("O agente só pode subir/sair na posição [1,1].")

    def _resolver_sala_atual(self, agente):
        # Continua resolvendo porque um morcego pode levar o agente para outro morcego,
        # para um poço ou para uma sala com Wumpus.
        while agente.vivo:
            if agente.pos in self.pocos:
                agente.pontuacao -= 1000
                agente.vivo = False
                agente.causa_morte = "caiu em um poço"
                print("O agente caiu em um poço!")
                return

            if agente.pos in self.wumpus:
                agente.pontuacao -= 1000
                agente.vivo = False
                agente.causa_morte = "foi devorado pelo Wumpus"
                print("O agente foi devorado pelo Wumpus!")
                return

            if agente.pos in self.morcegos:
                print("Um morcego gigante carregou o agente para outra sala!")
                nova_pos = (
                    self.random.randrange(self.tamanho),
                    self.random.randrange(self.tamanho)
                )
                agente.pos = nova_pos
                agente.visitadas.add(agente.pos)
                print(f"O agente foi levado para {posicao_texto(agente.pos)}.")
                continue

            return

    def mostrar_labirinto_do_agente(self, agente):
        print("\nMapa conhecido pelo agente:")
        print("    " + " ".join(f"{c+1:^3}" for c in range(self.tamanho)))

        for linha in range(self.tamanho):
            texto_linha = f"{linha+1:^3} "
            for coluna in range(self.tamanho):
                pos = (linha, coluna)

                if pos == agente.pos:
                    conteudo = "A"
                elif pos == (0, 0):
                    conteudo = "E"
                elif pos in agente.visitadas:
                    conteudo = "*"
                else:
                    conteudo = "?"

                texto_linha += f"[{conteudo}]"
            print(texto_linha)

        print("Legenda: A = agente | E = entrada/saída | * = visitado | ? = desconhecido")

    def revelar_mapa_completo(self, agente):
        print("\nMapa completo revelado no fim do jogo:")
        print("    " + " ".join(f"{c+1:^3}" for c in range(self.tamanho)))

        for linha in range(self.tamanho):
            texto_linha = f"{linha+1:^3} "
            for coluna in range(self.tamanho):
                pos = (linha, coluna)

                if pos == agente.pos:
                    conteudo = "A"
                elif pos == (0, 0):
                    conteudo = "E"
                elif pos in self.wumpus:
                    conteudo = "W"
                elif pos in self.pocos:
                    conteudo = "P"
                elif pos in self.ouros:
                    conteudo = "O"
                elif pos in self.morcegos:
                    conteudo = "M"
                else:
                    conteudo = "."

                texto_linha += f"[{conteudo}]"
            print(texto_linha)

        print("Legenda: W = Wumpus vivo | P = poço | O = ouro | M = morcego | . = sala vazia")


class AgenteLogicoSimples:
    """
    Agente automático simples.

    Ele não consulta o mapa real. Usa apenas:
    - posição atual;
    - direção atual;
    - percepções recebidas;
    - salas já visitadas/conhecidas como seguras.

    Regras básicas:
    1. Se perceber brilho, pega o ouro.
    2. Se estiver em [1,1] com ouro, sai.
    3. Se não houver brisa, fedor nem morcego próximo, marca adjacentes como seguras.
    4. Tenta visitar salas seguras ainda não visitadas.
    5. Se não houver caminho seguro, tenta voltar para [1,1] e sair.
    6. Se sentir fedor e ainda tiver flecha, atira.
    """

    def __init__(self, tamanho=TAMANHO):
        self.tamanho = tamanho
        self.seguras = {(0, 0)}
        self.visitadas = set()

    def adjacentes(self, pos):
        resultado = []
        for dl, dc in DELTA.values():
            nova = (pos[0] + dl, pos[1] + dc)
            if 0 <= nova[0] < self.tamanho and 0 <= nova[1] < self.tamanho:
                resultado.append(nova)
        return resultado

    def decidir(self, agente, percepcoes):
        self.visitadas.add(agente.pos)
        self.seguras.add(agente.pos)

        perigos_percebidos = {
            "Brisa",
            "Fedor do Wumpus",
            "Barulho de morcego",
        }

        if "Brilho do ouro" in percepcoes:
            return "P"

        if agente.pos == (0, 0) and agente.ouro > 0:
            return "S"

        if not any(p in percepcoes for p in perigos_percebidos):
            for casa in self.adjacentes(agente.pos):
                self.seguras.add(casa)

        destino = self._proxima_sala_segura_nao_visitada(agente.pos)
        if destino is None and agente.pos != (0, 0):
            destino = self._proximo_passo_para(agente.pos, (0, 0))

        if destino is not None:
            return self._acao_para_ir_ate(agente, destino)

        if "Fedor do Wumpus" in percepcoes and agente.flechas > 0:
            return "T"

        if agente.pos == (0, 0):
            return "S"

        return "D"

    def _proxima_sala_segura_nao_visitada(self, origem):
        fila = deque([origem])
        veio_de = {origem: None}

        while fila:
            atual = fila.popleft()

            if atual in self.seguras and atual not in self.visitadas:
                return self._primeiro_passo(origem, atual, veio_de)

            for vizinha in self.adjacentes(atual):
                if vizinha in self.seguras and vizinha not in veio_de:
                    veio_de[vizinha] = atual
                    fila.append(vizinha)

        return None

    def _proximo_passo_para(self, origem, destino):
        fila = deque([origem])
        veio_de = {origem: None}

        while fila:
            atual = fila.popleft()

            if atual == destino:
                return self._primeiro_passo(origem, destino, veio_de)

            for vizinha in self.adjacentes(atual):
                if vizinha in self.seguras and vizinha not in veio_de:
                    veio_de[vizinha] = atual
                    fila.append(vizinha)

        return None

    def _primeiro_passo(self, origem, destino, veio_de):
        if origem == destino:
            return origem

        atual = destino
        while veio_de[atual] != origem:
            atual = veio_de[atual]

        return atual

    def _acao_para_ir_ate(self, agente, destino):
        linha_atual, coluna_atual = agente.pos
        linha_destino, coluna_destino = destino

        if linha_destino < linha_atual:
            direcao_desejada = "N"
        elif linha_destino > linha_atual:
            direcao_desejada = "S"
        elif coluna_destino > coluna_atual:
            direcao_desejada = "L"
        else:
            direcao_desejada = "O"

        direcao_atual = DIRECOES[agente.direcao]

        if direcao_atual == direcao_desejada:
            return "F"

        return "D"


def mostrar_status(mundo, agente):
    mundo.mostrar_labirinto_do_agente(agente)

    percepcoes = mundo.perceber(agente)

    print("\nStatus:")
    print(f"Posição: {posicao_texto(agente.pos)}")
    print(f"Direção: {DIRECOES[agente.direcao]}")
    print(f"Pontuação: {agente.pontuacao}")
    print(f"Ouro coletado: {agente.ouro}")
    print(f"Flechas: {agente.flechas}")
    print("Percepções:", ", ".join(percepcoes))

    return percepcoes


def ler_acao_manual():
    print("\nAções:")
    print("F - Mover_para_frente")
    print("D - Virar_a_direita")
    print("P - Pegar_objeto")
    print("T - Atirar_flecha")
    print("S - Subir")

    while True:
        acao = input("Escolha a ação: ").strip().upper()
        if acao in NOMES_ACOES:
            return acao
        print("Ação inválida. Digite F, D, P, T ou S.")


def jogar(modo="manual", seed=None, atraso=0.8, max_passos=200):
    mundo = MundoWumpus(seed=seed)
    agente = Agente()
    cerebro = AgenteLogicoSimples()

    print("=" * 60)
    print("MUNDO DO WUMPUS - MATRIZ 6 x 6")
    print("=" * 60)
    print("O agente inicia em [1,1], que também é a saída.")
    print("O mapa completo fica oculto durante o jogo.")

    passos = 0

    while agente.vivo and not agente.saiu and passos < max_passos:
        passos += 1
        percepcoes = mostrar_status(mundo, agente)

        if modo == "automatico":
            acao = cerebro.decidir(agente, percepcoes)
            print(f"\nAção escolhida pelo agente: {NOMES_ACOES[acao]}")
            time.sleep(atraso)
        else:
            acao = ler_acao_manual()

        mundo.executar_acao(agente, acao)

        print("-" * 60)

    print("\nFIM DO JOGO")
    print("=" * 60)

    if agente.saiu:
        print("Resultado: o agente saiu vivo da caverna.")
    elif not agente.vivo:
        print(f"Resultado: o agente morreu porque {agente.causa_morte}.")
    else:
        print("Resultado: limite de passos atingido.")

    print(f"Pontuação final: {agente.pontuacao}")
    print(f"Ouro coletado: {agente.ouro}")
    print(f"Passos executados: {passos}")

    mundo.revelar_mapa_completo(agente)


if __name__ == "__main__":
    print("Escolha o modo de jogo:")
    print("1 - Manual")
    print("2 - Automático simples")

    escolha = input("Modo: ").strip()

    if escolha == "2":
        jogar(modo="automatico")
    else:
        jogar(modo="manual")
