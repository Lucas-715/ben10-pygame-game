"""
main.py — Ponto de entrada do jogo "Ben 10 - A Ameaça Eterna 2D".

Uso:
    python main.py             # joga normalmente
    python main.py --smoke     # teste rápido (sem janela) para validar o jogo
"""
import os
import sys

# garante que o diretório do jogo esteja no caminho de busca do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.game import Game  # noqa: E402


def main():
    smoke_test = "--smoke" in sys.argv
    Game().run(smoke_test=smoke_test)


if __name__ == "__main__":
    main()
