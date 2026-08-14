# BEN 10 — A AMEAÇA ETERNA 2D
## Documento Completo do Jogo — Guia de Habilidades, Personagens e Sistemas

> Este documento descreve **como o jogo funciona**, sem código. Cobre todos os
> personagens, habilidades, inimigos, power-ups, fusões, combos, HUD, câmera,
> efeitos visuais, áudio e a arquitetura por trás de tudo.

---

## 1. Visão geral

O jogo é um **roguelite de sobrevivência em arena** (estilo *20 Minutes Till
Dawn* / *Vampire Survivors*), ambientado no universo do Ben 10. O jogador
controla **um personagem visto de cima** dentro de um mundo de **3000×2000
pixels**, lutando contra hordas infinitas de cavaleiros que surgem **longe da
tela** e caminham até ele.

A mecânica central é o **Omnitrix**: em vez de trocar de arma, o jogador
**troca de alien** — e cada alien tem um poder primário (clique esquerdo) e uma
habilidade especial (tecla **X**) completamente diferentes. O mouse controla a
**mira** (o personagem gira e ataca na direção do cursor), e a câmera se
**inclina levemente** para o lado onde o mouse aponta, criando uma sensação
pseudo-3D.

Sobre a base original de sobrevivência, foram adicionados em "Fase 2":
**22 power-ups** aleatórios por raridade, **20 fusões de aliens** por sistema de
traços, **3 combos** de habilidade, recordes locais e efeitos visuais
procedurais.

---

## 2. Controles

| Entrada | Ação |
|---|---|
| **WASD / Setas** | Mover (com aceleração e atrito suaves) |
| **Mouse** | Mirar — o personagem e a câmera se orientam para o cursor |
| **Clique esquerdo (segurar)** | Poder primário do alien atual (dispara sozinho enquanto segurado) |
| **X** | Habilidade especial do alien atual |
| **F** | Ativar a Fusão do Omnitrix (quando a barra Prisma estiver cheia) |
| **SHIFT (esq/dir)** | Dash — **na direção do movimento** (WASD); parado, cai para a mira |
| **`,` / `.` ou roda do mouse** | Escolher o próximo alien no Omnitrix |
| **ENTER** | Transformar no alien escolhido (sem escolha, avança para o próximo) |
| **ESC** | Pausar / continuar |
| **1 / 2 / 3** | Selecionar modo de jogo na tela inicial |
| **R** | Reiniciar na tela de Game Over |

> O clique dispara **enquanto está segurado** (autofire), então basta apontar
> e segurar para o alien atacar continuamente respeitando o cooldown.

---

## 3. Modos de jogo

| Modo | Status | Descrição |
|---|---|---|
| **1 — Arena Infinita** | ✅ Funcional | O modo de sobrevivência: horda sem fim, dificuldade cresce com o tempo, recordes salvos em `scores.json` (top 5) |
| **2 — Campanha 1-10** | 🚧 Em breve | Níveis com objetivos e chefes (anunciado no menu, bloqueado) |
| **3 — Duelo Online** | 🚧 Em breve | 1x1 contra outro jogador (anunciado no menu, bloqueado) |

Na tela inicial, os três modos aparecem com as teclas 1/2/3 e o ENTER começa a
partida (só o modo Arena está liberado; os outros mostram "EM BREVE").

---

## 4. O Omnitrix — energia e transformação

- O jogador começa como **Ben** (forma humana, sem custo para manter).
- Qualquer outro alien **drena energia** enquanto transformado:
  - **Drena 5% por segundo** enquanto estiver transformado.
  - Se a energia zerar, volta automaticamente para o **Ben**.
- Como **Ben**, a energia **recarrega 10% por segundo**.
- **Transformar custa 10% de energia** (voltar para o Ben é grátis).
- Sem energia suficiente, o jogo avisa "Energia insuficiente" no banner.

**A troca funciona em dois passos (para nunca travar):**
1. **Escolhe** o alien (`,` / `.` / roda do mouse) — circula pelos **5 aliens**,
   todos acessíveis a partir de qualquer ponto (correção do bug antigo em que
   só dava para chegar a Quatro Braços e Diamante a partir do Ben).
