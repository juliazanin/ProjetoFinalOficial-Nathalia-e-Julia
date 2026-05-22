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