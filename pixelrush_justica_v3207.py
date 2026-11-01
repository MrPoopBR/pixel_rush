# -*- coding: utf-8 -*-
"""Plano H v3.207 — simulador de justiça somente para QA (NÃO importado no jogo).

Usa o DiretorAutorais real, o AuditorVariedade/AuditorJustica reais e, na
sondagem opcional, o Jogador e os obstáculos reais do script do jogo.
Não agenda spawn, corrige percurso, mexe em física ou roda no loop de produção.
As sondagens geométricas são de encontros ISOLADOS; não certificam a corrida,
perigos com fases, clima, power-ups ou a habilidade humana de reagir.
"""
import random
from collections import Counter

from pixelrush_percursos_v3140 import DiretorSequencias
from pixelrush_percursos_v3191 import AuditorVariedade
from pixelrush_sequencias_v3206 import DiretorAutorais, ACOES, RESPIROS, CHOQUES, FRASES

VALIDOS = frozenset(ACOES | RESPIROS)


def diretores():
    return AuditorVariedade(DiretorSequencias()), DiretorAutorais(AuditorVariedade(DiretorSequencias()))


def auditar_sequencias(biomas, sementes=(7, 41, 207), encontros=2000):
    """Testa decisão real de cada diretor sob 7 biomas e transições.

    Entradas não alteram RNG global; sementes mudam apenas a distância/bioma
    requisitados ao diretor, sem simular o RNG do gerador clássico (None).
    """
    resultados = []
    alertas = []
    total = Counter()
    assert all(b in FRASES for b in biomas)
    for bioma_alvo in tuple(biomas) + ('transicoes',):
        for seed in sementes:
            rng = random.Random(seed)
            antigo, novo = diretores()
            ultimo = None
            metros = 15
            contagem = Counter()
            sequencia_risco = 0
            max_sequencia_risco = 0
            for i in range(encontros):
                bioma = (biomas[(i // rng.randrange(9, 65)) % len(biomas)]
                         if bioma_alvo == 'transicoes' else bioma_alvo)
                metros += rng.randint(10, 47)
                a = antigo.proxima(metros, bioma)
                b = novo.proxima(metros, bioma)
                contagem['encontros'] += 1
                contagem['riscos_antes'] += int(a in ACOES)
                contagem['riscos_depois'] += int(b in ACOES)
                contagem['alterados'] += int(a != b)
                contagem['pausas'] += int(b is None or b in RESPIROS)
                if a is None and b is not None:
                    alertas.append({'regra': 'lacuna_none_mudou', 'bioma': bioma, 'seed': seed, 'i': i, 'm': metros})
                if a not in ACOES and b in ACOES:
                    alertas.append({'regra': 'novo_perigo', 'bioma': bioma, 'seed': seed, 'i': i, 'm': metros})
                if b is not None and b not in VALIDOS:
                    alertas.append({'regra': 'comando_desconhecido', 'bioma': bioma, 'seed': seed, 'i': i, 'm': metros})
                if (ultimo, b) in CHOQUES:
                    alertas.append({'regra': 'choque_diretor', 'bioma': bioma, 'seed': seed, 'i': i, 'm': metros,
                                    'anterior': ultimo, 'atual': b})
                if metros < 900 and a != b:
                    alertas.append({'regra': 'modificacao_antes_900m', 'bioma': bioma, 'seed': seed, 'i': i})
                if b in ACOES:
                    sequencia_risco += 1
                    max_sequencia_risco = max(max_sequencia_risco, sequencia_risco)
                else:
                    sequencia_risco = 0
                ultimo = b
            if contagem['riscos_depois'] > contagem['riscos_antes']:
                alertas.append({'regra': 'mais_perigos', 'bioma': bioma_alvo, 'seed': seed})
            contagem['max_perigos_consecutivos'] = max_sequencia_risco
            total.update({k: v for k, v in contagem.items() if k != 'max_perigos_consecutivos'})
            total['max_perigos_consecutivos'] = max(total.get('max_perigos_consecutivos', 0), max_sequencia_risco)
            resultados.append({'bioma': bioma_alvo, 'seed': seed, **contagem})
    return {'total': dict(total), 'cenarios': resultados, 'alertas_logicos': alertas,
            'cobertura': {'biomas': len(biomas), 'seeds_por_cenario': len(sementes),
                          'encontros_por_cenario': encontros, 'cenarios': len(resultados)},
            'limites': ['None representa geracao classica, nao ausencia de perigo real',
                        'Comandos nao equivalem a objetos/posicoes nem garantem dificuldade',
                        'Risco de transicoes eh auditado simbolicamente, sem temporizadores SDL']}


def simular_encontro_real(game, bioma, comando, velocidade, atraso_ticks, seed=207):
    """Sonda a colisão de UM obstáculo real e Jogador real, passo a passo.

    O retorno apenas informa se existe contato nas condições impostas;
    a janela de reação verdadeira também depende de aviso visual, jogador,
    outros obstáculos, latência de toque, fase dos perigos e spawn.
    """
    import pygame
    rng_state = random.getstate()
    random.seed(int(seed))
    try:
        jogador = game['Jogador']('NORMAL', (250, 252, 255), {})
        if comando == 'SALTO':
            obj = game['_criar_obstaculo_base_bioma'](game['LARGURA_VIRTUAL'] + 20, bioma)
        else:
            obj = game['ObstaculoVoador'](game['LARGURA_VIRTUAL'] + 20, bioma)
            obj.rect.y = game['ALTURA_VIRTUAL'] - (235 if comando == 'ESCOLHA' else 157)
        colidiu = False
        t_contato = None
        passou = False
        duracao = 135
        # Mesma atualizacao 60Hz do jogador e dos obstaculos; teste SEM powerups.
        for tick in range(duracao):
            if tick == atraso_ticks and comando == 'SALTO':
                jogador.pular()
            if tick == atraso_ticks and comando == 'PASSAGEM':
                jogador.agachar(True)
            if tick == atraso_ticks and comando == 'ESCOLHA':
                # O desenho da ESCOLHA oferece passagem inferior sem pulo.
                pass
            jogador.update(velocidade, frame_contador=tick, segurando_pulo=False,
                           segurando_baixo=(comando == 'PASSAGEM' and tick >= atraso_ticks))
            if comando == 'SALTO':
                obj.update(velocidade)
            else:
                obj.update(velocidade, e_noite=False, e_slow=False)
            if game['obstaculo_encosta_jogador'](jogador.obter_hitbox(), obj):
                colidiu = True
                t_contato = tick
                break
            if obj.rect.right < jogador.obter_hitbox().left:
                passou = True
                break
        return {'bioma': bioma, 'comando': comando, 'velocidade_px_tick': velocidade,
                'atraso_ticks': atraso_ticks, 'colisao': colidiu,
                'passou': passou, 'tick_contato': t_contato,
                'obstaculo_classe': type(obj).__name__}
    finally:
        random.setstate(rng_state)


def matriz_colisoes_reais(game, biomas, velocidades=(6., 10., 16., 24.),
                          atrasos=tuple(range(0, 91, 6))):
    """Sondas reais de controles ideais com aproximação isolada, sem mutações."""
    linhas = []
    for bioma in biomas:
        for comando in ('SALTO', 'ESCOLHA', 'PASSAGEM'):
            for velocidade in velocidades:
                for atraso in atrasos:
                    linhas.append(simular_encontro_real(game, bioma, comando, velocidade, atraso,
                                    seed=207 + int(velocidade) + atraso + len(bioma)))
    grupos = []
    for bioma in biomas:
        for comando in ('SALTO', 'ESCOLHA', 'PASSAGEM'):
            for velocidade in velocidades:
                amostras = [x for x in linhas if x['bioma'] == bioma and x['comando'] == comando and
                            x['velocidade_px_tick'] == velocidade]
                validos = [x['atraso_ticks'] for x in amostras if x['passou'] and not x['colisao']]
                grupos.append({'bioma': bioma, 'comando': comando, 'velocidade': velocidade,
                               'atrasos_testados': len(amostras), 'atrasos_sem_colisao': validos,
                               'sem_rota_nas_amostras': not bool(validos)})
    return {'total_sondagens':len(linhas), 'grupos':grupos, 'sondagens':linhas,
            'limites':['Amostras por encontro isolado e velocidade constante, nao uma corrida real',
                      'Teste ESCOLHA percorre rota inferior; PASSAGEM agacha; SALTO executa um salto',
                      'Variantes do obstaculo e timing de fases (ex.: geiser) nao exaustivos',
                      'Falhar em um atraso nao prova injustica; passar em outro nao prova justiça']}