2. **Transforma** com **ENTER** — se nenhum alien foi escolhido, o ENTER
   simplesmente avança para o próximo alien, então a troca nunca trava.

O sprite do jogador **gira na direção da mira** e um círculo sutil no chão
mostra o **alcance do poder primário** do alien atual.

---

## 5. Os 5 Aliens do Omnitrix

Cada alien tem três componentes:
- **Stats** — multiplicadores de velocidade, vida máxima e dano.
- **Ataque primário** (clique) — o poder que ele usa enquanto segura o botão.
- **Especial** (X) — habilidade forte com cooldown próprio.

### 5.1 Ben — "Soco" (o humano, forma versátil)

| Atributo | Valor |
|---|---|
| Velocidade | ×1.0 (100% da base, 230 px/s) |
| Vida | ×1.0 (10 de vida) |
| Dano | ×1.0 |
| **Primário — Soco** | Golpe em arco de **120°**, alcance **95 px**, dano **1**, cooldown **0.25s**, knockback 120 |
| **Especial** | ❌ Não tem (Ben é o equilibrante; sua energia recarrega) |

Ben é o alien mais rápido de atacar (0,25s de cooldown) e **não drena
energia** — é a forma de "respirar" e recarregar o Omnitrix. O soco em arco
acerta tudo na frente e também quebra baús.

### 5.2 Quatro Braços — "Pancada no Chão" (o tanque)

| Atributo | Valor |
|---|---|
| Velocidade | ×0.85 (mais lento) |
| Vida | ×1.4 (14 de vida) |
| Dano | ×1.2 |
| **Primário — Pancada no Chão** | Retângulo de pancada na direção da mira: alcance **250 px**, largura **150 px**, dano **2**, cooldown **1.2s**, knockback 160 |
| **Especial — Super Pulmão** | Salta até **350 px** na direção da mira (invencível no ar); ao **pousar**, detona uma **onda de pressão cinética** de raio **120** causando dano **2**; cooldown **4.5s** |

O tanque do grupo: aguenta mais, bate forte em área, mas é lento. O pouso do
Super Pulmão usa o efeito visual de **choque de pressão (força bruta)** —
anel irregular cinza/vermelho com raios de velocidade e poeira, **sem fogo**.

### 5.3 XLR8 — "Ataque em Cadeia" (o velocista)

| Atributo | Valor |
|---|---|
| Velocidade | ×1.5 (bem mais rápido) |
| Vida | ×0.9 (9 de vida) |
| Dano | ×0.9 |
| **Primário — Ataque em Cadeia** | Atinge os **3 inimigos mais próximos** dentro de **350 px** em sequência, com raio visual; dano **1**, cooldown **1.4s**; dá invencibilidade curta (0,5s) ao atravessar |
| **Especial — Super Velocidade** | Turbo por **3s**: velocidade ×2, **invencível** e mata qualquer inimigo que encostar (dano de contato 999); cooldown **10s** |

O velocista: atravessa a horda e o turbo é um "limpador de contato" poderoso.

### 5.4 Chama — "Bola de Fogo" (o artilheiro)

| Atributo | Valor |
|---|---|
| Velocidade | ×1.0 |
| Vida | ×1.0 |
| Dano | ×1.1 |
| **Primário — Bola de Fogo** | Projétil de fogo a **560 px/s**, alcance **420 px**, dano **1**, cooldown **0.45s**; **explode ao atingir** em área de raio **80** (animação de explosão em 24 quadros) |
| **Especial — Supernova** | Explosão massiva ao redor do jogador: raio **180**, dano **3**, cooldown **7.5s** |

O alien de dano em área: cada bola de fogo explode, e a Supernova é a "limpa
tela" de emergência.

### 5.5 Diamante — "Estilhaço de Diamante" (o sniper)

| Atributo | Valor |
|---|---|
| Velocidade | ×0.95 |
| Vida | ×1.2 (12 de vida) |
| Dano | ×1.0 |
| **Primário — Estilhaço de Diamante** | Projétil de cristal girando a **820 px/s**, alcance **900 px** (o maior do jogo), dano **2**, cooldown **0.5s**, **perfura até 4 inimigos** |
| **Especial — Campo de Cristais** | **8 cristais** orbitam o jogador por **4s**, dano **1** cada ao encostar; cooldown **12s** |

