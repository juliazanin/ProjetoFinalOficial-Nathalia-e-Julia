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



while rodando:

    dt = clock.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            tecla = evento.key

            if tela_atual == "menu":
                if tecla in (pygame.K_RETURN, pygame.K_SPACE):
                    estado      = criar_estado(recorde_geral)
                    tela_atual  = "jogando"
                    timer_passo = 0
                    timer_menu  = 0
                    parar_musica()
                    tocar_musica(MUSICA_JOGO)
                elif tecla == pygame.K_ESCAPE:
                    rodando = False

            elif tela_atual == "jogando":
                if tecla in (pygame.K_UP, pygame.K_w):
                    mover_jogador(estado, -1)
                    tocar_som(sons, "pulo")
                elif tecla in (pygame.K_DOWN, pygame.K_s):
                    mover_jogador(estado, 1)
                    tocar_som(sons, "pulo")
                elif tecla in (pygame.K_p, pygame.K_ESCAPE):
                    tela_atual = "pausa"
                    parar_musica()

            elif tela_atual == "pausa":
                if tecla in (pygame.K_p, pygame.K_ESCAPE):
                    tela_atual = "jogando"
                    tocar_musica(MUSICA_JOGO)
                elif tecla == pygame.K_m:
                    tela_atual = "menu"
                    parar_musica()
                    tocar_musica(MUSICA_MENU)

            elif tela_atual == "gameover":
                if tecla in (pygame.K_RETURN, pygame.K_SPACE):
                    estado      = criar_estado(recorde_geral)
                    tela_atual  = "jogando"
                    timer_passo = 0
                    timer_menu  = 0
                    parar_musica()
                    tocar_musica(MUSICA_JOGO)
                elif tecla == pygame.K_ESCAPE:
                    tela_atual = "menu"
                    timer_menu = 0
                    parar_musica()
                    tocar_musica(MUSICA_MENU)