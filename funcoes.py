"""
funcoes.py — Funções do jogo Turbo Dash (endless runner cartoon).
"""

import pygame
import random
import math


#  CONSTANTES
LARGURA  = 800
ALTURA   = 500
FPS      = 60

RAIA_CIMA   = 180
RAIA_MEIO   = 280
RAIA_BAIXO  = 380
RAIAS = [RAIA_CIMA, RAIA_MEIO, RAIA_BAIXO]

FUNDO_CEU  = (135, 206, 250)
FUNDO_CEU2 = (100, 180, 240)
COR_CHAO   = (100, 200,  80)
COR_CHAO2  = ( 80, 170,  60)
COR_CHAO3  = (160, 220, 100)
BRANCO     = (255, 255, 255)
PRETO      = (  0,   0,   0)
COR_CORPO  = (255, 200,  50)
COR_CORPO2 = (230, 170,  30)
COR_OLHO   = (255, 255, 255)
COR_PUPILA = ( 30,  30,  30)
COR_BOCA   = (200,  60,  60)
CORES_OBS  = [(255,80,80),(255,140,0),(180,80,220),(60,180,255)]
COR_POWER  = (255, 230,  50)
COR_POWER2 = (255, 180,   0)
COR_HUD    = ( 30,  30,  60)
COR_TEXTO  = (255, 255, 255)
COR_DEST   = (255, 220,  50)
COR_VIDA   = (255,  80,  80)

VEL_INICIAL = 5
VEL_MAX     = 18
ACELERACAO  = 0.002
JOG_W = 50
JOG_H = 54


#  ESTADO

def criar_estado(recorde_anterior=0):
    """
    Cria e retorna o estado inicial do jogo.

    Parâmetros:
        recorde_anterior (int): melhor pontuação das partidas anteriores.

    Retorna:
        dict com todos os dados do jogo: jogador, obstáculos, power-ups,
        pontuação, vidas, velocidade, cenário e flags de controle.
    """
    return {
        "jogador": {
            "raia": 1, "y": float(RAIAS[1]), "y_alvo": float(RAIAS[1]),
            "pulando": False, "frame_anim": 0,
        },
        "obstaculos": [], "powerups": [], "particulas": [],
        "nuvens": _criar_nuvens(),
        "pontuacao": 0, "recorde": recorde_anterior,
        "vidas": 3, "velocidade": float(VEL_INICIAL),
        "timer_obs": 60, "timer_pow": 300,
        "chao_offset": 0, "invencivel": 0,
        "game_over": False, "frames": 0,
    }


def _criar_nuvens():
    """Gera lista de nuvens com posições e velocidades aleatórias."""
    return [{"x": random.randint(0, 800), "y": random.randint(20, 120),
             "w": random.randint(80, 160), "vel": random.uniform(0.3, 0.8)}
            for _ in range(6)]


#  JOGADOR

def mover_jogador(estado, direcao):
    """
    Move o jogador para a raia acima (-1) ou abaixo (+1).

    Só age se o jogador não está em transição e a raia destino existe.

    Parâmetros:
        estado (dict): estado atual do jogo.
        direcao (int): -1 para cima, +1 para baixo.
    """
    jog  = estado["jogador"]
    nova = jog["raia"] + direcao
    if 0 <= nova <= 2 and abs(jog["y"] - jog["y_alvo"]) < 5:
        jog["raia"]   = nova
        jog["y_alvo"] = float(RAIAS[nova])
        jog["pulando"] = True


def atualizar_jogador(estado):
    """
    Interpola suavemente a posição vertical do jogador até o alvo.

    Usa fator 0.25 por frame para movimento fluido sem overshoot.

    Parâmetros:
        estado (dict): estado atual (modificado in-place).
    """
    jog = estado["jogador"]
    dy  = jog["y_alvo"] - jog["y"]
    if abs(dy) < 2:
        jog["y"] = jog["y_alvo"]
        jog["pulando"] = False
    else:
        jog["y"] += dy * 0.25
    jog["frame_anim"] = (jog["frame_anim"] + 1) % 20