O sniper: alcance gigante e perfuração, ideal para abrir baús e acertar à
distância.

---

## 6. Fusões do Omnitrix (Modo Prisma) — 20 combinações

### Como funciona
- Cada golpe acertado, Núcleo coletado e orbe de XP enche a **barra Prisma**
  (ganho: **4 por golpe**, **1 por Núcleo**, **0.5 por orbe**, com teto de 10
  por frame para não encher de uma vez).
- Quando a barra enche, o jogo **sorteia um alien parceiro** (mostrado no HUD:
  "PRISMA CHEIA — Fusão: + X (F)").
- Com **F**, a fusão ativa por **8 segundos**: o alien ativo **não troca de
  corpo** — ele **empresta o traço** do parceiro para o seu ataque primário.
- **O parceiro nunca é o próprio alien** (sorteado entre os outros 4), então
  são **5 bases × 4 parceiros = 20 combinações**.
- Ao acabar, a fusão deixa uma **"ressaca"** universal: **-15% de velocidade
  por 3s** (o efeito não é grátis de reutilizar).

### Os 5 traços emprestáveis

| Parceiro sorteado | Traço | Efeito no ataque primário do alien ativo |
|---|---|---|
| **Ben** | Versatilidade (cadência) | Cooldown do ataque primário **× 0.65** (ataca quase 35% mais rápido) |
| **Quatro Braços** | Força Bruta (impacto) | Dano bônus (+1.5 × bônus de dano), knockback extra e **onda de pressão cinética** de raio 70 causando **35% do dano** em área ao acertar |
| **XLR8** | Velocidade (rajada) | O ataque dispara em **rajada de 2 a 4 golpes** seguidos (conforme a cadência natural do poder; cada golpe mais fraco, ~65-70%) |
| **Chama** | Elemental (fogo) | Todo golpe **explode em área** ao acertar (raio 55, **50% do dano** extra); bolas de fogo explodem com raio ×1.35 |
| **Diamante** | Perfuração (alcance) | Ataque ganha **alcance estendido** (soco +70 px, pancada +40 px de largura, cadeia +60 px, bola de fogo +100 px) e estilhaços perfuram +2 |

### Como cada traço se comporta em cada alien (exemplos reais)

| Você é… | Sorteia… | Resultado |
|---|---|---|
| Ben | XLR8 | Soco em arco vira **4 socos rápidos em sequência** ("Punho Relâmpago") |
| Diamante | Quatro Braços | Estilhaço acerta e solta uma **onda de pressão cinética** no ponto de impacto ("Estilhaço Esmagador") |
| Chama | XLR8 | Bola de Fogo dispara em **rajada de 3** com leve espalhamento |
| Quatro Braços | Diamante | Pancada fica **mais larga** (+40 px) e o impacto se propaga |
| XLR8 | Chama | Ataque em Cadeia faz **cada acerto explodir** em área |
| Ben | Diamante | Soco ganha **alcance estendido** (+70 px) — soco de longo alcance |

### Visual da fusão
Enquanto ativa, o personagem ganha uma **aura pulsante** na cor do traço
emprestado, **fragmentos orbitando** e anéis que "respiram" — além dos projéteis
ganharem um anel da cor do traço.

---

## 7. Inimigos (horda)

### Tipos, estatísticas e desbloqueio

| Inimigo | Vida | Velocidade | Dano | XP | Desbloqueio | Peso de spawn |
|---|---|---|---|---|---|---|
| **Cavaleiro Nv.1** | 2 | 1.15 | 1 | 10 | Desde o início | 10 |
| **Cavaleiro Nv.2** | 4 | 1.25 | 1 | 15 | 20 abates | 8 |
| **Cavaleiro Nv.3** | 9 | 1.4 | 1 | 25 | 60 abates | 6 |
| **Caveira** | 1 | 2.1 | 1 | 5 | 120s de jogo | 5 |
| **Cavaleiro de Magma** | 16 | 0.85 | 2 | 40 | 240s de jogo | 3 |

- A velocidade exibida é multiplicada por **95 px/s** (Cavaleiro Nv.1 anda a
  ~109 px/s no início).
