# Mundo do Wumpus

Projeto desenvolvido para a disciplina **Inteligência Computacional**, com o objetivo de implementar uma versão do jogo **Mundo do Wumpus** utilizando uma matriz 6 x 6, sensores, ações, pontuação e movimentação do agente.

## Informações do trabalho

**Curso:** Bacharelado em Engenharia da Computação  
**Disciplina:** Inteligência Computacional  
**Professora:** Dra. Jaqueline Alves Ribeiro  
**Tema:** Agentes Lógicos – Mundo do Wumpus  

## Descrição

O Mundo do Wumpus é um ambiente em formato de labirinto onde um agente deve explorar salas desconhecidas, coletar ouro e tentar sair vivo da caverna.

Durante a exploração, o agente não tem acesso ao mapa completo. Ele deve tomar decisões com base nas percepções recebidas ao entrar em cada sala, como brisa, fedor, barulho de morcego, brilho do ouro, impacto contra parede e grito do Wumpus.

O jogo termina quando o agente sai da caverna pela posição inicial `[1,1]` ou morre ao cair em um poço ou ser devorado por um Wumpus.

## Requisitos implementados

O programa implementa os seguintes requisitos:

- Labirinto representado por uma matriz **6 x 6**;
- Agente iniciando sempre na posição `[1,1]`;
- A posição `[1,1]` também representa a saída da caverna;
- Sorteio aleatório da posição inicial dos elementos do labirinto;
- O agente não tem acesso ao mapa completo durante a execução;
- Visualização dos movimentos do agente no console;
- Exibição da pontuação durante o jogo;
- Exibição da pontuação final;
- Revelação do mapa completo apenas ao final da partida.

## Elementos do labirinto

O labirinto possui:

- **2 Wumpus**;
- **4 poços**;
- **3 pedras de ouro**;
- **2 morcegos gigantes**.

A posição dos elementos é sorteada automaticamente no início do programa. A posição inicial `[1,1]` é mantida livre para o agente começar o jogo.

## Ações do agente

O agente pode executar as seguintes ações:

| Tecla | Ação | Descrição |
|---|---|---|
| `F` | Mover_para_frente | Move o agente uma casa na direção em que ele está olhando |
| `D` | Virar_a_direita | Rotaciona o agente 90° para a direita |
| `P` | Pegar_objeto | Pega o ouro, caso exista ouro na sala atual |
| `T` | Atirar_flecha | Atira uma flecha em linha reta na direção atual do agente |
| `S` | Subir | Sai da caverna, se o agente estiver na posição `[1,1]` |

## Sensores do agente

O agente recebe percepções do ambiente conforme sua posição:

| Sensor | Quando acontece |
|---|---|
| Fedor do Wumpus | Quando existe um Wumpus em sala adjacente, exceto diagonal |
| Brisa | Quando existe um poço em sala adjacente, exceto diagonal |
| Barulho de morcego | Quando existe um morcego em sala adjacente, exceto diagonal |
| Brilho do ouro | Quando existe ouro na sala atual |
| Impacto na parede | Quando o agente tenta andar contra uma parede |
| Grito do Wumpus | Quando o Wumpus é morto por uma flecha |

## Sistema de pontuação

Cada ação executada possui custo de `-1`.

Além disso, existem recompensas e penalidades específicas:

| Evento | Pontuação |
|---|---:|
| Pegar ouro | `+1000` |
| Cair em um poço | `-1000` |
| Ser devorado pelo Wumpus | `-1000` |
| Atirar flecha | `-10` |

Observação: ao atirar uma flecha, o agente também sofre o custo normal da ação, ou seja, o custo total do disparo é `-11`.

## Modos de jogo

O programa possui dois modos de execução:

### 1. Modo manual

No modo manual, o usuário controla o agente digitando as ações pelo teclado.

Exemplo:

```text
F - Mover_para_frente
D - Virar_a_direita
P - Pegar_objeto
T - Atirar_flecha
S - Subir
```

### 2. Modo automático simples

No modo automático, o agente toma decisões básicas usando apenas as percepções recebidas.

As principais regras usadas pelo agente automático são:

- Se perceber brilho, pega o ouro;
- Se estiver na posição `[1,1]` e já tiver ouro, sai da caverna;
- Se não perceber brisa, fedor ou barulho de morcego, considera as casas adjacentes como seguras;
- Tenta visitar casas seguras ainda não visitadas;
- Caso não encontre uma casa segura, tenta retornar para `[1,1]`;
- Se perceber fedor e ainda tiver flecha, pode atirar.

Esse agente automático é propositalmente simples e não consulta diretamente o mapa real do jogo.

## Como executar

É necessário ter o **Python 3** instalado.

No terminal, execute:

```bash
python mundo_wumpus.py
```

Em alguns sistemas, pode ser necessário usar:

```bash
python3 mundo_wumpus.py
```

Após executar, escolha o modo de jogo:

```text
1 - Manual
2 - Automático simples
```

## Visualização do mapa

Durante o jogo, o programa exibe apenas o mapa conhecido pelo agente.

Legenda do mapa conhecido:

| Símbolo | Significado |
|---|---|
| `A` | Agente |
| `E` | Entrada/Saída |
| `*` | Sala já visitada |
| `?` | Sala desconhecida |

Ao final do jogo, o mapa completo é revelado.

Legenda do mapa completo:

| Símbolo | Significado |
|---|---|
| `A` | Posição final do agente |
| `E` | Entrada/Saída |
| `W` | Wumpus vivo |
| `P` | Poço |
| `O` | Ouro |
| `M` | Morcego |
| `.` | Sala vazia |

## Estrutura principal do código

O programa foi organizado em classes:

### `Agente`

Representa o agente do jogo.

Armazena informações como:

- posição atual;
- direção atual;
- pontuação;
- quantidade de ouro coletado;
- quantidade de flechas;
- estado de vida;
- salas visitadas;
- últimas percepções especiais.

### `MundoWumpus`

Representa o ambiente do jogo.

Responsável por:

- criar a matriz 6 x 6;
- sortear os elementos;
- verificar sensores;
- executar ações;
- resolver morte, teleporte por morcego e coleta de ouro;
- exibir o mapa conhecido e o mapa completo.

### `AgenteLogicoSimples`

Representa um agente automático simples.

Ele toma decisões com base nas percepções e nas salas consideradas seguras.

## Observações

- O mapa completo não é exibido durante a partida para respeitar a regra de que o agente não pode conhecer previamente o ambiente.
- Os morcegos transportam o agente para uma posição aleatória e depois retornam para a sala original.
- O agente pode ser transportado para uma sala segura, para um poço, para um Wumpus ou até para outro morcego.
- O jogo pode ser encerrado por saída da caverna, morte ou limite de passos no modo automático.

## Arquivo principal

O arquivo principal do projeto é:

```text
mundo_wumpus.py
```

