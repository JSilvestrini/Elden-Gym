import PyMym as pm
import struct

bases = {
    "WorldChrMan": {"aob": "48 8B 05 00 00 00 00 48 85 C0 74 0F 48 39 88", "mask": "xxx????xxxxxxxx", "offset": 3, "additional": 7},
    "WorldChrManAlt": {"aob": "0F 10 00 0F 11 44 24 70 0F 10 48 10 0F 11 4D 80 48 83 3D", "mask": "xxxxxxxxxxxxxxxxxxx", "offset": 19, "additional": 24},
    "GameDataMan": {"aob": "48 8B 05 00 00 00 00 48 85 C0 74 05 48 8B 40 58 C3 C3", "mask": "xxx????xxxxxxxxxxx", "offset": 3, "additional": 7},
    "NetManImp": {"aob": "48 8B 05 00 00 00 00 80 78 00 00 00 00 48 8D 9F 00 00 00 00 48 8B 03", "mask": "xxx????xx?x??xxx????xxx", "offset": 3, "additional": 7},
    "EventFlagMan": {"aob":"48 8B 3D 00 00 00 00 48 85 FF 00 00 32 C0 E9", "mask": "xxx????xxx??xxx", "offset": 3, "additional": 7},
    "FieldArea": {"aob":"48 8B 0D 00 00 00 00 48 00 00 00 44 0F B6 61 00 E8 00 00 00 00 48 63 87 00 00 00 00 48 00 00 00 48 85 C0", "mask": "xxx????x???xxxx?x????xxx????x???xxx", "offset": 3, "additional": 7},
}

player_addrs_loc = {
    "playerDead": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x1c5]},
    "playerHealth": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x0, 0x138]},
    "playerMaxHealth": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x0, 0x13c]},
    "playerFP": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x0, 0x148]},
    "playerMaxFP": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x0, 0x14c]},
    "playerStamina": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x0, 0x154]},
    "playerMaxStamina": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x0, 0x158]},
    "playerAnimation": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x80, 0x90]},
    "playerAnimationSpeed": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x28, 0x17C8]},
    "playerCos": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0x54]},
    "playerSin": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0x5c]},
    "playerGravity": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0x1d3]},
    "cutsceneLoading": {"base" : "EventFlagMan", "offsets" : [0x28, 0x113]}, # if byte == 128, cutscene

    "playRegionID": {"base" : "FieldArea", "offsets" : [0xE4]},
    "mapID": {"base" : "FieldArea", "offsets" : [0x2C]},
    "playerX": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0x70]},
    "playerY": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0x74]},
    "playerZ": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0x78]},
    "playerGlobalX": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6B0]},
    "playerGlobalY": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6B4]},
    "playerGlobalZ": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6B8]},
    "altMapID": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6C0]},
    "playerChunkX": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0xa8, 0x18, 0xD0]},
    "playerChunkZ": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0xa8, 0x18, 0xD4]},
    "playerChunkY": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x190, 0x68, 0xa8, 0x18, 0xD8]},
    "lastPlayerGlobalX": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6C4]},
    "lastPlayerGlobalY": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6C8]},
    "lastPlayerGlobalZ": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6CC]},
    "lastAltMapID": {"base" : "WorldChrMan", "offsets" : [0x10ef8, 0x0, 0x6D4]},

    "healingFlask": {"base": "GameDataMan", "offsets": [0x8, 0x101]},
    "FPFlask": {"base": "GameDataMan", "offsets": [0x8, 0x102]},
    "leftItem": {"base": "GameDataMan", "offsets": [0x8, 0x399]},
    "rightItem": {"base": "GameDataMan", "offsets": [0x8, 0x39C]},
    "leftItem2": {"base": "GameDataMan", "offsets": [0x8, 0x3A0]},
    "rightItem2": {"base": "GameDataMan", "offsets": [0x8, 0x3A4]},
    "leftItem3": {"base": "GameDataMan", "offsets": [0x8, 0x3A8]},
    "rightItem3": {"base": "GameDataMan", "offsets": [0x8, 0x3AC]},
    "helmet": {"base": "GameDataMan", "offsets": [0x8, 0x3C8]},
    "chest": {"base": "GameDataMan", "offsets": [0x8, 0x3CC]},
    "arms": {"base": "GameDataMan", "offsets": [0x8, 0x3D0]},
    "leggings": {"base": "GameDataMan", "offsets": [0x8, 0x3D4]}
}

camera_addrs = {
    "X": {},
    "Y": {},
    "Z": {},
    "Yaw": {},
    "Pitch": {}
}