- **Inimigos morrem ao encostar no jogador** (causam o dano dele e somem) —
  evita empilhamento sobre o personagem.
- Ao morrer, soltam partículas roxas, **orbe(s) de XP**, **10% de chance** de
  orbe de vida e **6% de chance** de um Núcleo Instável (power-up).

### Curva de dificuldade (Arena Infinita)
- **Vida cresce com o tempo**: +0,8% por segundo, até **×2.2** no máximo.
- **Velocidade começa tranquila e acelera aos poucos**: nos primeiros **35s** a
  velocidade é a base (graça inicial); depois cresce **+0,6% por segundo**, com
  teto de **×1.8**.
- **Spawn fica mais rápido**: intervalo base de **1.8s**, diminuindo
  **0.004s/s** até o mínimo de **0.35s**.

### Spawn longe do jogador (correção das bordas)
- Os inimigos nascem a **430–560 px** do centro da câmera, **fora da área
  visível** (a vista da câmera + 90 px de margem é respeitada).
- Nos cantos do mundo, onde não existe ponto fora da tela, eles nascem
  **encostados na borda oposta ao jogador** e caminham até ele — nunca surgem
  do nada dentro da tela, mesmo com a câmera travada no limite do mapa.

---

## 8. Objetos do mundo

| Objeto | Comportamento |
|---|---|
| **Orbe de XP** (azul) | Solto pelos inimigos; **ímã** atrai quando o jogador passa perto (raio 130 px); dá XP |
| **Orbe de Vida** (verde) | 10% de chance; recupera **1 de vida**; com o power-up Fome Voraz recupera 2 |
| **Baú Mágico** | Aparece a cada **15s** no mundo; tem **5 de vida** e leva dano de **todos** os ataques (soco, pancada, projéteis, explosões, cristais, cadeia); ao quebrar solta **3 orbes de vida + 1 Núcleo Instável sempre** |
| **Núcleo Instável** | Power-up caído; pulsa na cor da raridade; atrai como ímã; **ativa na hora** ao tocar |

---

## 9. Power-ups — 22 Núcleos Instáveis

### Raridades e frequência

| Raridade | Cor | Chance de drop | Filosofia |
|---|---|---|---|
| **Comum** | Cinza/branco | 50% dos drops | Sobrevivência, previsível |
| **Raro** | Azul | 30% | Muda o estilo por um tempo |
| **Épico** | Roxo | 15% | Poderoso e arriscado |
| **Lendário** | Dourado | 5% | Overpower, o "UAU" da run |

### 🟢 Comuns

| # | Nome | Efeito |
|---|---|---|
| 1 | **Coração de Ben** | Cura 25% da vida máxima + regenera 1%/s por 10s |
| 2 | **Botas de Kevin 11** | +25% velocidade de movimento por 12s |
| 3 | **Escudo Petrossápien** | Bloqueia o próximo golpe recebido (acumula até 3 cargas, mostradas no HUD com ícone xN) |
| 4 | **Ímã de Orbes Turbo** | Raio de coleta de XP ×3 por 20s |
| 5 | **Recarga Rápida** | Zera todos os cooldowns ativos instantaneamente (primário, especial e dash) |

### 🔵 Raros

| # | Nome | Efeito |
|---|---|---|
| 6 | **Minigun do Sumo Sacerdote** | Ataque primário vira **disparo automático contínuo** por 15s (balas de orbe mágico animado, dano baixo 0.5, cadência altíssima 0.08s) |
| 7 | **Sanguessuga (Vampiro)** | Todo golpe acertado recupera **15% do dano** por 15s |
| 8 | **Sombra de Kevin** | Um **clone inteligente** copia seus ataques com 50% de dano por 12s |
| 9 | **Campo Anti-Gravidade** | Inimigos num raio de 520 px ficam **40% mais lentos** por 8s |
| 10 | **Fúria do Way Big (mini)** | +30% de dano, -20% de velocidade por 10s |
| 11 | **Bomba Relógio** | **Explosão no jogador a cada 2s** por 12s (raio 100, dano 2) — não machuca o jogador, só os inimigos |

### 🟣 Épicos