#  OBSTÁCULOS

def atualizar_obstaculos(estado):
    """
    Gera novos obstáculos e move os existentes para a esquerda.

    Nunca bloqueia todas as 3 raias ao mesmo tempo — garante que
    sempre existe pelo menos uma raia livre para o jogador escapar.
    Remove obstáculos que saíram da tela.

    Parâmetros:
        estado (dict): estado atual (modificado in-place).
    """
    vel = estado["velocidade"]
    estado["timer_obs"] -= 1

    if estado["timer_obs"] <= 0:
        base = int(120 - vel * 4)
        estado["timer_obs"] = max(35, base) + random.randint(-10, 10)
        n = random.choices([1, 2], weights=[60, 40])[0]
        for r in random.sample([0, 1, 2], n):
            estado["obstaculos"].append({
                "x": float(LARGURA + 20), "raia": r,
                "tipo": random.randint(0, 3),
                "w": random.randint(30, 55), "h": random.randint(40, 65),
            })
    estado["obstaculos"] = [o for o in
        [{**o, "x": o["x"] - vel} for o in estado["obstaculos"]]
        if o["x"] > -80]

def atualizar_powerups(estado):
    """
    Gera e move power-ups (estrelas que restauram uma vida).

    Aparecem raramente (a cada 300-500 frames) em raia aleatória.

    Parâmetros:
        estado (dict): estado atual (modificado in-place).
    """
    estado["timer_pow"] -= 1
    if estado["timer_pow"] <= 0:
        estado["timer_pow"] = random.randint(300, 500)
        estado["powerups"].append({
            "x": float(LARGURA + 20), "raia": random.randint(0, 2), "angulo": 0,
        })

    estado["powerups"] = [p for p in
        [{**p, "x": p["x"] - estado["velocidade"]*0.8,
          "angulo": (p["angulo"] + 4) % 360}
         for p in estado["powerups"]]
        if p["x"] > -40]
    

