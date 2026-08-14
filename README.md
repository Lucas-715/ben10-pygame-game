# 👽 Ben 10: A Ameaça Eterna 2D

Um jogo de sobrevivência estilo *Roguelite* (inspirado em **20 Minutes Till Dawn**) desenvolvido em **Python** com **Pygame**. Sobreviva a hordas de Cavaleiros Eternos usando o **Omnitrix**: cada alien tem seus poderes característicos do Ben 10, com **mira no mouse**, câmera inclinada na direção do cursor e um sistema completo de **power-ups, fusões e combos** (Fase 2).

## 🚀 Como executar

1. Tenha o Python instalado (3.10+).
2. Instale o Pygame:
   ```bash
   pip install pygame
   ```
3. Rode o jogo:
   ```bash
   python main.py
   ```
   > No Windows, basta dar dois cliques em `run.bat`.

**Teste rápido (sem abrir janela):**
```bash
python main.py --smoke
```

## ⌨️ Controles

| Tecla | Ação |
| :--- | :--- |
| `WASD` / `Setas` | Movimentação (suave, com aceleração e atrito) |
| **Mouse** | Mira — o personagem gira para onde o cursor aponta |
| **Clique esquerdo (segurar)** | Usa o poder primário do alien atual na direção do mouse |
| `X` | Habilidade especial do alien |
| `F` | **Fusão** — ativa quando a barra **PRISMA** está cheia (combina o alien atual com o selecionado) |
| `SHIFT` | Dash na direção da mira (com invencibilidade) |
| `,` / `.` / **roda do mouse** | Escolhe o alien no Omnitrix |
| `ENTER` | Transforma no alien escolhido |
| `1` / `2` / `3` | No título: escolher modo de jogo |
| `ESC` | Pausa |

## 👽 Os poderes de cada alien (como no desenho)

| Alien | Poder primário (clique) | Especial (X) |
| :--- | :--- | :--- |
| **Ben** | Soco em arco (rápido) | — |
| **Quatro Braços** | Pancada no Chão (retângulo com knockback) | Super Pulmão (salta na direção da mira e explode no pouso) |
| **XLR8** | Ataque em Cadeia (atinge os inimigos mais próximos) | Super Velocidade (turbo com dano de contato) |
| **Chama** | Bola de Fogo (explode em área) | Supernova (explosão gigante ao redor) |
| **Diamante** | Estilhaço de Diamante (rápido e perfurante) | Campo de Cristais (cristais orbitam o corpo) |

## ⚡ FASE 2 — Combate dinâmico

### 🟣 Fusões do Omnitrix (Modo Prisma)
A barra **PRISMA** (canto superior direito) enche ao acertar golpes e coletar orbes. Quando está cheia, pressione **F** para fundir o **alien atual + o alien selecionado**:

| Fusão | Combinação | Efeito |
| :--- | :--- | :--- |
| **Punho Relâmpago** | Quatro Braços + XLR8 | 4 socos/segundo com knockback |
| **Fúria Congelante** | Quatro Braços + Diamante | Socos deixam os inimigos lentos |
| **Chama Veloz** | Chama + XLR8 | Rajada de 3 bolas de fogo + rastro que queima |
| **Cristal Blindado** | Diamante + Quatro Braços | Estilhaços explodem em área ao acertar |
| **Supernova Precoce** | Chama + Diamante | Especial mais rápido, mas com dano reduzido |

### 🎁 Núcleos Instáveis (22 power-ups)
Inimigos e baús soltam **Núcleos** coloridos — a cor indica a raridade (comum → raro → épico → **lendário**). Ao pegar, o efeito ativa na hora com anúncio arcade:

- **Comuns:** Coração de Ben (cura+regen), Botas de Kevin (+velocidade), Escudo Petrossápien, Ímã de Orbes, Recarga Rápida.
- **Raros:** Minigun do Sumo Sacerdote, Sanguessuga (vampirismo), Sombra de Kevin (clone), Campo Anti-Gravidade, Fúria do Way Big, Bomba Relógio.
- **Épicos:** Traje Venom (3x tudo, sem especial), Núcleo Instável de Chama (golpes explodem), Ricochete Diamante, Fome Voraz, Congelamento em Massa.
- **Lendários:** Punhos x4, Modo Way Big Furioso, Caos do Baú Mágico, Clone Bagunçado, Fúria Final, Sorte do Omnitrix.

### 🥊 Combos (skill expression)
- **Golpe Triplo:** 3 acertos em 1,5s → próximo golpe com **+50%** (contador no HUD).
- **Troca Relâmpago:** transformar e atacar em até 0,4s → **crítico 2x**.
- **Combo Elemental:** Chama seguido de Diamante em 2s → estilhaço pega fogo (explode ao acertar).

## 🎮 Modos de jogo

- **Arena Infinita (1):** o modo de sobrevivência, com **melhores marcas salvas** em `scores.json`.
- **Campanha 1-10 (2) e Duelo Online (3):** *em breve* — próximos marcos.

## 🎯 Destaques das versões

* **Mira com mouse**: todos os poderes são disparados na direção do cursor, com crosshair animado e círculo sutil mostrando o alcance do poder atual.
* **Câmera inclinada**: a visão de cima faz uma leve rotação/inclinação na direção do mouse (pseudo-3D), com a mira compensada para continuar precisa.
* **Limite do mapa = limite da câmera**: a câmera para na borda do mundo.
* **Poderes preservados**: cada alien mantém suas características do Ben 10 (sem armas genéricas).
* **Power-ups data-driven**: os 22 efeitos são dicionários em `settings.py` — o sorteio escolhe por peso, sem lógica hardcoded.
* **Movimentação melhorada**: aceleração, atrito e velocidade máxima, tudo independente de FPS.
* **Código legível**: o `main.py` gigante virou um pacote organizado (`game/`).

## 🗂️ Estrutura do projeto

```
ben10-game/
├── main.py              # Ponto de entrada (python main.py)
├── run.bat              # Atalho para Windows
├── scores.json          # Melhores marcas da Arena (criado ao jogar)
└── game/
    ├── settings.py      # Toda a configuração (aliens, power-ups, fusões, inimigos)
    ├── assets.py        # Carregamento de imagens/sons (com fallback)
    ├── audio.py         # Música ambiente por "humor" do jogo
    ├── entities.py      # Jogador, inimigos, orbes, baús, projéteis, Núcleos
    ├── camera.py        # Câmera que segue, treme, inclina e para na borda do mapa
    ├── effects.py       # Partículas e textos flutuantes de dano
    ├── world.py         # Poderes, horda, colisões, power-ups, fusões e combos
    ├── ui.py            # HUD, crosshair, banners arcade e telas de menu
    └── game.py          # Classe Game: estados, loop e recordes
```

## 🧠 Conceitos de engenharia aplicados

* **Arquitetura em camadas**: configuração → assets → entidades → mundo → câmera → UI → orquestrador.
* **Máquina de estados**: `title`, `playing`, `level_up`, `paused`, `game_over`.
* **Data-driven**: poderes, power-ups, fusões, inimigos e aliens são dicionários em `settings.py`.
* **Matemática vetorial**: movimentação com `Vector2`, projéteis, pancadas (dot/cross) e inclinação da câmera.
* **Game feel**: screen shake, partículas, hit-flash, knockback, números de dano e banners de anúncio.
* **Código tolerante a falhas**: assets ausentes viram placeholders silenciosos.
* **Smoke test embutido**: `python main.py --smoke` percorre aliens, power-ups, fusões e combos.

## 🛠️ Tecnologias

Python · Pygame 2.6+ · Git · JSON (recordes)

## 📸 Assets

Imagens originais dos aliens (Ben, Chama, Quatro Braços, Diamante, XLR8), inimigos (Cavaleiros, Caveira, Magma), baú mágico e sons em `assets/`.