| # | Nome | Efeito |
|---|---|---|
| 12 | **Traje Venom (Triplo)** | **×3 dano, cadência e velocidade** por 8s, mas **bloqueia o especial (X)** e ao acabar dá "ressaca" de **-20% velocidade por 3s** |
| 13 | **Núcleo Instável de Chama** | Todo golpe primário **explode como Bola de Fogo** por 12s (raio 55, +40% do dano em área) |
| 14 | **Ricochete Diamante** | Projéteis **ricocheteiam em até 2 inimigos extras** por 15s |
| 15 | **Fome Voraz** | Vampirismo de **40%** + orbes de vida curam **2** por 10s |
| 16 | **Congelamento em Massa** | Todos os inimigos na tela ficam **paralisados por 3s** (efeito único) |

### 🔴 Lendários

| # | Nome | Efeito |
|---|---|---|
| 17 | **Punhos de Quatro Braços x4** | **4 socos/segundo** com força de Quatro Braços (alcance 135, arco 140°, knockback 150) por 8s |
| 18 | **Modo Way Big Furioso** | **Pisão de terremoto**: explosão de raio 520 causando dano 6 em tudo + **+100% de dano por 6s**, com tremor forte |
| 19 | **Caos do Baú Mágico** | Um **baú extra cai perto a cada 3s** por 12s (chovendo orbes de vida e Núcleos) |
| 20 | **Clone Bagunçado** | **2 a 4 clones** com IA aleatória (atiram em qualquer direção, 40% do dano) por 10s |
| 21 | **Fúria Final** | Dano alto (8) em **todos** os inimigos da tela; sobreviventes ficam com **-50% de vida máxima** por 10s |
| 22 | **Sorte do Omnitrix** | Ativa **2 power-ups aleatórios** de nível comum/raro de uma vez |

### Detalhes de sistema
- Ao coletar, um **banner arcade** anuncia o nome (cor da raridade) e, para
  épicos/lendários, há tremor de tela.
- Power-ups ativos ficam no HUD com **ícone + nome + círculo de contagem
  regressiva** (o nome fica visível enquanto o efeito durar).
- Núcleos coletados também dão **+1 de Prisma**.

---

## 10. Combos (skill expression)

| Combo | Como ativar | Efeito |
|---|---|---|
| **Golpe Triplo** | Acertar **3 ataques primários em 1.5s** sem errar | O **próximo golpe** primário causa **+50% de dano** (mostra "COMBO PRONTO! +50%") |
| **Troca Relâmpago** | Transformar e **atacar em até 0.4s** | O golpe vira **crítico automático (×2)** ("CRÍTICO!") |
| **Combo Elemental** | Chama → trocar para Diamante e atacar em até **2s** | O Estilhaço sai **em chamas** (explode ao acertar com +50% do dano) |

O contador de combo aparece no HUD (x2, x3...) e o bônus do Golpe Triplo
expira se o jogador demorar para usar.

---

## 11. Progressão — XP, níveis e upgrades

- XP necessária por nível: **100 + (nível−1) × 50** (100, 150, 200, ...).
- Ao subir de nível, o jogo pausa e oferece **3 upgrades aleatórios** (teclas
  1/2/3). O catálogo tem 12 opções:

| Upgrade | Efeito |
|---|---|
| Vida Máx +2 | +2 de vida máxima |
| Vida Máx +30% | Vida máxima +30% (cura a diferença) |
| Velocidade +20% | Anda 20% mais rápido |
| Dano Base +1 | Todas as armas +1 de dano |
| Dano +25% / Dano +50% | Multiplicador de dano (+25% / +50%, acumula) |
| Cadência +25% / Cooldowns -10% | Ataca mais rápido (mín. 10%) |
| Explosão da Chama +40 | Bola de Fogo explode em área maior |
| Pancada Mais Larga +50 | Pancada do Quatro Braços fica mais larga |
| Cadeia do XLR8 +1 Alvo | Ataque em Cadeia atinge +1 inimigo |
| Campo de Cristais +2s | Cristais do Diamante duram mais |

---

## 12. Mundo e câmera

### Mundo
- Mundo de **3000×2000 px**, janela de **1024×768** a **60 FPS**.
- Fundo: gradiente roxo + **400 estrelas com parallax** de profundidade.

