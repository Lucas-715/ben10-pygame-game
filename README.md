# 👽 Ben 10: A Ameaça Eterna 2D

🔗 **Repositório de Lógica e Automação:** [Clique aqui](https://github.com/Lucas-715/python-logic-automation)

Um jogo de sobrevivência estilo *Roguelite* desenvolvido em **Python** com a biblioteca **Pygame**. O projeto desafia o jogador a sobreviver a hordas de Cavaleiros Eternos utilizando o icônico Omnitrix para se transformar em diferentes formas alienígenas, cada uma com habilidades únicas.

---

## 🛠️ Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-000000?style=for-the-badge&logo=python&logoColor=4FC08D)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

---

## 🎮 Galeria do Jogo

### **Transformações do Jogador**
| Ben | Chama | Quatro Braços | XLR8 | Diamante |
| :---: | :---: | :---: | :---: | :---: |
| ![Ben](assets/images/player/ben.png) | ![Chama](assets/images/player/chama.png) | ![4B](assets/images/player/quatro_bracos.png) | ![XLR8](assets/images/player/xlr8.png) | ![Diamante](assets/images/player/diamante.png) |

### **Inimigos e Itens**
| Cavaleiro Nível 1 | Cavaleiro Nível 2 | Baú Mágico |
| :---: | :---: | :---: |
| ![Inimigo 1](assets/images/enemies/cavaleiro_nivel1.png) | ![Inimigo 2](assets/images/enemies/cavaleiro_nivel2.png) | ![Baú](assets/images/objects/bau_magico.png) |

---

## 🧠 Conceitos de Engenharia de Software Aplicados

* **Máquina de Estados Finita (FSM):** Gerenciamento de estados como `Menu`, `Gameplay`, `LevelUp` e `GameOver`.
* **Data-Driven Design:** Estatísticas e habilidades configuradas em dicionários modulares (`ALIEN_DATA`) para fácil balanceamento.
* **Matemática Vetorial:** Uso de `pygame.math.Vector2` para movimentação, colisões e lógica de projéteis.
* **Feedback Visual (Game Feel):** Implementação de *Screen Shake*, partículas e textos flutuantes de dano.
* **Programação Funcional:** Lógica de progressão e upgrades utilizando funções `lambda`.

## 🚀 Como Executar o Projeto

1. Certifique-se de ter o Python instalado.
2. Instale as dependências:
   ```bash
   pip install pygame
   ```
3. Clone o repositório:
   ```bash
   git clone https://github.com/Lucas-715/ben10-survival-pygame.git
   ```
4. Execute o Arquivo Principal
   ```bash
   python main.py
   ```

## ⌨️ Controles

* Setas / WASD: Movimentação.

* Z: Ataque Primário.

* X: Habilidade Especial.

* SHIFT: Dash Elétrico (Esquiva).

* Vírgula (,) / Ponto (.): Selecionar Alien no Omnitrix.

* **ENTER: Confirmar Transformação / Iniciar Jogo.**
