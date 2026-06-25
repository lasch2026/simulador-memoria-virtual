# simulador-memoria-virtual
# 🖥️ Simulador de Página Virtual

Trabalho prático da disciplina **Análise e Aplicações de Sistemas Operacionais**  
Universidade do Vale do Rio dos Sinos — UNISINOS 2026/1


## Descrição

Simulação do gerenciamento de memória virtual em **Python**, utilizando **threads**, **mutex** e o paradigma **produtor-consumidor**. O sistema cria dois processos leves que geram instruções de acesso à memória, e uma MMU que realiza a tradução de endereços virtuais para físicos, com tratamento de falta de página e substituição pelo algoritmo **FIFO**.


## Arquitetura

Processo-1 (Thread) ──┐
                      ├──► Gera endereços virtuais (produtor)
Processo-2 (Thread) ──┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │         MMU          │
                   │  (Memory Management  │
                   │       Unit)          │
                   │                      │
                   │  end_virtual         │
                   │  ÷ 8 KB → página     │
                   │  % 8 KB → offset     │
                   └──────────┬───────────┘
                              │
                   ┌──────────▼───────────┐
                   │   Tabela de Páginas   │
                   │  página → frame?      │
                   └───┬──────────────┬───┘
                       │              │
                  SIM (acerto)   NÃO (page fault)
                       │              │
                       ▼         ┌────▼─────┐
               Retorna end.      │Frame livre│
                físico +         └──┬────┬──┘
                conteúdo          SIM   NÃO
                                   │     │
                                   ▼     ▼
                              Caso A:  Caso B:
                             carrega   FIFO →
                             no frame  substitui
                             livre     vítima


Memória Principal — 64 KB
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Frame 0  │ Frame 1  │ Frame 2  │ Frame 3  │ Frame 4  │ Frame 5  │ Frame 6  │ Frame 7  │
│  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
                              Total: 8 frames × 8 KB = 64 KB



## Especificações do Sistema

| Componente | Valor |
|---|---|
| Memória Principal (RAM) | **64 KB** (65.536 bytes) |
| Memória Virtual | **1 MB** (1.048.576 bytes) |
| Tamanho de Página / Frame | **8 KB** (8.192 bytes) |
| Número de Frames (RAM) | **8 frames** (Frame 0 a Frame 7) |
| Número de Páginas (virtual) | **128 páginas** (Página 0 a Página 127) |
| Processos Leves | **2 threads** simultâneas |
| Algoritmo de Substituição | **FIFO** (First-In, First-Out) |

### Como chegamos nesses números

Frames  = Memória Principal ÷ Tamanho do Frame = 64 KB ÷ 8 KB  =   8 frames
Páginas = Memória Virtual   ÷ Tamanho da Página =  1 MB ÷ 8 KB  = 128 páginas

## Fluxo da MMU — Tradução de Endereços

O algoritmo da MMU decompõe o endereço virtual em dois campos e consulta a tabela de páginas:

Endereço Virtual  =  9.182

Número da Página  =  9.182 ÷ 8.192  =  Página 1
Offset            =  9.182 % 8.192  =  990

Tabela de páginas: Página 1 → Frame 3

Endereço Físico   =  (3 × 8.192) + 990  =  25.566




## Técnicas Utilizadas

- **Threads Python** (`threading.Thread`) — dois processos leves rodando simultaneamente, cada um com seu próprio espaço de endereçamento virtual
- **Mutex** (`threading.Lock`) — protege o acesso à MMU e à memória principal, evitando condições de corrida entre as threads
- **Paradigma Produtor-Consumidor** — os processos leves produzem endereços virtuais, a MMU consome e processa cada acesso
- **Algoritmo FIFO** — política de substituição de páginas baseada na ordem de chegada: a página mais antiga é substituída primeiro


## Algoritmo de Substituição: FIFO

Quando todos os frames estão ocupados e uma nova página precisa ser carregada:


Estado da fila FIFO (ordem de chegada):
[Processo-1 / Pág 1] → [Processo-2 / Pág 1] → [Processo-2 / Pág 4] → [Processo-1 / Pág 0] → ...

Nova página requisitada → sem frames livres!
Vítima = primeiro da fila → [Processo-1 / Pág 1]  ← mais antiga, sai primeiro
Nova página entra no frame liberado → vai para o final da fila




## Como Executar

### Requisitos

