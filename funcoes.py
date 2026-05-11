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