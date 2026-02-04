# 👽 Ben 10: A Ameaça Eterna 2D

Um jogo de sobrevivência estilo *Roguelite* desenvolvido em **Python** com a biblioteca **Pygame**. O projeto desafia o jogador a sobreviver a hordas de Cavaleiros Eternos utilizando o icônico Omnitrix para se transformar em diferentes formas alienígenas, cada uma com habilidades únicas.

---

## 🛠️ Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-000000?style=for-the-badge&logo=python&logoColor=4FC08D)

---

## 🎮 Galeria de Transformações

| Ben | Chama | Quatro Braços | XLR8 | Diamante |
| :---: | :---: | :---: | :---: | :---: |
| ![Ben](assets/images/player/ben.png) | ![Chama](assets/images/player/chama.png) | ![4B](assets/images/player/quatro_bracos.png) | ![XLR8](assets/images/player/xlr8.png) | ![Diamante](assets/images/player/diamante.png) |

## 🧠 Conceitos de Engenharia de Software Aplicados

O desenvolvimento deste projeto focou em práticas modernas de arquitetura de software:

* **Máquina de Estados Finita (FSM):** Gerenciamento robusto dos estados do jogo (`Menu`, `Gameplay`, `LevelUp`, `GameOver`) e estados do jogador (`Normal`, `Dash`, `SuperPulo`).
* **Data-Driven Design:** As estatísticas e habilidades dos aliens são configuradas em dicionários modulares (`ALIEN_DATA`), permitindo balanceamento rápido sem alterar a lógica principal.
* **Matemática Vetorial:** Uso de `pygame.math.Vector2` para movimentação fluida, detecção de colisão circular e lógica de projéteis.
* **Sistemas de Partículas e Feedback:** Implementação de *Screen Shake*, textos flutuantes de dano e partículas para aumentar o *game feel*.
* **Sistema de XP e Upgrades:** Lógica de progressão utilizando funções *lambda* e escolha aleatória de habilidades ao subir de nível.

## 🚀 Como Executar o Projeto

1. Certifique-se de ter o Python instalado.
2. Instale as dependências:
   ```bash
   pip install pygame