#  COLISÕES
def checar_colisoes(estado):
    """
    Verifica colisão do jogador com obstáculos e power-ups.

    Usa hitbox reduzida para tornar o jogo mais justo.
    Após hit: perde vida, 90 frames de invencibilidade e partículas.
    Power-up: +1 vida (máx 5) e partículas douradas.

    Parâmetros:
        estado (dict): estado atual (modificado in-place).

    Retorna:
        str: "hit", "powerup" ou "" indicando o que aconteceu.
    """
    jog = estado["jogador"]
    jx  = 120
    jy  = jog["y"]
    hx1, hx2 = jx + 8, jx + JOG_W - 8
    hy1, hy2 = jy + 6, jy + JOG_H - 4
    resultado = ""

    if estado["invencivel"] > 0:
        estado["invencivel"] -= 1
    else:
        obs_novos = []
        for obs in estado["obstaculos"]:
            ox1 = obs["x"] + 4
            ox2 = obs["x"] + obs["w"] - 4
            oy1 = RAIAS[obs["raia"]] + 4
            oy2 = RAIAS[obs["raia"]] + obs["h"] - 4
            if hx2 > ox1 and hx1 < ox2 and hy2 > oy1 and hy1 < oy2:
                estado["vidas"]     -= 1
                estado["invencivel"] = 90
                _burst(estado, jx + JOG_W//2, jy + JOG_H//2, COR_VIDA)
                resultado = "hit"
                if estado["vidas"] <= 0:
                    estado["game_over"] = True
            else:
                obs_novos.append(obs)
        if resultado == "hit":
            estado["obstaculos"] = obs_novos

    pow_novos = []
    for p in estado["powerups"]:
        px1, px2 = p["x"] + 4, p["x"] + 36
        py1      = RAIAS[p["raia"]] + 4
        py2      = py1 + 36
        if hx2 > px1 and hx1 < px2 and hy2 > py1 and hy1 < py2:
            estado["vidas"] = min(5, estado["vidas"] + 1)
            _burst(estado, p["x"] + 20, RAIAS[p["raia"]] + 20, COR_POWER)
            resultado = "powerup"
        else:
            pow_novos.append(p)
    estado["powerups"] = pow_novos
    return resultado

def _burst(estado, x, y, cor):
    """Cria explosão de partículas em (x, y)."""
    for _ in range(14):
        ang = random.uniform(0, 2 * math.pi)
        vel = random.uniform(2, 7)
        estado["particulas"].append({
            "x": float(x), "y": float(y),
            "vx": math.cos(ang)*vel, "vy": math.sin(ang)*vel,
            "vida": 30, "cor": cor,
        })

def atualizar_particulas(estado):
    """Move partículas com gravidade e remove as expiradas."""
    vivas = []
    for p in estado["particulas"]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.3
        p["vida"] -= 1
        if p["vida"] > 0:
            vivas.append(p)
    estado["particulas"] = vivas

#  ATUALIZAÇÃO GERAL
def atualizar_estado(estado):
    """
    Avança o jogo um frame: velocidade, pontuação, todos os sistemas.

    Não faz nada se game_over for True.

    Parâmetros:
        estado (dict): estado atual (modificado in-place).
    """
    if estado["game_over"]:
        return
    estado["frames"]    += 1
    estado["pontuacao"] += 1
    estado["velocidade"] = min(VEL_MAX, VEL_INICIAL + estado["frames"] * ACELERACAO)
    estado["chao_offset"] = (estado["chao_offset"] + estado["velocidade"]) % 80
    for n in estado["nuvens"]:
        n["x"] -= n["vel"]
        if n["x"] < -n["w"] - 20:
            n["x"] = LARGURA + 20
            n["y"] = random.randint(20, 120)
    atualizar_jogador(estado)
    atualizar_obstaculos(estado)
    atualizar_powerups(estado)
    atualizar_particulas(estado)
    if estado["pontuacao"] > estado["recorde"]:
        estado["recorde"] = estado["pontuacao"]


#  DESENHO DO JOGO
def _nuvem(tela, x, y, w):
    """Desenha nuvem cartoon com três elipses sobrepostas."""
    h = w // 3
    pygame.draw.ellipse(tela, BRANCO, (x,        y+h//2,  w,    h))
    pygame.draw.ellipse(tela, BRANCO, (x+w//4,   y,       w//2, h))
    pygame.draw.ellipse(tela, BRANCO, (x+w//2,   y+h//3,  w//3, h//2))


def desenhar_fundo(tela, estado):
    """Preenche céu e desenha nuvens animadas."""
    tela.fill(FUNDO_CEU)
    pygame.draw.rect(tela, FUNDO_CEU2, (0, 0, LARGURA, 140))
    for n in estado["nuvens"]:
        _nuvem(tela, int(n["x"]), int(n["y"]), n["w"])


def desenhar_chao(tela, estado):
    """Desenha as 3 raias do chão com listras de movimento animadas."""
    off = int(estado["chao_offset"])
    for i, ry in enumerate(RAIAS):
        base = ry + JOG_H - 10
        cor1 = COR_CHAO if i % 2 == 0 else COR_CHAO2
        cor2 = COR_CHAO2 if i % 2 == 0 else COR_CHAO
        pygame.draw.rect(tela, cor1, (0, base, LARGURA, 55))
        x = -off
        while x < LARGURA:
            pygame.draw.rect(tela, cor2, (int(x), base+4, 40, 47))
            x += 80
        pygame.draw.rect(tela, COR_CHAO3, (0, base, LARGURA, 4))


def desenhar_jogador(tela, estado):
    """Desenha personagem com animação de corrida; pisca se invencível."""
    jog = estado["jogador"]
    if estado["invencivel"] > 0 and (estado["invencivel"] // 6) % 2 == 0:
        return
    x  = 120
    y  = int(jog["y"])
    fa = jog["frame_anim"]
    perna = int(math.sin(fa * math.pi / 10) * 10)
    # Sombra
    pygame.draw.ellipse(tela, (80,160,60), (x+5, y+JOG_H-4, JOG_W-10, 10))
    # Pernas
    pygame.draw.rect(tela, COR_CORPO2, (x+12, y+38, 10, 16+perna))
    pygame.draw.rect(tela, COR_CORPO2, (x+28, y+38, 10, 16-perna))
    # Corpo
    pygame.draw.ellipse(tela, COR_CORPO,  (x+4,  y+12, JOG_W-8, 32))
    pygame.draw.ellipse(tela, COR_CORPO2, (x+4,  y+12, JOG_W-8, 32), 2)
    # Cabeça
    pygame.draw.circle(tela, COR_CORPO,  (x+JOG_W//2, y+14), 17)
    pygame.draw.circle(tela, COR_CORPO2, (x+JOG_W//2, y+14), 17, 2)
    # Olhos
    pygame.draw.circle(tela, COR_OLHO,   (x+20, y+10), 6)
    pygame.draw.circle(tela, COR_OLHO,   (x+34, y+10), 6)
    pygame.draw.circle(tela, COR_PUPILA, (x+22, y+10), 3)
    pygame.draw.circle(tela, COR_PUPILA, (x+36, y+10), 3)
    # Boca
    if estado["invencivel"] > 0:
        pygame.draw.circle(tela, COR_BOCA, (x+JOG_W//2, y+20), 4)
    else:
        pygame.draw.arc(tela, COR_BOCA,
                        pygame.Rect(x+16, y+16, 18, 8), math.pi, 2*math.pi, 2)
    # Braços
    bx = int(math.sin(fa * math.pi / 10) * 8)
    pygame.draw.line(tela, COR_CORPO2, (x+8,       y+22), (x,       y+30+bx), 5)
    pygame.draw.line(tela, COR_CORPO2, (x+JOG_W-8, y+22), (x+JOG_W, y+30-bx), 5)


def desenhar_obstaculo(tela, obs):
    """Desenha obstáculo cartoon arredondado com cara de X."""
    x  = int(obs["x"])
    y  = RAIAS[obs["raia"]]
    w, h = obs["w"], obs["h"]
    cor    = CORES_OBS[obs["tipo"]]
    escura = tuple(max(0, c-60) for c in cor)
    clara  = tuple(min(255, c+60) for c in cor)
    pygame.draw.rect(tela, cor,    (x, y, w, h), border_radius=8)
    pygame.draw.rect(tela, escura, (x, y, w, h), 3, border_radius=8)
    pygame.draw.rect(tela, clara,  (x+5, y+5, w//3, 6), border_radius=3)
    cx, cy = x+w//2, y+h//2-4
    pygame.draw.line(tela, escura, (cx-10, cy-6), (cx-4,  cy),   3)
    pygame.draw.line(tela, escura, (cx-4,  cy-6), (cx-10, cy),   3)
    pygame.draw.line(tela, escura, (cx+4,  cy-6), (cx+10, cy),   3)
    pygame.draw.line(tela, escura, (cx+10, cy-6), (cx+4,  cy),   3)
    pygame.draw.arc(tela, escura, pygame.Rect(cx-8, cy+2, 16, 8), 0, math.pi, 2)


def desenhar_powerup(tela, p, frames):
    """Desenha estrela giratória e pulsante de power-up."""
    x  = int(p["x"])
    y  = RAIAS[p["raia"]] + 8
    cx, cy = x+20, y+20
    ang = math.radians(p["angulo"])
    pts = []
    for i in range(10):
        r = 18 if i % 2 == 0 else 8
        a = ang + i * math.pi / 5
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    pulso = int(4 * math.sin(frames * 0.1))
    pygame.draw.circle(tela, COR_POWER2, (cx, cy), 22+pulso)
    pygame.draw.polygon(tela, COR_POWER, pts)
    pygame.draw.polygon(tela, BRANCO, pts, 2)

def _coracao(tela, x, y, cor):
    """Desenha um coração simples para o HUD de vidas."""
    pygame.draw.circle(tela, cor, (x+6,  y+6),  6)
    pygame.draw.circle(tela, cor, (x+16, y+6),  6)
    pygame.draw.polygon(tela, cor, [(x, y+9), (x+11, y+22), (x+22, y+9)])

def desenhar_hud(tela, estado, fonte_grande, fonte_media, fonte_pequena):
    """Desenha pontuação, recorde, vidas e barra de velocidade."""
    pygame.draw.rect(tela, COR_HUD, (0, 0, LARGURA, 42))
    pygame.draw.rect(tela, (60,60,100), (0, 42, LARGURA, 2))
    s = fonte_grande.render(f"{estado['pontuacao']:06d}", True, COR_DEST)
    tela.blit(s, (LARGURA//2 - s.get_width()//2, 4))
    sr = fonte_pequena.render(f"recorde: {estado['recorde']:06d}", True, (180,200,255))
    tela.blit(sr, (LARGURA//2 - sr.get_width()//2, 28))
    for i in range(5):
        _coracao(tela, 14+i*32, 8, COR_VIDA if i < estado["vidas"] else (70,70,90))
    sv = fonte_pequena.render("VELOCIDADE", True, (180,200,255))
    tela.blit(sv, (LARGURA-130, 6))
    pct = (estado["velocidade"]-VEL_INICIAL) / (VEL_MAX-VEL_INICIAL)
    pygame.draw.rect(tela, (60,60,100),  (LARGURA-130, 20, 120, 10), border_radius=5)
    pygame.draw.rect(tela, COR_DEST,     (LARGURA-130, 20, int(120*pct), 10), border_radius=5)


def desenhar_jogo(tela, estado, fonte_grande, fonte_media, fonte_pequena):
    """Desenha o frame completo: fundo, chão, objetos, jogador e HUD."""
    desenhar_fundo(tela, estado)
    desenhar_chao(tela, estado)
    for p in estado["powerups"]:
        desenhar_powerup(tela, p, estado["frames"])
    for obs in estado["obstaculos"]:
        desenhar_obstaculo(tela, obs)
    for p in estado["particulas"]:
        pygame.draw.circle(tela, p["cor"], (int(p["x"]), int(p["y"])), 4)
    desenhar_jogador(tela, estado)
    desenhar_hud(tela, estado, fonte_grande, fonte_media, fonte_pequena)


def desenhar_menu(tela, recorde, fonte_titulo, fonte_grande, fonte_media, fonte_pequena):
    """Desenha tela de menu com título, instruções e recorde."""
    tela.fill(FUNDO_CEU)
    pygame.draw.rect(tela, FUNDO_CEU2, (0, 0, LARGURA, 140))
    for x, y, w in [(80,30,140),(350,50,100),(600,25,130)]:
        _nuvem(tela, x, y, w)
    pygame.draw.rect(tela, COR_CHAO,  (0, ALTURA-80, LARGURA, 80))
    pygame.draw.rect(tela, COR_CHAO3, (0, ALTURA-80, LARGURA, 6))
    s1 = fonte_titulo.render("TURBO DASH", True, PRETO)
    s2 = fonte_titulo.render("TURBO DASH", True, COR_DEST)
    tela.blit(s1, (LARGURA//2 - s2.get_width()//2+3, 103))
    tela.blit(s2, (LARGURA//2 - s2.get_width()//2,   100))
    for txt, y in [
        ("Use CIMA e BAIXO para trocar de raia!", 195),
        ("Desvie dos obstaculos coloridos!", 225),
        ("Pegue as estrelas para ganhar vida extra!", 255),
    ]:
        s = fonte_media.render(txt, True, PRETO)
        tela.blit(s, (LARGURA//2 - s.get_width()//2, y))
    if recorde > 0:
        sr = fonte_media.render(f"Recorde: {recorde:06d}", True, COR_VIDA)
        tela.blit(sr, (LARGURA//2 - sr.get_width()//2, 295))
    se = fonte_grande.render("Pressione ENTER para jogar", True, PRETO)
    se2 = fonte_grande.render("Pressione ENTER para jogar", True, COR_DEST)
    tela.blit(se,  (LARGURA//2 - se.get_width()//2+2, 342))
    tela.blit(se2, (LARGURA//2 - se.get_width()//2,   340))
