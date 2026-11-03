# -*- coding: utf-8 -*-
"""Fechamento QA: pré-aquecimento incremental de skins/pets no MENU.

Somente funções já existentes no jogo; não carrega saves, não libera itens,
não altera RNG global nem tenta ativar pets atualmente desabilitados.
Uma tarefa a cada oito quadros de MENU, nunca durante o tutorial ou corrida.
"""
import random
from collections import deque

_MENU=frozenset(('INICIO','LOJA','CONFIG','UPGRADES'))
class PrecargaVisuaisQA:
    def __init__(self, skin_equipada, skins_ativas, pet_equipado,
                 renderizar_skin, preparar_pet):
        ids=[]
        if skin_equipada in skins_ativas:
            ids.append(skin_equipada)
        ids.extend(sorted(x for x in skins_ativas if x not in ids))
        self._fila=deque([('skin',x) for x in ids])
        if pet_equipado:
            self._fila.append(('pet',pet_equipado))
        self._renderizar_skin=renderizar_skin
        self._preparar_pet=preparar_pet
        self._ticks_menu=0
        self.status={'skins_prontas':0,'pets_preparados':0,'fallbacks':0,
                     'tarefas_pendentes':len(self._fila),
                     'sorteio_alterado':False}

    def passo(self, estado):
        if estado not in _MENU or not self._fila:
            return False
        self._ticks_menu+=1
        # Dar tempo para a tela inicial ser apresentada; somente
        # um item por 8 frames de menu. Não tocar o loop JOGANDO.
        if self._ticks_menu<6 or self._ticks_menu%8!=0:
            return False
        tipo,item=self._fila.popleft()
        estado_rng=random.getstate()
        try:
            if tipo=='skin':
                self._renderizar_skin(item)
                self.status['skins_prontas']+=1
            else:
                self._preparar_pet(item)
                self.status['pets_preparados']+=1
        except (ValueError,TypeError,RuntimeError,KeyError,MemoryError):
            # Falha de asset: o caminho lazy original continua intacto.
            self.status['fallbacks']+=1
        finally:
            # A identidade da próxima fase e dos spawns não é alterada
            # mesmo se um renderizador futuro passar a consultar random.
            random.setstate(estado_rng)
            self.status['tarefas_pendentes']=len(self._fila)
        return True

    def diagnostico(self):
        return dict(self.status,menu_ticks=self._ticks_menu)
