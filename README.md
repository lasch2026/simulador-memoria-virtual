# 🖥️ Simulador de Página Virtual

Trabalho prático da disciplina **Análise e Aplicações de Sistemas Operacionais**  
Universidade do Vale do Rio dos Sinos — UNISINOS 2026/1

---

## Descrição

Simulação do gerenciamento de memória virtual em **Python**, utilizando **threads**, **mutex** e o paradigma **produtor-consumidor**. O sistema cria dois processos leves que geram instruções de acesso à memória, e uma MMU que realiza a tradução de endereços virtuais para físicos, com tratamento de falta de página e substituição pelo algoritmo **FIFO**.

---

## Arquitetura

```
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
```

```
Memória Principal — 64 KB
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Frame 0  │ Frame 1  │ Frame 2  │ Frame 3  │ Frame 4  │ Frame 5  │ Frame 6  │ Frame 7  │
│  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │  8 KB    │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
                              Total: 8 frames × 8 KB = 64 KB
```

---

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

```
Frames  = Memória Principal ÷ Tamanho do Frame = 64 KB ÷ 8 KB  =   8 frames
Páginas = Memória Virtual   ÷ Tamanho da Página =  1 MB ÷ 8 KB  = 128 páginas
```

---

## Fluxo da MMU — Tradução de Endereços

O algoritmo da MMU decompõe o endereço virtual em dois campos e consulta a tabela de páginas:

```
Endereço Virtual  =  9.182

Número da Página  =  9.182 ÷ 8.192  =  Página 1
Offset            =  9.182 % 8.192  =  990

Tabela de páginas: Página 1 → Frame 3

Endereço Físico   =  (3 × 8.192) + 990  =  25.566
```

---

## Técnicas Utilizadas

- **Threads Python** (`threading.Thread`) — dois processos leves rodando simultaneamente, cada um com seu próprio espaço de endereçamento virtual
- **Mutex** (`threading.Lock`) — protege o acesso à MMU e à memória principal, evitando condições de corrida entre as threads
- **Paradigma Produtor-Consumidor** — os processos leves produzem endereços virtuais, a MMU consome e processa cada acesso
- **Algoritmo FIFO** — política de substituição de páginas baseada na ordem de chegada: a página mais antiga é substituída primeiro

---

## Algoritmo de Substituição: FIFO

Quando todos os frames estão ocupados e uma nova página precisa ser carregada:

```
Estado da fila FIFO (ordem de chegada):
[Processo-1 / Pág 1] → [Processo-2 / Pág 1] → [Processo-2 / Pág 4] → [Processo-1 / Pág 0] → ...

Nova página requisitada → sem frames livres!
Vítima = primeiro da fila → [Processo-1 / Pág 1]  ← mais antiga, sai primeiro
Nova página entra no frame liberado → vai para o final da fila
```

---

## Como Executar

### Requisitos

- Python 3.x — [python.org/downloads](https://www.python.org/downloads)
- Nenhuma biblioteca externa necessária (usa apenas módulos da biblioteca padrão)

### Executando o simulador

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/simulador-memoria-virtual.git

# Entre na pasta
cd simulador-memoria-virtual

# Execute o simulador
python simulador.py
```

---

## Exemplo de Saída

```
     SIMULADOR DE MEMORIA VIRTUAL

 Configuracoes do sistema:
   Memoria Principal : 64 KB  ->  8 frames de 8 KB cada
   Memoria Virtual   : 1024 KB  ->  128 paginas de 8 KB cada
   Algoritmo de subst: FIFO (First-In, First-Out)

 Processos criados:
   Processo-1: 50 KB -> 7 pagina(s)
   Processo-2: 50 KB -> 7 pagina(s)

============================================================
 NOVA INSTRUCAO!
 Processo-1 -> Endereco Virtual: 6526
 Decompondo: Pagina No 0  |  Offset: 6526
 [PAGE FAULT] FALTA DE PAGINA! Pagina 0 nao esta na memoria principal.
 [MMU] Caso A: Temos um Frame 0 livre!
 [MMU] Pagina 0 de Processo-1 carregada -> Frame 0
 [MMU] Tabela de paginas de Processo-1 atualizada.
 Endereco Fisico (depois do carregamento): 6526
 Conteudo no endereco: 146 (valor do byte)

============================================================
 NOVA INSTRUCAO!
 Processo-2 -> Endereco Virtual: 46318
 Decompondo: Pagina No 5  |  Offset: 5358
 [PAGE FAULT] FALTA DE PAGINA! Pagina 5 nao esta na memoria principal.
 [FIFO] Sem frames livres! Iniciando substituicao de pagina...
 [FIFO] Vitima escolhida: Processo-1 / Pagina 3 (Frame 0)
 [FIFO] Pagina 5 de Processo-2 carregada -> Frame 0
 [MMU] Tabela de paginas de Processo-2 atualizada.
 [MMU] Tabela de paginas de Processo-1 invalidada (Pagina 3).
 Endereco Fisico (depois do carregamento): 5358
 Conteudo no endereco: 111 (valor do byte)

============================================================
 NOVA INSTRUCAO!
 Processo-1 -> Endereco Virtual: 7419
 Decompondo: Pagina No 0  |  Offset: 7419
 OK! Pagina 0 encontrada no Frame 5
 Endereco Fisico: 48379
 Conteudo no endereco: 249 (valor do byte)

============================================================
 SIMULACAO CONCLUIDA COM SUCESSO!
 ESTADO DA MEMORIA PRINCIPAL
 Frame    Status       Proprietario / Pagina
 Frame 0   OCUPADO     Processo-2 / Pagina 5
 Frame 1   OCUPADO     Processo-1 / Pagina 3
 Frame 2   OCUPADO     Processo-2 / Pagina 3
 Frame 3   OCUPADO     Processo-2 / Pagina 4
 Frame 4   OCUPADO     Processo-2 / Pagina 1
 Frame 5   OCUPADO     Processo-2 / Pagina 2
 Frame 6   OCUPADO     Processo-1 / Pagina 1
 Frame 7   OCUPADO     Processo-1 / Pagina 2

 Frames livres : 0/8
 Frames usados : 8/8

 Tabela de Paginas de Processo-1:
 Pagina     Frame      Na Memoria?
 Pag 0        -           NAO
 Pag 1        6           SIM
 Pag 2        7           SIM
 Pag 3        1           SIM
 Pag 4        -           NAO
 Pag 5        -           NAO
 Pag 6        -           NAO

 Tabela de Paginas de Processo-2:
 Pagina     Frame      Na Memoria?
 Pag 0        -           NAO
 Pag 1        4           SIM
 Pag 2        5           SIM
 Pag 3        2           SIM
 Pag 4        3           SIM
 Pag 5        0           SIM
 Pag 6        -           NAO
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

A principal diferença deste simulador em relação a um SO real está na **simplicidade intencional**: o algoritmo FIFO é menos eficiente que o LRU, mas evidencia com clareza o mecanismo de substituição de páginas, tornando o comportamento do sistema fácil de acompanhar e verificar.

---

## Vídeo

Assista no YouTube _link_

---

Este projeto foi desenvolvido para a disciplina de **Análise e Aplicação de Sistemas Operacionais**  
UNISINOS — 2026/1
