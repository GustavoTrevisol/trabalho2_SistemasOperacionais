###
###     S I M U L A D O R    D E    M E M Ó R I A
###
### Prof. Filipo - github.com/ProfessorFilipo/MemSim/
###

import sys
from collections import deque


class Frame:
    def __init__(self, id_frame):
        self.id_frame = id_frame
        self.pagina_alocada = None  # Armazena o número da página ou None se estiver vazio
        # Dica para os alunos: vocês podem adicionar atributos aqui para ajudar no algoritmo (ex: timestamp, contador)
        self.bit_referencia = 0

class TabelaPaginas:
    def __init__(self, num_frames, algoritmo):
        # Inicializa a memória física com a quantidade de frames especificada
        self.frames = [Frame(i) for i in range(num_frames)]
        self.total_page_faults = 0
        self.total_acessos = 0
        self.algoritmo = algoritmo

        # Estado interno do Segunda Chance (Clock)
        self.ponteiro = 0

        # Estado interno do FIFO: fila com a ordem de chegada das páginas
        self.fila_fifo = deque()

    def acessar_pagina(self, numero_pagina):
        self.total_acessos += 1

        # 1. Verificar se a página já está em algum frame (Hit)
        for frame in self.frames:
            if frame.pagina_alocada == numero_pagina:
                frame.bit_referencia = 1
                return True, frame.id_frame  # Retorna (Hit=True, frame_id)

        # 2. Se não encontrou, ocorreu um Page Fault!
        self.total_page_faults += 1

        # 3. Verificar se existe algum frame vazio disponível
        for frame in self.frames:
            if frame.pagina_alocada is None:
                frame.pagina_alocada = numero_pagina
                frame.bit_referencia = 1
                self.fila_fifo.append(numero_pagina)
                return False, frame.id_frame  # Retorna (Hit=False, frame_id)

        # 4. Memória cheia: Aplicar algoritmo de substituição de página
        frame_vitima_id = self.substituir_pagina(numero_pagina)
        return False, frame_vitima_id

    def substituir_pagina(self, nova_pagina):
        if self.algoritmo == "FIFO":
            return self._substituir_fifo(nova_pagina)
        else:
            return self._substituir_segunda_chance(nova_pagina)

    def _substituir_fifo(self, nova_pagina):
        # Remove a página mais antiga da fila e encontra seu frame
        pagina_vitima = self.fila_fifo.popleft()
        for frame in self.frames:
            if frame.pagina_alocada == pagina_vitima:
                frame.pagina_alocada = nova_pagina
                frame.bit_referencia = 1
                self.fila_fifo.append(nova_pagina)
                return frame.id_frame

    def _substituir_segunda_chance(self, nova_pagina):
        # Percorre os frames em ordem circular até encontrar um com bit = 0
        while True:
            frame_atual = self.frames[self.ponteiro]
            if frame_atual.bit_referencia == 1:
                frame_atual.bit_referencia = 0
                self.ponteiro = (self.ponteiro + 1) % len(self.frames)
            else:
                frame_atual.pagina_alocada = nova_pagina
                frame_atual.bit_referencia = 1
                frame_escolhido_id = frame_atual.id_frame
                self.ponteiro = (self.ponteiro + 1) % len(self.frames)
                return frame_escolhido_id

    def imprimir_mapa_memoria(self, passo, pagina_acessada, foi_hit, frame_alterado=None):
        status = "Hit" if foi_hit else "Page Fault"
        print(f"\n--- Passo {passo}: Acesso à Página {pagina_acessada} ({status}) ---")

        for frame in self.frames:
            conteudo = f"Página {frame.pagina_alocada}" if frame.pagina_alocada is not None else "[Vazio]"
            marcador = " <-- Alterado" if frame.id_frame == frame_alterado and not foi_hit else ""
            print(f"[Frame {frame.id_frame}]: {conteudo}{marcador}")

        print("-" * 40)


class Simulador:
    def __init__(self, caminho_arquivo, algoritmo):
        self.caminho_arquivo = caminho_arquivo
        self.algoritmo = algoritmo

    def executar(self):
        try:
            with open(self.caminho_arquivo, 'r') as arquivo:
                linhas = arquivo.readlines()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.caminho_arquivo}' não foi encontrado.")
            return

        # Limpa linhas vazias ou comentários se houver
        linhas = [l.strip() for l in linhas if l.strip() and not l.strip().startswith('#')]

        if not linhas:
            print("Erro: Arquivo de entrada vazio.")
            return

        # A primeira linha válida define o número de frames na memória RAM simulada
        num_frames = int(linhas[0])
        tabela_paginas = TabelaPaginas(num_frames, self.algoritmo)

        print(f"Iniciando simulação com {num_frames} frames disponíveis. Algoritmo: {self.algoritmo}")
        print("=" * 40)

        # As linhas seguintes são a sequência de acessos às páginas
        passo = 1
        for linha in linhas[1:]:
            numero_pagina = int(linha)

            # Processa o acesso na tabela de páginas
            foi_hit, frame_id = tabela_paginas.acessar_pagina(numero_pagina)

            # Renderiza o mapa de memória para o aluno ver o passo a passo
            tabela_paginas.imprimir_mapa_memoria(passo, numero_pagina, foi_hit, frame_id)
            passo += 1

        # Exibição das estatísticas finais da simulação
        print("\n================ STATS FINAIS ================")
        print(f"Total de Acessos: {tabela_paginas.total_acessos}")
        print(f"Total de Page Faults: {tabela_paginas.total_page_faults}")
        if tabela_paginas.total_acessos > 0:
            taxa_faults = (tabela_paginas.total_page_faults / tabela_paginas.total_acessos) * 100
            print(f"Taxa de Page Faults: {taxa_faults:.2f}%")
        print("==============================================")


if __name__ == "__main__":
    # Uso: python simulador_memoria.py <arquivo> <FIFO|SC>
    arquivo_entrada = sys.argv[1] if len(sys.argv) > 1 else "entrada.txt"
    algoritmo = sys.argv[2].upper() if len(sys.argv) > 2 else "SC"

    if algoritmo not in ("FIFO", "SC"):
        print(f"Erro: algoritmo '{algoritmo}' inválido. Use FIFO ou SC.")
        sys.exit(1)

    simulador = Simulador(arquivo_entrada, algoritmo)
    simulador.executar()
    