- Python 3.x — [python.org/downloads](https://www.python.org/downloads)
- Nenhuma biblioteca externa necessária (usa apenas módulos da biblioteca padrão)

### Executando o simulador

bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/simulador-memoria-virtual.git

# Entre na pasta
cd simulador-memoria-virtual

# Execute o simulador
python simulador.py
`

---

## Exemplo de Saída

```
============================================================
     SIMULADOR DE MEMORIA VIRTUAL
     Sistemas Operacionais - UNISINOS 2026/1
============================================================

 Configuracoes do sistema:
   Memoria Principal : 64 KB  ->  8 frames de 8 KB cada
   Memoria Virtual   : 1024 KB  ->  128 paginas de 8 KB cada
   Algoritmo de subst: FIFO (First-In, First-Out)

 Processos criados:
   Processo-1: 20 KB -> 3 pagina(s)
   Processo-2: 35 KB -> 5 pagina(s)

============================================================
 NOVA INSTRUCAO gerada!
 Processo-1 -> Endereco Virtual: 9182
 Decompondo: Pagina No 1  |  Offset: 990
 [PAGE FAULT] FALTA DE PAGINA! Pagina 1 nao esta na memoria principal.
 [MMU] Caso A: Frame 0 livre encontrado!
 [MMU] Pagina 1 de Processo-1 carregada -> Frame 0
 Endereco Fisico (apos carregamento): 990
 Conteudo no endereco: 217 (valor do byte)

============================================================
 NOVA INSTRUCAO gerada!
 Processo-2 -> Endereco Virtual: 13205
 Decompondo: Pagina No 1  |  Offset: 5013
 [OK] ACERTO! Pagina 1 encontrada no Frame 1
 Endereco Fisico: 13205
 Conteudo no endereco: 154 (valor do byte)

============================================================
 NOVA INSTRUCAO gerada!
 Processo-1 -> Endereco Virtual: 3100
 Decompondo: Pagina No 0  |  Offset: 3100
 [PAGE FAULT] FALTA DE PAGINA! Pagina 0 nao esta na memoria principal.
 [FIFO] Sem frames livres! Iniciando substituicao de pagina...
 [FIFO] Vitima escolhida: Processo-2 / Pagina 3 (Frame 6)
 [FIFO] Pagina 0 de Processo-1 carregada -> Frame 6
 Endereco Fisico (apos carregamento): 52332
 Conteudo no endereco: 89 (valor do byte)

============================================================
 SIMULACAO CONCLUIDA!

============================================================
 ESTADO DA MEMORIA PRINCIPAL
 Frame    Status       Proprietario / Pagina
 ---------------------------------------------
 Frame 0   OCUPADO     Processo-1 / Pagina 1
 Frame 1   OCUPADO     Processo-2 / Pagina 1
 Frame 2   OCUPADO     Processo-2 / Pagina 4
 Frame 3   OCUPADO     Processo-1 / Pagina 0
 Frame 4   OCUPADO     Processo-2 / Pagina 2
 Frame 5   OCUPADO     Processo-1 / Pagina 2
 Frame 6   OCUPADO     Processo-2 / Pagina 3
 Frame 7   OCUPADO     Processo-2 / Pagina 0

 Frames livres : 0/8
 Frames usados : 8/8
============================================================

 Tabela de Paginas de Processo-1:
 Pagina     Frame      Na Memoria?
 -----------------------------------
 Pag 0        3           SIM
 Pag 1        0           SIM
 Pag 2        5           SIM

 Tabela de Paginas de Processo-2:
 Pagina     Frame      Na Memoria?
 -----------------------------------
 Pag 0        7           SIM
 Pag 1        1           SIM
 Pag 2        4           SIM
 Pag 3        6           SIM
 Pag 4        2           SIM
```

---

## Comparação com Sistema Real

O gerenciamento de memória virtual real em sistemas operacionais modernos (Linux, Windows) utiliza mecanismos semelhantes, porém com diferenças:

| Aspecto | Este Simulador | SO Real |
|---|---|---|
| Algoritmo de substituição | FIFO (simples) | LRU, Clock, NRU (mais eficientes) |
| Tabela de páginas | Array simples por processo | Multinível (4 níveis no x86-64) |
| Memória virtual | 1 MB fixo | Até 128 TB (x86-64) |
| Granularidade de página | 8 KB | 4 KB (padrão) ou 2 MB/1 GB (huge pages) |
| Swap | Não implementado | Disco usado como extensão da RAM |
| TLB | Não implementado | Cache de tradução em hardware |

A principal diferença deste simulador é a adição do **disco** como contexto de dados dos processos e a granularidade de **8 KB por página**, deixando o cenário mais próximo de sistemas com grandes blocos de dados, como bancos de dados e servidores de arquivos.

---

## Vídeo de Apresentação

Assista no YouTube *(link do vídeo)*

---

## Autora

Desenvolvido para a disciplina de **Análise e Aplicação de Sistemas Operacionais**  
UNISINOS — 2026/1
