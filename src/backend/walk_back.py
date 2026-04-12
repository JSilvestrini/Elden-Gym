from backend.er_helper import key_press, key_presses, find_activate_window, talk_to_gideon
from typing import List

class EnemyContainer:
    def __init__(self):
        self.enemy_ID = -1
        self.door_map_ID = -1
        self.door_coords = []
        self.true_door_coords = []
        self.arena_map_ID = -1
        self.arena_tp_coords = []
        self.true_arena_coords = []
        self.door_rotation = []
        self.arena_rotation = []
        self.stake = False
        self.phase_two = False

    def get_door_coords(self, talked):
        if talked:
            return self.door_coords

        return self.true_door_coords

    def get_arena_coords(self, talked):
        if talked:
            return self.arena_tp_coords

        return self.true_arena_coords

def leonine_misbegotten(talk) -> EnemyContainer:
    if talk:
        talk_to_gideon([1, 0])

    e = EnemyContainer()
    e.enemy_ID = 34600913
    e.door_map_ID = 0x3C2B1E00
    e.door_coords = [-11.971, -0.2378, 0.9075]
    e.door_rotation = [0.1376, 0.9905]
    e.arena_map_ID = e.door_map_ID
    e.arena_tp_coords = [-19.995, 0.25793, -21.154]
    e.arena_rotation = [0.2423, 0.97021]
    e.true_door_coords = e.door_coords
    e.true_arena_coords = e.arena_tp_coords

    return e

def soldier_godrick(talk: bool) -> EnemyContainer:
    if talk:
        talk_to_gideon([2, 3, 0])

    e = EnemyContainer()
    e.enemy_ID = 43113906
    e.door_map_ID = 0x12000000
    e.door_coords = [-0.886, 0.9078, 4.9455]
    e.door_rotation = [0.331, 0.9436]
    e.arena_map_ID = e.door_map_ID
    e.arena_tp_coords = [-15, 0.6, -5]
    e.arena_rotation = [0.13, 0.99]
    e.true_door_coords = [-9.097, 0.9078, -10.883]
    e.true_arena_coords = [-25, 0.6, -20]
    e.stake = True

    return e

def beastman(talk: bool) -> EnemyContainer:
    if talk:
        talk_to_gideon([2, 3, 1])

    e = EnemyContainer()
    e.enemy_ID = 39701910
    e.door_map_ID = 0x1F030000
    e.door_coords = [-8.181, 1.836, 2.11]
    e.door_rotation = [0.923, 0.385]
    e.arena_map_ID = e.door_map_ID
    e.arena_tp_coords = [-21.552, 0.4452, 10.873]
    e.arena_rotation = [0.8645, 0.5026]
    e.true_door_coords = e.door_coords
    e.true_arena_coords = e.arena_tp_coords

    return e

# LEGACY

def elemer() -> List[int]:
    talk_to_gideon([1, 8])
    return [31000931]

def misbegotten_crusader() -> List[int]:
    talk_to_gideon([2, 3, 21])
    return [34601952]

def dancing_lion() -> List[int]: 
    talk_to_gideon([3, 0])
    return [52100088]

def rellana() -> List[int]:
    talk_to_gideon([3, 1])
    return [53000082]

def messmer() -> List[int]:
    talk_to_gideon([3, 6])
    return [51300099, 51301099]

def midra() -> List[int]:
    talk_to_gideon([3, 7])
    key_press('w', 1)
    return [50500086, 50510086]