enemy_addrs_loc = {
    "ID": {"offsets": [0x28, 0x124]},
    "globalID": {"offsets": [0x74]},
    "paramID": {"offsets": [0x60]},
    "health": {"offsets": [0x190, 0x0, 0x138]},
    "maxHealth": {"offsets": [0x190, 0x0, 0x13c]},
    "animation": {"offsets": [0x190, 0x18, 0x40]},
    "animationSpeed": {"offsets": [0x190, 0x28, 0x17C8]},
    "x": {"offsets": [0x190, 0x68, 0x70]},
    "y": {"offsets": [0x190, 0x68, 0x74]},
    "z": {"offsets": [0x190, 0x68, 0x78]},
    "isDead": {"offsets": [0x58, 0xc8, 0x24]},
}

class GameAccessor:
    def __init__(self, wrapper: pm.ProcessWrapper):
        self.er : pm.ProcessWrapper = wrapper
        self.__is_paused = False
        self.__gravity = True
        self.reset()

    def reset(self) -> None:
        self.__physics_pointer = 0x0
        self.enemy = {}
        self._load_data()

    def _load_data(self):
        for key in bases.keys():
            addr = self.er.module_aob_scan(module_name="eldenring.exe", pattern=bases[key]["aob"], mask=bases[key]["mask"], hex_string=True)
            off = self.er.int[addr + bases[key]["offset"]]
            r_addr = self.er.longlong[addr + off + bases[key]["additional"]]
            bases[key]["address"] = r_addr

        for key in player_addrs_loc.keys():
            b_addr = player_addrs_loc[key]["base"]
            r_addr = bases[b_addr]["address"]
            offs = player_addrs_loc[key]["offsets"]
            for i in range(len(offs) - 1):
                r_addr = self.er.longlong[r_addr + offs[i]]

            player_addrs_loc[key]["address"] = r_addr + offs[-1]

        self.__physics_pointer = self.er.module_aob_scan(module_name="eldenring.exe", pattern="80 BB 28 01 00 00 00 0F 84", hex_string=True)

    def clean(self) -> None:
        self.enemy = {}

    def check_world_pointer(self) -> bool:
        return self.er.module_aob_scan(module_name="eldenring.exe", pattern=bases["WorldChrMan"]["aob"], mask=bases["WorldChrMan"]["mask"], hex_string=True)

    def get_physics_pointer(self) -> int:
        return self.__physics_pointer

    def player_in_roundtable(self) -> bool:
        return self.er.int[bases["FieldArea"]["address"] + 0xE4] == 11100

    def get_player_dead(self) -> bool:
        return self.get_player_health() <= 0

    def get_player_health(self) -> int:
        return self.er.int[player_addrs_loc["playerHealth"]["address"]]

    def get_player_max_health(self) -> int:
        return self.er.int[player_addrs_loc["playerMaxHealth"]["address"]]

    def kill_player(self) -> None:
        self.er.int[player_addrs_loc["playerHealth"]["address"]] = 0

    def get_player_fp(self) -> int:
        return self.er.int[player_addrs_loc["playerFP"]["address"]]

    def get_player_max_fp(self) -> int:
        return self.er.int[player_addrs_loc["playerMaxFP"]["address"]]

    def get_player_stamina(self) -> int:
        return self.er.int[player_addrs_loc["playerStamina"]["address"]]

    def get_player_max_stamina(self) -> int:
        return self.er.int[player_addrs_loc["playerMaxStamina"]["address"]]

    def get_player_coords(self) -> tuple:
        x = self.er.float[player_addrs_loc["playerX"]["address"]]
        y = self.er.float[player_addrs_loc["playerY"]["address"]]
        z = self.er.float[player_addrs_loc["playerZ"]["address"]]
        return (x, y, z)

    def get_player_rotation(self) -> tuple:
        cos = self.er.float[player_addrs_loc["playerCos"]["address"]]
        sin = self.er.float[player_addrs_loc["playerSin"]["address"]]
        return (cos, sin)

    def get_player_animation(self) -> int:
        return self.er.int[player_addrs_loc["playerAnimation"]["address"]]

    def get_player_heal_flask(self) -> int:
        return self.er.int[player_addrs_loc["healingFlask"]["address"]]

    def get_player_fp_flask(self) -> int:
        return self.er.int[player_addrs_loc["FPFlask"]["address"]]

    def get_left_equipment(self) -> list:
        ret = [
            self.er.int[player_addrs_loc["leftItem"]["address"]],
            self.er.int[player_addrs_loc["leftItem2"]["address"]],
            self.er.int[player_addrs_loc["leftItem3"]["address"]]
        ]

        return ret

    def get_right_equipment(self) -> list:
        ret = [
            self.er.int[player_addrs_loc["rightItem"]["address"]],
            self.er.int[player_addrs_loc["rightItem2"]["address"]],
            self.er.int[player_addrs_loc["rightItem3"]["address"]]
        ]

        return ret

    def get_armor(self) -> list:
        ret = [
            self.er.int[player_addrs_loc["helmet"]["address"]],
            self.er.int[player_addrs_loc["chest"]["address"]],
            self.er.int[player_addrs_loc["arms"]["address"]],
            self.er.int[player_addrs_loc["leggings"]["address"]]
        ]

        return ret

    def toggle_gravity(self) -> None:
        if self.__gravity:
            self.er.int[player_addrs_loc["playerGravity"]["address"]] = 1
        else:
            self.er.int[player_addrs_loc["playerGravity"]["address"]] = 0

        self.__gravity = not self.__gravity

    def cutscene_loading_state(self):
        return self.er[player_addrs_loc["cutsceneLoading"]["address"]] > 0

    def pause_game(self) -> None:
        if self.__is_paused:
            self.er[self.__physics_pointer + 0x6] = 1
        else:
            self.er[self.__physics_pointer + 0x6] = 0

        self.__is_paused = not self.__is_paused

    def stake_of_marika(self) -> bool:
        offsets =  [0x10ef8, 0x0, 0x178, 0x8]
        addr = bases["WorldChrMan"]["address"]
        for offset in offsets:
            addr = self.er.longlong[addr + offset]

        temp = addr
        try:
            for i in range(0, 15):
                for _ in range(0, i):
                    temp = self.er.longlong[temp + 0x30]

                if temp == 8:
                    return False
                if self.er.int[temp + 0x8] == 26:
                    return True
        except:
            return False

    def find_enemy(self, id) -> None:
        #print(f"FINDING ENEMIES: {ids}")
        self.enemy = {}

        pattern = bases["WorldChrManAlt"]["aob"]
        mask = bases["WorldChrManAlt"]["mask"]
        addr = self.er.module_aob_scan(module_name='eldenring.exe', pattern=pattern, mask=mask, hex_string=True)
        offset = self.er.int[addr + bases["WorldChrManAlt"]["offset"]]
        address = self.er.longlong[addr + offset + bases["WorldChrManAlt"]["additional"]]
        bases["WorldChrManAlt"]["address"] = address

        p = bases["WorldChrManAlt"]["address"]
        begin = self.er.longlong[p + 0x1f1b8]
        end = self.er.longlong[p + 0x1f1c0]
        characters = (end - begin) // 8

        for i in range(characters):
            #print(f"Scanning Character {i}")
            addr = self.er.longlong[begin + i * 8]
            tb = self.er.int[addr + 0x60]

            if tb == id:
                self.find_enemy_addrs(addr)
                break

    def find_enemy_addrs(self, base) -> None:
        self.enemy = {}
        for key in enemy_addrs_loc.keys():
            offsets = enemy_addrs_loc[key]["offsets"]
            addr = base
            for offset in range(len(offsets) - 1):
                addr = self.er.longlong[addr + offsets[offset]]
            self.enemy[key] = addr + offsets[-1]

    def get_enemy_health(self) -> list:
        return self.er.int[self.enemy["health"]]

    def get_enemy_max_health(self) -> list:
        return self.er.int[self.enemy["maxHealth"]]

    def get_enemy_id(self) -> list:
        return self.er.int[self.enemy["ID"]]

    def get_global_id(self, integer: bool = False) -> list:
        id = 0
        tb = bytes(self.er[self.enemy["globalID"]: self.enemy["globalID"] + 2])
        if integer:
            id = int(struct.unpack('>H', tb)[0].to_bytes(2, byteorder='little').hex(), 16)
        else:
            id = struct.unpack('>H', tb)[0].to_bytes(2, byteorder='little').hex()
        return id

    def get_param_id(self) -> list:
        return self.er.int[self.enemy["paramID"]]

    def get_enemy_animation(self) -> list:
        return self.er.int[self.enemy["animation"]]

    def get_enemy_coords(self) -> list:
        x = self.er.float[self.enemy["x"]]
        y = self.er.float[self.enemy["y"]]
        z = self.er.float[self.enemy["z"]]
        return [x, y, z]

    def get_enemy_dead(self) -> list:
        return self.er[self.enemy["isDead"]] > 0

    def teleport(self, coords) -> None:
        self.toggle_gravity()
        self.er.float[player_addrs_loc["playerX"]["address"]] = coords[0]
        self.er.float[player_addrs_loc["playerY"]["address"]] = coords[1]
        self.er.float[player_addrs_loc["playerZ"]["address"]] = coords[2]
        self.toggle_gravity()

    def rotate(self, rotation) -> None:
        self.er.float[player_addrs_loc["playerCos"]["address"]] = rotation[0]
        self.er.float[player_addrs_loc["playerSin"]["address"]] = rotation[1]

    def get_map_id(self) -> int:
        return self.er.int[player_addrs_loc["mapID"]["address"]]

if __name__ == "__main__":
    pass