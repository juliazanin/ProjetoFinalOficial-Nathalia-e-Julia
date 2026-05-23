# Turbo Dash
Jogo final de Design de Software — Nathalia Sena e Julia Zanin | Insper 2026/1

---
## Vídeo demonstração
https://youtu.be/VdyC93r9iBg


---
## Sobre o jogo

Turbo Dash é um endless runner 2D com visual cartoon e colorido. O jogador controla um personagem que corre automaticamente em 3 raias e precisa desviar de obstáculos coloridos que aparecem em velocidade crescente. Para trocar de raia, basta pressionar as setas para cima ou para baixo.

O jogo conta com 5 vidas representadas por corações no HUD, estrelas espalhadas pelo cenário que recuperam uma vida ao serem coletadas, efeitos de partículas ao tomar dano ou pegar itens, animação de corrida do personagem, barra de velocidade e sistema de recorde. A dificuldade aumenta progressivamente conforme a pontuação cresce, tornando o jogo cada vez mais desafiador.

---

## Como instalar e rodar
### 1. Instale o Python 3.12
Baixe em: https://www.python.org/downloads/

> Na instalação, marque a opção **"Add Python to PATH"**

### 2. Clone o repositório
```bash
git clone https://github.com/juliazanin/ProjetoFinalOficial-Nathalia-e-Julia.git
cd ProjetoFinalOficial-Nathalia-e-Julia
```

### 3. Crie e ative o ambiente virtual
```bash
py -3.12 -m venv .venv312
.venv312\Scripts\Activate.ps1
```

> Se aparecer erro de permissão no PowerShell, rode antes:
> ```
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```

### 4. Instale as dependências
```bash
pip install pygame numpy
```

### 5. Execute o jogo
```bash
python programa.py
```

---
## Controles

| Tecla | Ação |
|-------|------|
| ↑ ou W | Mover para raia de cima |
| ↓ ou S | Mover para raia de baixo |
| ENTER ou ESPAÇO | Iniciar / Reiniciar |
| P ou ESC | Pausar |
| M | Voltar ao menu (na pausa) |

---
## Uso de Inteligência Artificial

Este projeto utilizou ferramentas de IA (Claude - Anthropic e ChatGPT - disponibilizado pela conta Insper) como apoio no desenvolvimento. O histórico completo de uso está documentado em: [link para o documento]