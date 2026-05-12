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