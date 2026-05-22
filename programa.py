"""
programa.py — Loop principal do Turbo Dash.
Execute: python programa.py
Dependencias: pip install pygame numpy

Musicas necessarias na mesma pasta:
    musica_menu.ogg
    musica_jogo.mp3
"""

import pygame
import os
from funcoes import (
    LARGURA, ALTURA, FPS,
    criar_estado, atualizar_estado,
    mover_jogador, checar_colisoes,
    criar_sons, tocar_som,
    desenhar_menu, desenhar_jogo, desenhar_game_over, desenhar_pausa,
)


pygame.init()
pygame.mixer.init()

tela  = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Turbo Dash")
clock = pygame.time.Clock()

fonte_titulo  = pygame.font.SysFont("consolas", 52, bold=True)
fonte_grande  = pygame.font.SysFont("consolas", 24, bold=True)
fonte_media   = pygame.font.SysFont("consolas", 18)
fonte_pequena = pygame.font.SysFont("consolas", 14)

sons = criar_sons()


pasta = os.path.dirname(os.path.abspath(_file_))
MUSICA_MENU = os.path.join(pasta, "musica_menu.ogg")
MUSICA_JOGO = os.path.join(pasta, "musica_jogo.mp3")

def tocar_musica(arquivo):
    pygame.mixer.music.load(arquivo)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def parar_musica():
    pygame.mixer.music.stop()



estado        = None
recorde_geral = 0
INTERVALO_PASSO = 18
timer_passo     = 0
DELAY_MENU      = 2200
timer_menu      = 0

tela_atual = "menu"
rodando    = True
tocar_musica(MUSICA_MENU)