### Câmera com inclinação (pseudo-3D)
- Segue o jogador com suavidade (lerp exponencial).
- **Trava nos limites do mundo**: a borda do mapa é a borda da tela — a câmera
  nunca "vaza" para fora do mundo (correção das bordas).
- **Inclina para o mouse**: o mundo é desenhado em um surface maior, girado até
  **3.5°** e levemente "achatado" na vertical (pitch 0.03) conforme o cursor
  fica perto das bordas da tela.
- **Pan oposto à mira** (até 10 px) dá a sensação de "a câmera se inclina para
  onde você aponta".
- **Tremor de tela** (screen shake) em explosões, pancadas, fusões e power-ups
  lendários.
- **Mira precisa**: a conversão mouse→mundo **desfaz a rotação/inclinação**, então
  o cursor continua batendo exatamente no que aparece na tela, mesmo com a
  câmera inclinada ou tremendo.

---

## 13. HUD (interface durante o jogo)

| Elemento | Posição | Conteúdo |
|---|---|---|
| **Vida + XP + Energia** | Canto sup. esquerdo | 3 barras empilhadas com ícone de coração; o texto mostra `vida/máx`, `Nível N` e `Energia N%` |
| **Escudos Petrossápien** | Abaixo da energia | Ícone de escudo + xN quando há cargas |
| **Cronômetro** | Topo central | Tempo de sobrevivência `MM:SS` |
| **Abates** | Canto sup. direito | Contador de inimigos derrotados |
| **Combo** | Abaixo do cronômetro | x2, x3... ou "COMBO PRONTO! +50%" |
| **Faixa do Omnitrix** | Centro, y=130 | Os **5 retratos** dos aliens; o atual tem anel **verde**, o escolhido tem contorno **dourado**, os demais ficam escurecidos |
| **Dica central** | Abaixo da faixa | "Forma: X → Y (ENTER p/ transformar)" ou o lembrete de como escolher |
| **Barra Prisma** | Canto sup. direito | Barra de fusão; dourada quando cheia; abaixo mostra o parceiro sorteado ("FUSÃO: + X") ou o tempo restante da fusão ativa |
| **Power-ups ativos** | Coluna à direita | Ícone + **nome** + círculo de contagem regressiva na cor da raridade |
| **Poderes do alien** | Inferior central | 2 caixas: "Clique: [poder]" e "X: [especial]" com barrinha de recarga; com fusão mostra "Fusão: +Alien (Traço)"; com Minigun/Punhos mostra o substituído |
| **Crosshair** | No cursor | Mira com círculo e 4 traços girando, na cor do poder atual |
| **Banners arcade** | Centro da tela | Anúncios grandes ("MINIGUN DO SUMO SACERDOTE!") com zoom-in, cor da raridade e sombra |

### Telas
- **Título**: controles, seleção de modo e melhores marcas da Arena.
- **Level Up**: 3 cartas de upgrade numeradas sobre um fundo escurecido.
- **Game Over**: tempo, abates, nível, "★ NOVO RECORDE! ★" quando aplicável, top 5 de recordes e "R para reiniciar".
- **Pausa**: ESC continua.

---

## 14. Efeitos visuais

| Efeito | Onde aparece | Descrição |
|---|---|---|
| **Explosão animada** | Supernova, Bola de Fogo, bombas, pisão do Way Big | Sprite sheet de 24 quadros (Ville Seppanen, CC-BY), redimensionada pelo raio, com anel colorido por cima |
| **Onda de pressão cinética** | Pancada no Chão, pouso do Super Pulmão, fusão Força Bruta | Efeito **100% procedural** de choque de força: anel irregular de 18 pontos expandindo + raios de velocidade radiais + poeira/detritos cinza e clarão branco — sem fogo |
| **Partículas** | Acertos, mortes, dash, transformações | Sistema de pequenas bolinhas com resistência do ar e encolhimento |
| **Textos flutuantes** | Dano, CRÍTICO!, COMBO +50%, BLOQUEADO! | Números que sobem e somem (vermelho no jogador, branco nos inimigos, dourado nos críticos) |
| **Raio da Cadeia** | XLR8 | Relâmpago amarelo esticado entre os alvos (sprite CC-BY 4.0) |
| **Bola de Fogo animada** | Chama | 3 quadros de chama no voo |
| **Cristais** | Diamante | Estilhaço girando no ar + cristal orbitando no Campo de Cristais |
| **Aura de fusão** | Durante fusão | Anel pulsante na cor do traço + fragmentos orbitando + anéis que "respiram" |
| **Anel de transformação** | ENTER / fusão | Onda circular verde (ou da cor do traço) + explosão de partículas |
| **Arco do soco / retângulo da pancada** | Ben / Quatro Braços | Formas translúcidas na direção da mira (a cor muda com o traço da fusão) |

