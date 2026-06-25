import threading
import random
import time
from collections import deque

#Configurações do sistema
TAM_MEM_PRINCIPAL = 64 * 1024         #64 KB = 65.536 bytes
TAM_MEM_VIRTUAL = 1 * 1024 * 1024     #1 MB = 1.048.576 bytes
TAM_PAGINA = 8 * 1024                 #8 KB = 8.192 bytes

NUM_FRAMES = TAM_MEM_PRINCIPAL // TAM_PAGINA    #64 KB/8 KB = 8 frames
NUM_PAGINAS = TAM_MEM_VIRTUAL // TAM_PAGINA     #1 MB/8 KB = 128 paginas

#Lista com 8 frames. Cada frame guarda TAM_PAGINA bytes, ou None se estiver livre.
memoria_principal = [None] * NUM_FRAMES   #8 posições (frames)
frames_livres = list(range(NUM_FRAMES))   #[0, 1, 2, 3, 4, 5, 6, 7]

#FIFO -> A fila guarda tuplas (processo, num_pagina, num_frame) na ordem em que as paginas foram carregadas.
fila_fifo = deque()

#Locks(travas) para garantir acesso exclusivo
mmu_lock = threading.Lock()    #mmu_lock -> evita que duas threads usem a MMU ao mesmo tempo
print_lock = threading.Lock()  #print_lock -> evita que as saidas das threads se misturem


#ProcessoLeve(representa cada thread/processo leve)
class ProcessoLeve:
    """
    Representa um processo leve (thread) com:
    PID: identificador unico
    Dados: conteudo do processo na memoria virtual (bytes aleatorios)
    Tabela de paginas: mapeia pagina -> frame (ou -1 se nao esta na RAM)
    """
    def __init__(self, pid, tamanho_bytes):
        self.pid = pid
        self.tamanho = tamanho_bytes

        #Simula os dados do processo no espaco virtual (bytes aleatórios representando instruções/dados)
        self.dados = bytearray(random.randint(0, 255) for _ in range(tamanho_bytes))

        #Tabela de páginas do processo:
        #Indice = número da pagina | Valor = frame (-1 = nâo esta na memória)
        num_paginas_processo = (tamanho_bytes + TAM_PAGINA - 1) // TAM_PAGINA
        self.tabela_paginas = [-1] * num_paginas_processo

    def __str__(self):
        return f"Processo-{self.pid}"


#MMU: Tradução de Endereço Virtual -> Físico
def mmu_traduzir(processo, end_virtual):
    """
    A MMU recebe um endereco virtual e:
    1. Decompose em numero de pagina + offset
    2. Consulta a tabela de paginas do processo
    3. Se a pagina esta na RAM -> retorna o endereco fisico e o conteudo
    4. Se NAO esta -> emite page fault e carrega a pagina
    """
    with mmu_lock:
        #Decomposição do endereço virtual 
        num_pagina = end_virtual // TAM_PAGINA  #Qual pagina
        offset = end_virtual %  TAM_PAGINA      #Posição dentro da pagina

        with print_lock:
            print(f"\n{'='*60}")
            print(f" NOVA INSTRUCAO!")
            print(f" {processo} -> Endereco Virtual: {end_virtual}")
            print(f" Decompondo: Pagina No {num_pagina}  |  Offset: {offset}")

        #Verifica se o endereço é valido para o processo
        if num_pagina >= len(processo.tabela_paginas):
            with print_lock:
                print(f" [ERRO] Endereco {end_virtual} esta fora do espaco do {processo}!")
            return

        #Consulta a tabela de paginas
        frame = processo.tabela_paginas[num_pagina]

        if frame != -1:
            #Ok -> pagina ja esta na memoria principal
            end_fisico = frame * TAM_PAGINA + offset
            conteudo = memoria_principal[frame][offset]
            with print_lock:
                print(f" OK! Pagina {num_pagina} encontrada no Frame {frame}")
                print(f" Endereco Fisico: {end_fisico}")
                print(f" Conteudo no endereco: {conteudo} (valor do byte)")
        else:
            #Page Fault
            with print_lock:
                print(f" [PAGE FAULT] FALTA DE PAGINA! Pagina {num_pagina} nao esta na memoria principal.")

            #Chama o carregador de paginas
            _carregar_pagina(processo, num_pagina)

            #Depois do carregamento, acessa o conteudo normalmente
            frame = processo.tabela_paginas[num_pagina]
            end_fisico = frame * TAM_PAGINA + offset
            conteudo = memoria_principal[frame][offset]
            with print_lock:
                print(f" Endereco Fisico (depois do carregamento): {end_fisico}")
                print(f" Conteudo no endereco: {conteudo} (valor do byte)")


