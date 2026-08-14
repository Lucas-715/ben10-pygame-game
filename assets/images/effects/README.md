# 🎨 Efeitos de pixel art (baixados)

Pixel arts de efeitos com **licença livre** (CC0 / CC-BY) para os poderes e armas
do jogo. **Nenhum asset usa personagens da série Ben 10** (marca registrada) —
tudo é efeito genérico (fogo, explosão, cristal, raio, orbes) que encaixa nos
poderes sem problema legal.

## Estrutura (por tipo de poder)

```
effects/
├── fire/        → Bola de Fogo (Chama), Firebomb, Plant Missile
├── explosion/   → Explosão da Supernova, Splash, Water Blast
├── crystal/     → Estilhaço de Diamante / Campo de Cristais (8 cores)
├── lightning/   → Ataque em Cadeia do XLR8 (bolts e raios)
├── orbs/        → Projéteis genéricos (minigun, orbes mágicos, sparks)
└── ui/          → Coração (vida), Baú, Escudo
```

## Origem e licença

| Asset | Fonte | Licença | Autor |
|---|---|---|---|
| `fire/*`, `lightning/*`, `orbs/*`, `ui/Pixelart Shield.png` | [Pixel Art Spells](https://opengameart.org/content/pixel-art-spells) | CC0 | DevWizard |
| `explosion/explosionframes.png` | [Explosion Animated](https://opengameart.org/content/explosion-animated) | CC-BY 3.0 | Ville Seppanen |
| `crystal/*` | [Crystals 1.1](https://opengameart.org/content/crystals-0) | CC0 | — (ver `sources.md`) |
| `lightning/Lightning_Yellow.png` | [Pixel Lightning](https://opengameart.org/content/pixel-lightning) | CC-BY 4.0 | Marco L. |
| `ui/hearts32x32.png` | [Hearts 32x32 & 16x16](https://opengameart.org/content/hearts-32x32-16x16) | CC0 | Leozlk |
| `ui/ChestRed.png` | [Pixel chest and coin](https://opengameart.org/content/pixel-chest-and-coin) | CC0 | hippo |

## Já integrado no jogo

- `../ui/vida.png` ← primeiro quadro do coração (32×32) — usado no HUD
- `../objects/bau_magico.png` ← baú vermelho redimensionado (50×50)
- `../ui/escudo.png` ← primeiro quadro do escudo (48×48) — usado no HUD

> ⚠️ **Personagens (aliens e inimigos) usam as artes originais do jogo** — os
> sprites de efeitos desta pasta são exclusivamente para PODERES e ARMAS
> (Bola de Fogo, explosões, cristais, raios, orbes e ícones de power-up).

## Nota CC-BY (atribuição obrigatória)

- **Explosão** (Ville Seppanen): incluir "Ville Seppanen" na lista de créditos.
- **Raios** (Marco L.): incluir "Marco L." na lista de créditos.

## Sugestões de uso no código

- `fire/Fireball.png` (96×16, 3 quadros) → sprite animado da Bola de Fogo.
- `crystal/crystal-cyan/blue.png` → Estilhaço de Diamante (substituir o círculo).
- `explosion/explosionframes.png` (1024×384) → animação da Supernova.
- `lightning/Light Bolt.png` → linhas do Ataque em Cadeia do XLR8.
