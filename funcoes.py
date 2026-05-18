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