#Carregamento da pagina -. Executa os casos A (frame livre) e B (substituicao FIFO)
def _carregar_pagina(processo, num_pagina):
    """
    Carrega a pagina do espaco virtual do processo na memoria principal.
    Caso A: temos frame disponivel -> usa o primeiro livre.
    Caso B: sem frames livres -> aplica substituicao FIFO.
    """
    #Extrai os dados desta pagina do espaco virtual do processo
    inicio = num_pagina * TAM_PAGINA
    fim = min(inicio + TAM_PAGINA, processo.tamanho)
    dados_pagina = bytearray(TAM_PAGINA)
    dados_pagina[:fim - inicio] = processo.dados[inicio:fim]

    if frames_livres:
        #Caso A: tem frame disponivel
        frame = frames_livres.pop(0)   #Pega o primeiro frame livre
        memoria_principal[frame] = dados_pagina
        processo.tabela_paginas[num_pagina] = frame
        fila_fifo.append((processo, num_pagina, frame))

        with print_lock:
            print(f" [MMU] Caso A: Temos um Frame {frame} livre!")
            print(f" [MMU] Pagina {num_pagina} de {processo} carregada -> Frame {frame}")
            print(f" [MMU] Tabela de paginas de {processo} atualizada.")

    else:
        #Caso B: sem frames livres -> substituição FIFO
        with print_lock:
            print(f" [FIFO] Sem frames livres! Iniciando substituicao de pagina...")

        #A vitima é a primeira a entrar na fila (FIFO)
        proc_vitima, pag_vitima, frame_vitima = fila_fifo.popleft()

        with print_lock:
            print(f" [FIFO] Vitima escolhida: {proc_vitima} / Pagina {pag_vitima} (Frame {frame_vitima})")

        #Invalida a entrada da vitima na tabela de paginas dela
        proc_vitima.tabela_paginas[pag_vitima] = -1

        #Carrega a nova pagina no frame liberado
        memoria_principal[frame_vitima] = dados_pagina
        processo.tabela_paginas[num_pagina] = frame_vitima
        fila_fifo.append((processo, num_pagina, frame_vitima))

        with print_lock:
            print(f" [FIFO] Pagina {num_pagina} de {processo} carregada -> Frame {frame_vitima}")
            print(f" [MMU] Tabela de paginas de {processo} atualizada.")
            print(f" [MMU] Tabela de paginas de {proc_vitima} invalidada (Pagina {pag_vitima}).")


#Estados na memória principal
def mostrar_memoria():
    """Exibindo o estado atual de todos os frames da memoria principal."""
    with print_lock:
        print(" ESTADO DA MEMORIA PRINCIPAL")
        print(f" {'Frame':<8} {'Status':<12} {'Proprietario / Pagina'}")
        for i in range(NUM_FRAMES):
            if memoria_principal[i] is None:
                print(f" Frame {i:<3}   LIVRE")
            else:
                dono = "? / ?"
                for proc, pag, frm in fila_fifo:
                    if frm == i:
                        dono = f"{proc} / Pagina {pag}"
                print(f" Frame {i:<3}   OCUPADO     {dono}")
        print(f"\n Frames livres : {len(frames_livres)}/{NUM_FRAMES}")
        print(f" Frames usados : {NUM_FRAMES - len(frames_livres)}/{NUM_FRAMES}")

def mostrar_tabela_paginas(processo):
    """Exibindo a tabela de paginas de um processo."""
    with print_lock:
        print(f"\n Tabela de Paginas de {processo}:")
        print(f" {'Pagina':<10} {'Frame':<10} {'Na Memoria?'}")
        for i, frame in enumerate(processo.tabela_paginas):
            na_mem = "SIM" if frame != -1 else "NAO"
            frame_str = str(frame) if frame != -1 else "-"
            print(f" Pag {i:<6}   {frame_str:<10}  {na_mem}")


#Processo leve
def executar_thread(processo, num_acessos):
    """
    Simula um processo leve fazendo 'num_acessos' acessos
    aleatorios a memoria virtual.
    """
    for i in range(num_acessos):
        #Gera um endereço virtual aleatório dentro do espaço do processo
        end_virtual = random.randint(0, processo.tamanho - 1)
        mmu_traduzir(processo, end_virtual)
        time.sleep(0.05)   #simula tempo de execução entre instruções


#Main
if __name__ == "__main__":

    print("     SIMULADOR DE MEMORIA VIRTUAL")
    print(f"\n Configuracoes do sistema:")
    print(f"   Memoria Principal : {TAM_MEM_PRINCIPAL // 1024} KB  ->  {NUM_FRAMES} frames de {TAM_PAGINA // 1024} KB cada")
    print(f"   Memoria Virtual   : {TAM_MEM_VIRTUAL   // 1024} KB  ->  {NUM_PAGINAS} paginas de {TAM_PAGINA // 1024} KB cada")
    print(f"   Algoritmo de subst: FIFO (First-In, First-Out)")

    #Criando os Processos Leves -> Tamanhos entre 1 byte e 1 MB (conforme enunciado)
    proc1 = ProcessoLeve(pid=1, tamanho_bytes=50 * 1024)   #Processo 1: 50 KB -> 7 paginas
    proc2 = ProcessoLeve(pid=2, tamanho_bytes=50 * 1024)   #Processo 2: 50 KB -> 7 paginas

    print(f"\n Processos criados:")
    print(f"   {proc1}: {proc1.tamanho // 1024} KB -> {len(proc1.tabela_paginas)} pagina(s)")
    print(f"   {proc2}: {proc2.tamanho // 1024} KB -> {len(proc2.tabela_paginas)} pagina(s)")

    #Exibe o estado inicial da memória
    mostrar_memoria()

    #Cria e inicia as threads (processos leves)
    print("\n Iniciando processos leves (threads)...\n")

    t1 = threading.Thread(target=executar_thread, args=(proc1, 15), name="Thread-P1")
    t2 = threading.Thread(target=executar_thread, args=(proc2, 15), name="Thread-P2")

    t1.start()
    t2.start()

    #Espera ambas as threads terminarem
    t1.join()
    t2.join()

    #Estado final
    print(" SIMULACAO CONCLUIDA COM SUCESSO!")
    mostrar_memoria()
    mostrar_tabela_paginas(proc1)
    mostrar_tabela_paginas(proc2)
