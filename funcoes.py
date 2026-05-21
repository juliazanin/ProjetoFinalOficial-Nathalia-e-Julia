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
    return [{"x": random.randint(0, 800), "y": random.randint(20, 120),
             "w": random.randint(80, 160), "vel": random.uniform(0.3, 0.8)}
            for _ in range(6)]


#  JOGADOR

def mover_jogador(estado, direcao):
    jog  = estado["jogador"]
    nova = jog["raia"] + direcao
    if 0 <= nova <= 2 and abs(jog["y"] - jog["y_alvo"]) < 5:
        jog["raia"]   = nova
        jog["y_alvo"] = float(RAIAS[nova])
        jog["pulando"] = True


def atualizar_jogador(estado):
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
    for _ in range(14):
        ang = random.uniform(0, 2 * math.pi)
        vel = random.uniform(2, 7)
        estado["particulas"].append({
            "x": float(x), "y": float(y),
            "vx": math.cos(ang)*vel, "vy": math.sin(ang)*vel,
            "vida": 30, "cor": cor,
        })


def atualizar_particulas(estado):
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


#  DESENHO

def _nuvem(tela, x, y, w):
    h = w // 3
    pygame.draw.ellipse(tela, BRANCO, (x,        y+h//2,  w,    h))
    pygame.draw.ellipse(tela, BRANCO, (x+w//4,   y,       w//2, h))
    pygame.draw.ellipse(tela, BRANCO, (x+w//2,   y+h//3,  w//3, h//2))


def desenhar_fundo(tela, estado):
    tela.fill(FUNDO_CEU)
    pygame.draw.rect(tela, FUNDO_CEU2, (0, 0, LARGURA, 140))
    for n in estado["nuvens"]:
        _nuvem(tela, int(n["x"]), int(n["y"]), n["w"])


def desenhar_chao(tela, estado):
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
    jog = estado["jogador"]
    if estado["invencivel"] > 0 and (estado["invencivel"] // 6) % 2 == 0:
        return
    x  = 120
    y  = int(jog["y"])
    fa = jog["frame_anim"]
    perna = int(math.sin(fa * math.pi / 10) * 10)
    pygame.draw.ellipse(tela, (80,160,60), (x+5, y+JOG_H-4, JOG_W-10, 10))
    pygame.draw.rect(tela, COR_CORPO2, (x+12, y+38, 10, 16+perna))
    pygame.draw.rect(tela, COR_CORPO2, (x+28, y+38, 10, 16-perna))
    pygame.draw.ellipse(tela, COR_CORPO,  (x+4,  y+12, JOG_W-8, 32))
    pygame.draw.ellipse(tela, COR_CORPO2, (x+4,  y+12, JOG_W-8, 32), 2)
    pygame.draw.circle(tela, COR_CORPO,  (x+JOG_W//2, y+14), 17)
    pygame.draw.circle(tela, COR_CORPO2, (x+JOG_W//2, y+14), 17, 2)
    pygame.draw.circle(tela, COR_OLHO,   (x+20, y+10), 6)
    pygame.draw.circle(tela, COR_OLHO,   (x+34, y+10), 6)
    pygame.draw.circle(tela, COR_PUPILA, (x+22, y+10), 3)
    pygame.draw.circle(tela, COR_PUPILA, (x+36, y+10), 3)
    if estado["invencivel"] > 0:
        pygame.draw.circle(tela, COR_BOCA, (x+JOG_W//2, y+20), 4)
    else:
        pygame.draw.arc(tela, COR_BOCA,
                        pygame.Rect(x+16, y+16, 18, 8), math.pi, 2*math.pi, 2)
    bx = int(math.sin(fa * math.pi / 10) * 8)
    pygame.draw.line(tela, COR_CORPO2, (x+8,       y+22), (x,       y+30+bx), 5)
    pygame.draw.line(tela, COR_CORPO2, (x+JOG_W-8, y+22), (x+JOG_W, y+30-bx), 5)


def desenhar_obstaculo(tela, obs):
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
    pygame.draw.circle(tela, cor, (x+6,  y+6),  6)
    pygame.draw.circle(tela, cor, (x+16, y+6),  6)
    pygame.draw.polygon(tela, cor, [(x, y+9), (x+11, y+22), (x+22, y+9)])


def desenhar_hud(tela, estado, fonte_grande, fonte_media, fonte_pequena):
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


def desenhar_game_over(tela, estado, fonte_titulo, fonte_grande, fonte_media):
    ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    ov.fill((20, 10, 40, 210))
    tela.blit(ov, (0, 0))
    cy = ALTURA // 2
    for txt, cor, dy in [
        ("GAME OVER",                          COR_VIDA,       -100),
        (f"Pontuacao: {estado['pontuacao']:06d}", BRANCO,       -20),
        (f"Recorde:   {estado['recorde']:06d}",  COR_DEST,      30),
        ("ENTER: jogar de novo   ESC: menu",   (180,200,255),   90),
    ]:
        f = fonte_titulo if dy == -100 else (fonte_grande if dy != 90 else fonte_media)
        s = f.render(txt, True, cor)
        tela.blit(s, (LARGURA//2 - s.get_width()//2, cy+dy))


def desenhar_pausa(tela, fonte_titulo, fonte_media):
    ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    ov.fill((20, 10, 40, 180))
    tela.blit(ov, (0, 0))
    s1 = fonte_titulo.render("PAUSADO", True, COR_DEST)
    s2 = fonte_media.render("P ou ESC: continuar   M: menu", True, BRANCO)
    tela.blit(s1, (LARGURA//2 - s1.get_width()//2, ALTURA//2 - 50))
    tela.blit(s2, (LARGURA//2 - s2.get_width()//2, ALTURA//2 + 20))


#  SONS E MÚSICAS

def criar_sons():
    sons = {}
    try:
        import numpy as np
        taxa = 44100

        def senoide(freq, dur, vol=1.0, envelope=None):
            n = int(taxa * dur)
            t = np.linspace(0, dur, n, endpoint=False)
            w = np.sin(2 * math.pi * freq * t)
            if envelope is not None:
                w *= envelope(t, dur)
            return w * vol

        def env_decay(t, dur, velocidade=6):
            return np.exp(-velocidade * t / dur)

        def env_adsr(t, dur, a=0.05, d=0.1, s=0.7, r=0.2):
            n = len(t)
            na = int(a * n); nd = int(d * n); nr = int(r * n)
            ns = n - na - nd - nr
            atk = np.linspace(0, 1,   max(1, na))
            dec = np.linspace(1, s,   max(1, nd))
            sus = np.full(max(1, ns), s)
            rel = np.linspace(s, 0,   max(1, nr))
            return np.concatenate([atk, dec, sus, rel])[:n]

        def fade(w, taxa_local, ms_in=8, ms_out=8):
            fi = int(taxa_local * ms_in  / 1000)
            fo = int(taxa_local * ms_out / 1000)
            if fi > 0 and len(w) > fi:
                w[:fi] *= np.linspace(0, 1, fi)
            if fo > 0 and len(w) > fo:
                w[-fo:] *= np.linspace(1, 0, fo)
            return w

        def to_sound(w, vol=0.35):
            w = fade(w, taxa)
            w = np.clip(w * vol * 32767, -32767, 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack([w, w]))

        def concat(*partes):
            return np.concatenate(partes)

        def nota(freq, dur, forma="tri", vol=1.0):
            if forma == "sin":
                return senoide(freq, dur, vol, env_adsr)
            elif forma == "sq":
                n = int(taxa * dur)
                t = np.linspace(0, dur, n, endpoint=False)
                w = np.sign(np.sin(2 * math.pi * freq * t))
                env = env_adsr(t, dur)[:n]
                return w * env * vol
            else:
                n = int(taxa * dur)
                t = np.linspace(0, dur, n, endpoint=False)
                w = (2/math.pi) * np.arcsin(np.sin(2*math.pi*freq*t))
                env = env_adsr(t, dur)[:n]
                return w * env * vol

        def silencio(dur):
            return np.zeros(int(taxa * dur))

        DO4=261.63; RE4=293.66; MI4=329.63; FA4=349.23
        SOL4=392.0; LA4=440.0; SI4=493.88
        DO5=523.25; RE5=587.33; MI5=659.25; FA5=698.46
        SOL5=783.99; LA5=880.0
        DO3=130.81; SOL3=196.0; MI3=164.81; LA3=220.0

        # Pulo
        n_pulo = int(taxa * 0.12)
        t_pulo = np.linspace(0, 0.12, n_pulo, endpoint=False)
        freq_sweep = np.linspace(400, 700, n_pulo)
        w_pulo = np.sin(2 * math.pi * np.cumsum(freq_sweep) / taxa)
        w_pulo *= env_decay(t_pulo, 0.12, 8)
        sons["pulo"] = to_sound(w_pulo, 0.22)

        # Hit
        n_hit  = int(taxa * 0.22)
        t_hit  = np.linspace(0, 0.22, n_hit, endpoint=False)
        grave  = np.sin(2 * math.pi * np.linspace(200, 50, n_hit) * t_hit)
        ruido  = np.random.uniform(-1, 1, n_hit)
        w_hit  = grave * 0.7 + ruido * 0.3
        w_hit *= np.exp(-9 * t_hit / 0.22)
        vibr   = np.sin(2 * math.pi * 35 * t_hit) * np.exp(-5 * t_hit / 0.22) * 0.3
        w_hit += vibr
        sons["hit"] = to_sound(w_hit, 0.55)

        # Powerup
        def nota_magica(freq, dur, vol=1.0):
            n   = int(taxa * dur)
            t   = np.linspace(0, dur, n, endpoint=False)
            w   = (np.sin(2*math.pi*freq*t)      * 0.50
                 + np.sin(2*math.pi*freq*2*t)     * 0.25
                 + np.sin(2*math.pi*freq*3*t)     * 0.12
                 + np.sin(2*math.pi*freq*4*t)     * 0.08)
            env = np.exp(-4 * t / dur)
            return w * env * vol

        n_sh   = int(taxa * 0.18)
        t_sh   = np.linspace(0, 0.18, n_sh, endpoint=False)
        shimmer = (np.sin(2*math.pi*1200*t_sh) * 0.3
                 + np.sin(2*math.pi*1500*t_sh) * 0.2
                 + np.sin(2*math.pi*1800*t_sh) * 0.1) * np.exp(-8*t_sh/0.18)
        w_pow = concat(
            nota_magica(DO5,    0.09, 0.6),
            nota_magica(MI5,    0.09, 0.65),
            nota_magica(SOL5,   0.09, 0.70),
            nota_magica(DO5*2,  0.18, 0.80) + shimmer,
        )
        sons["powerup"] = to_sound(w_pow, 0.42)

        # Game over
        def nota_go(freq, dur, vol=1.0):
            n  = int(taxa * dur)
            t  = np.linspace(0, dur, n, endpoint=False)
            w  = (np.sin(2*math.pi*freq*t)     * 0.55
                + np.sin(2*math.pi*freq*2*t)    * 0.20
                + np.sin(2*math.pi*freq*0.5*t)  * 0.15)
            env = np.concatenate([
                np.linspace(0, 1, max(1, int(0.03*n))),
                np.linspace(1, vol, max(1, int(0.10*n))),
                np.full(max(1, n - int(0.13*n) - int(0.20*n)), vol),
                np.linspace(vol, 0, max(1, int(0.20*n))),
            ])[:n]
            return w * env
        w_go = concat(
            nota_go(SOL4, 0.28, 0.80), nota_go(MI4,  0.28, 0.75),
            nota_go(RE4,  0.28, 0.70), silencio(0.06),
            nota_go(DO4,  0.22, 0.75), silencio(0.04),
            nota_go(LA3,  0.55, 0.90),
        )
        sons["gameover"] = to_sound(w_go, 0.48)

        # Recorde
        w_rec = concat(
            nota(DO5,  0.10, "sq", 0.5), nota(MI5,  0.10, "sq", 0.5),
            nota(SOL5, 0.10, "sq", 0.5), nota(DO5,  0.06, "sq", 0.4),
            nota(SOL5, 0.06, "sq", 0.4), nota(DO5*2,0.25, "sq", 0.7),
        )
        sons["recorde"] = to_sound(w_rec, 0.40)

        # Passo
        n_ps = int(taxa * 0.07)
        t_ps = np.linspace(0, 0.07, n_ps, endpoint=False)
        freq_ps = np.linspace(200, 80, n_ps)
        w_ps = np.sin(2 * math.pi * np.cumsum(freq_ps) / taxa)
        w_ps += np.random.uniform(-0.15, 0.15, n_ps)
        w_ps *= env_decay(t_ps, 0.07, 12)
        sons["passo"] = to_sound(w_ps, 0.18)

        # Musica do menu
        bpm_menu = 140
        bat = 60 / bpm_menu
        col = bat / 2
        scol = bat / 4

        def kick(dur=0.12):
            n = int(taxa * dur)
            t = np.linspace(0, dur, n, endpoint=False)
            f = np.linspace(180, 40, n)
            return np.sin(2*math.pi*np.cumsum(f)/taxa) * np.exp(-10*t/dur)

        def snare(dur=0.10):
            n = int(taxa * dur)
            t = np.linspace(0, dur, n, endpoint=False)
            noise = np.random.uniform(-1, 1, n)
            tonal = np.sin(2*math.pi*200*t)
            return (noise * 0.6 + tonal * 0.4) * np.exp(-8*t/dur)

        def hihat(dur=0.05):
            n = int(taxa * dur)
            return np.random.uniform(-1, 1, n) * np.exp(-15*np.linspace(0,1,n))

        mel_menu = concat(
            nota(MI5,  col,  "sq", 0.5), nota(MI5,  scol, "sq", 0.5), nota(FA5, scol, "sq", 0.5),
            nota(SOL5, col,  "sq", 0.6), nota(SOL5, scol, "sq", 0.6), nota(FA5, scol, "sq", 0.5),
            nota(MI5,  col,  "sq", 0.5), nota(RE5,  col,  "sq", 0.5),
            nota(DO5,  col,  "sq", 0.5), nota(DO5,  scol, "sq", 0.5), nota(RE5, scol, "sq", 0.5),
            nota(MI5,  col,  "sq", 0.5), nota(MI5,  scol, "sq", 0.55),nota(RE5, scol, "sq", 0.45),
            nota(RE5,  bat,  "sq", 0.6),
            silencio(scol),
            nota(MI5,  col,  "sq", 0.5), nota(MI5,  scol, "sq", 0.5), nota(FA5, scol, "sq", 0.5),
            nota(SOL5, col,  "sq", 0.6), nota(LA5,  col,  "sq", 0.65),
            nota(SOL5, col,  "sq", 0.6), nota(FA5,  col,  "sq", 0.55),
            nota(MI5,  col,  "sq", 0.5), nota(RE5,  scol, "sq", 0.45),nota(DO5, scol, "sq", 0.5),
            nota(RE5,  col,  "sq", 0.5), nota(MI5,  col,  "sq", 0.55),
            nota(DO5,  bat,  "sq", 0.7),
            silencio(col),
        )

        baixo_notas = [DO3, DO3, SOL3, SOL3, LA3, LA3, MI3, MI3] * 2
        baixo_durs  = [bat] * 16
        bas_menu = concat(*[nota(f, d, "tri", 0.35) for f, d in zip(baixo_notas, baixo_durs)])

        n_loop = len(mel_menu)
        bat_menu = np.zeros(n_loop)
        compasso = int(taxa * bat * 4)
        total_compassos = n_loop // compasso
        for c in range(total_compassos):
            base = c * compasso
            for beat_pos in [0, compasso // 2]:
                p = base + beat_pos
                k = kick()
                end = min(p + len(k), n_loop)
                bat_menu[p:end] += k[:end-p] * 0.5
            for beat_pos in [compasso // 4, 3 * compasso // 4]:
                p = base + beat_pos
                s_arr = snare()
                end = min(p + len(s_arr), n_loop)
                bat_menu[p:end] += s_arr[:end-p] * 0.35
            for i in range(8):
                p = base + int(i * compasso / 8)
                h = hihat()
                end = min(p + len(h), n_loop)
                bat_menu[p:end] += h[:end-p] * 0.15

        L = min(len(mel_menu), len(bas_menu), len(bat_menu))
        mix_menu = mel_menu[:L] * 0.5 + bas_menu[:L] * 0.4 + bat_menu[:L]
        mix_menu = fade(mix_menu, taxa, ms_in=20, ms_out=30)

        import wave, tempfile, os as _os
        def _wav(arr, vol=0.35):
            fd, path = tempfile.mkstemp(suffix=".wav")
            _os.close(fd)
            stereo = np.column_stack([arr, arr])
            data   = np.clip(stereo * vol * 32767, -32767, 32767).astype(np.int16)
            with wave.open(path, "w") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(taxa)
                wf.writeframes(data.tobytes())
            return path

        sons["_wav_menu"] = _wav(mix_menu, 0.40)

    except Exception:
        pass
    return sons


def tocar_som(sons, nome):
    if nome not in sons:
        return
    try:
        pygame.mixer.set_num_channels(8)
        for i in range(1, 8):
            canal = pygame.mixer.Channel(i)
            if not canal.get_busy():
                canal.play(sons[nome])
                return
        pygame.mixer.Channel(7).play(sons[nome])
    except Exception:
        pass