### Sprites (assets)
- **Jogador**: sprites próprios por alien (ben, chama, diamante, quatro_bracos,
  xlr8), girando para a mira.
- **Inimigos**: sprites próprios por tipo (cavaleiro_n1/2/3, caveira,
  cavaleiro_magma).
- **UI**: coração, escudo, baú, cristal, ícones de power-up.
- **Efeitos**: fireball, explosão, cristal, raio, orbes da minigun.
- Todos os assets são **tolerantes a falhas**: se faltar um arquivo, o jogo
  usa placeholders coloridos e nunca quebra.

---

## 15. Áudio

### Música ambiente (alterna pelo momento do jogo)
| Humor | Quando toca |
|---|---|
| intro | Tela inicial |
| suspense | Sem inimigos na tela |
| combat | Há inimigos (1ª fase) |
| phase2 | A partir de **50 abates** (2ª fase) |

### Efeitos sonoros
transformação, seleção de alien, soco, pancada, pouso, bola de fogo, supernova,
estilhaço, campo de cristais, turbo, acerto, dash e level up — todos com
substituto silencioso se o arquivo não existir.

---

## 16. Recordes

- O jogo salva as **5 melhores marcas** da Arena em `scores.json` (tempo +
  abates), ordenadas por tempo.
- Aparecem na tela inicial e no Game Over; quando a partida atual entra no top
  da lista, o jogo mostra "★ NOVO RECORDE! ★".

---

## 17. Arquitetura e organização

O projeto é **data-driven**: quase tudo é descrito como **dados** (nome, dano,
cooldown, duração, raridade, peso) em um único arquivo de configuração, e a
lógica apenas lê esses dados. Isso facilita balancear sem mexer em código.

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada (`python main.py` ou `--smoke` para teste) |
| `game/settings.py` | **Todos os dados do jogo**: janela, cores, jogador, aliens, inimigos, power-ups, fusões, combos, modos |
| `game/game.py` | O loop principal, estados de tela, eventos, transformação, fusão, dash, nível |
| `game/world.py` | O "mundo vivo": spawn, ataques de todos os aliens, projéteis, colisões, drops, baús, clones, power-ups, efeitos |
| `game/entities.py` | Jogador (movimento, energia, fusões, combos, power-ups) e inimigos |
| `game/camera.py` | Câmera inclinada pseudo-3D + mira precisa + tremor |
| `game/ui.py` | Todo o HUD e telas de menu |
| `game/effects.py` | Partículas e textos flutuantes |
| `game/assets.py` | Carregamento de imagens e sons (tolerante a falhas) |
| `game/audio.py` | Música ambiente por "humor" |

### Exemplo de fluxo de uma partida
1. Tela inicial → escolhe modo (1) → ENTER.
2. Horda surge longe e caminha até o jogador; ele ataca com o alien atual
   apontando com o mouse.
3. Inimigos soltam XP, vida e Núcleos; coletar Núcleos ativa power-ups; XP
   sobe de nível → 3 upgrades.
4. Acertar golpes enche o Prisma → sorteia parceiro → F ativa a fusão com o
   traço emprestado por 8s.
5. A dificuldade escala (vida, velocidade, spawn) até o jogador cair; a partida
   é registrada nos recordes e o R reinicia.

### Teste automático
`python main.py --smoke` roda ~900 frames sem janela, exercitando troca de
alien, ENTER, dash, fusão, todos os power-ups, combos, baús e telas, e imprime
"SMOKE OK" se nada quebrar.
