# import files here
from backend.game_accessor import GameAccessor
from backend import er_helper
from backend import speedhack
from backend import walk_back
from backend.walk_back import EnemyContainer
from backend import database_helper

import dxcam
import time
import numpy as np
import gymnasium
import PyMym as pm

import vgamepad as vg

controller_action_space = {
    0: 0,
    1: vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
    2: vg.DS4_BUTTONS.DS4_BUTTON_CROSS,
    3: vg.DS4_BUTTONS.DS4_BUTTON_SQUARE,
    4: vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
    5: vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT,
    6: vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT,
    7: vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_LEFT
}

current_boss = {
    0 : walk_back.soldier_godrick,
    1 : walk_back.beastman,
    2 : walk_back.leonine_misbegotten
}

class EldenRing(gymnasium.Env):
    def __init__(self, train_mode = 0, n_steps = 1024):
        self.__process_wrapper = pm.ProcessWrapper(application_name="eldenring.exe")
        self.__game = GameAccessor(wrapper=self.__process_wrapper)
        self.__camera = dxcam.create(output_color="RGB", max_buffer_len=4)
        left, top, right, bottom = er_helper.client_window_size()
        #self.__region = (12 + left, 52 + top, 12 + right, 52 + bottom)
        self.__region = (left, top, right, bottom)

        self.obs_type = "rgb"

        self.readable_action_space = gymnasium.spaces.Dict({
            "LeftX": gymnasium.spaces.Box(low=-1, high=1, dtype=np.float32),
            "LeftY": gymnasium.spaces.Box(low=-1, high=1, dtype=np.float32),
            "Buttons": gymnasium.spaces.Discrete(len(controller_action_space))
        })

        self.action_space = gymnasium.spaces.flatten_space(self.readable_action_space)

        self.currently_pressed = 0
        self.ds4_controller = vg.VDS4Gamepad()

        self.observation_space = gymnasium.spaces.Box(low = 0, high = 255, shape = ((self.__region[3]- self.__region[1]), (self.__region[2] - self.__region[0]), 3), dtype=np.uint8)
        self.train_mode = train_mode
        self.reward_function = self.complex_reward
        self.games = 0

        self.time_step_run = 0
        self.time_step_total = 0
        self.n_steps = n_steps
        self.begin_time = 0
        self.end_time = 0

        self.speed_hack = speedhack.SpeedHackConnector(pm.get_pid("eldenring.exe"))
        er_helper.controller = self.ds4_controller

        database_helper.create_database()
        self.games = database_helper.get_run_number() + 1 if database_helper.get_run_number() > 0 else 0

        er_helper.find_activate_window()
        self.win = False

        self.__camera.start(region=self.__region, video_mode=True)
        self.__game.reset()

    def __enter__(self):
        pass

    def __exit__(self):
        self.__process_wrapper.close()

    def reset_controller(self):
        self.ds4_controller.reset()
        self.ds4_controller.update()
        self.currently_pressed = 0

    def kill_player(self):
        self.reset_controller()

        if self.player_current_health > 0:
            self.__game.kill_player()

        if (not self.win):
            stake = self.__game.stake_of_marika()
            self.speed_hack.set_game_speed(8)

            if (self.__game.get_player_health() <= 0 or stake):
                time.sleep(5)
                er_helper.key_press('e')
                er_helper.key_press('e')

        time.sleep(10)

    def begin_boss(self):
        self.started_in_round_table = self.__game.player_in_roundtable()
        #self.enemy_container = current_boss[int(str(self.games)[0]) % 3](self.started_in_round_table)
        self.enemy_container : EnemyContainer = current_boss[0](self.started_in_round_table)

        if not (self.__game.get_map_id() == self.enemy_container.door_map_ID and self.started_in_round_table):
            self.__game.reset()

    def switch_boss(self):
        if (not self.__game.player_in_roundtable()):
            er_helper.travel_to_roundtable()
            self.__game.reset()

    def begin_attempt(self):
        self.__game.teleport(self.enemy_container.get_door_coords(self.started_in_round_table))
        self.__game.rotate(self.enemy_container.door_rotation)
        er_helper.lock_on()
        er_helper.enter_boss()
        self.__game.teleport(self.enemy_container.get_arena_coords(self.started_in_round_table))
        self.__game.rotate(self.enemy_container.arena_rotation)
        er_helper.lock_on()

    def reset(self, seed = 0, options = 0) -> None:
        self.win = False

        self.speed_hack.set_game_speed(1)

        self.reward = 0
        self.time_step_run = 0
        self.games += 1
        er_helper.clean_keys()

        while True:
            self.__game.reset()
            self.begin_boss()
            search_timer = time.time()

            while self.__game.enemy == {}:
                time.sleep(0.1)
                self.__game.find_enemy(self.enemy_container.enemy_ID)

                if time.time() - search_timer > 1:
                    er_helper.travel_to_roundtable()
                    break

            if self.__game.enemy != {}:
                anim = self.__game.get_enemy_animation()
                self.begin_attempt()
                if anim != self.__game.get_enemy_animation():
                    break
                else:
                    er_helper.travel_to_roundtable()

        database_helper.increase_attempts(self.enemy_container.enemy_ID)

        self.screenshot()
        self.reset_ground_truth()

        return self.state(), {}

    def reset_ground_truth(self) -> None:
        self.begin_time = time.time()
        # used for rewards
        self.deal_damage_timer = time.time()
        self.take_damage_timer = time.time()

        self.player_max_health = self.__game.get_player_max_health()
        self.player_current_health = self.__game.get_player_health()
        self.player_max_stamina = self.__game.get_player_max_stamina()
        self.player_current_stamina = self.__game.get_player_stamina()
        self.player_max_fp = self.__game.get_player_max_fp()
        self.player_current_fp = self.__game.get_player_fp()
        self.boss_max_health = self.__game.get_enemy_max_health()
        self.boss_current_health = self.__game.get_enemy_health()
        self.player_coordinates = self.__game.get_player_coords()
        self.boss_coordinates = self.__game.get_enemy_coords()
        self.player_animation = self.__game.get_player_animation()
        self.boss_animation = self.__game.get_enemy_animation()
        self.player_current_flasks = self.__game.get_player_heal_flask()

        self.player_previous_health = self.player_current_health
        self.player_previous_stamina = self.player_current_stamina
        self.player_previous_fp = self.player_current_fp
        self.boss_previous_health = self.boss_current_health
        self.player_previous_coordinates = self.player_coordinates
        self.boss_previous_coordinates = self.boss_coordinates
        self.player_previous_animation = self.player_animation
        self.boss_previous_animation = self.boss_animation
        self.player_previous_flasks = self.player_current_flasks

    def perform_action(self, action) -> None:
        button_segment = action[0:8]
        if np.all(button_segment == 0):
            print("Bad Button")
            action[0] = 1.0

        real_action = gymnasium.spaces.unflatten(self.readable_action_space, action)
        #print(real_action)
        if self.currently_pressed != 0:
            self.ds4_controller.release_button(controller_action_space[self.currently_pressed])

        action_button = real_action["Buttons"]
        if action_button != 0:
            self.ds4_controller.press_button(controller_action_space[action_button])

        self.currently_pressed = action_button

        self.ds4_controller.left_joystick_float(real_action["LeftX"][0], real_action["LeftY"][0])
        self.ds4_controller.update()

    def screenshot(self) -> None:
        # screenshot, convert to correct color space
        # DXCam boasts high screen capture speed, but will throw
        # an error if the frame does not change since last screenshot
        try:
            self.__screenshot = np.array(self.__camera.get_latest_frame())
        except:
            return

    def update(self) -> None:
        self.player_previous_health = self.player_current_health
        self.player_previous_stamina = self.player_current_stamina
        self.player_previous_fp = self.player_current_fp
        self.boss_previous_health = self.boss_current_health
        self.player_previous_coordinates = self.player_coordinates
        self.boss_previous_coordinates = self.boss_coordinates
        self.player_previous_animation = self.player_animation
        self.boss_previous_animation = self.boss_animation
        self.player_previous_flasks = self.player_current_flasks

        self.player_current_health = self.__game.get_player_health()
        self.player_current_stamina = self.__game.get_player_stamina()
        self.player_current_fp = self.__game.get_player_fp()
        self.boss_current_health = self.__game.get_enemy_health()
        self.player_coordinates = self.__game.get_player_coords()
        self.player_animation = self.__game.get_player_animation()
        self.boss_coordinates = self.__game.get_enemy_coords()
        self.boss_animation = self.__game.get_enemy_animation()
        self.player_current_flasks = self.__game.get_player_heal_flask()

    def state(self):
        return self.__screenshot

    def simple_reward(self):
        self.reward -= 0.1
        #self.reward = 1 * (self.time_step_run / 128)

        if self.boss_current_health < self.boss_previous_health:
            self.deal_damage_timer = time.time()
            self.reward += ((self.boss_previous_health - self.boss_current_health) / 10)
        if self.boss_current_health != self.boss_previous_health and self.boss_current_health <= 0:
            self.reward += 100

        # punish for taking damage
        if self.player_current_health < self.player_previous_health:
            self.reward -= (15 * ((self.player_previous_health - self.player_current_health) / self.player_max_health))

        if time.time() - self.deal_damage_timer > 12:
            self.reward -= (5 * (time.time() - self.deal_damage_timer - 12))

    def complex_reward(self) -> None:
        self.simple_reward()

        # punish for low stamina
        if self.player_current_stamina < self.player_max_stamina * 0.25:
            self.reward -= (2 * ((self.player_max_stamina * 0.25 - self.player_current_stamina) / self.player_max_stamina))

        if (self.player_current_flasks < self.player_previous_flasks) and (self.player_current_health == self.player_previous_health):
            self.reward -= 10

        if self.player_current_health > self.player_previous_health:
            # reward for healing
            self.reward += (15 * ((self.player_current_health - self.player_previous_health) / self.player_max_health))

            health_diff = self.player_current_health - self.player_previous_health
            if health_diff < 200:
                self.reward -= (5 * (250 - (self.player_current_health - self.player_previous_health)) / 200)

        if self.player_animation == 50113 and self.player_previous_animation != self.player_animation:
            self.reward -= 20


    def one_shot_done(self) -> bool:
        if self.player_current_health < self.player_max_health:
            self.__game.kill_player()
            return self.reg_done()
        return False

    def range_done(self) -> bool:
        if self.player_current_health < (self.player_max_health * .4):
            self.__game.kill_player()
            return self.reg_done()
        return False

    def reg_done(self) -> bool:
        if self.__game.get_player_dead():
            self.reward -= 50
            return True

        if not self.__game.get_enemy_dead():
            return False

        self.reward += 100
        self.win = True
        return True

    def cutscene_check(self) -> bool:
        while not self.__game.check_world_pointer() or self.__game.cutscene_loading_state():
            time.sleep(0.2)

    def step(self, action):
        self.cutscene_check()
        self.perform_action(action)

        if not (self.time_step_total % self.n_steps == 0 and self.time_step_total > 1):
            self.update()
        
        self.screenshot()
        self.reward_function()
        done = ([self.one_shot_done(), self.range_done(), self.reg_done()][self.train_mode])

        truncated = False

        if self.time_step_total % self.n_steps == 0 and self.time_step_total > 1:
            truncated = True
            if not self.__game.player_in_roundtable():
                self.__game.kill_player()
            er_helper.clean_keys()

        if done or truncated:
            er_helper.clean_keys()
            self.end_time = time.time()

            run_info = {
                "Run_Number": self.games,
                "Boss_ID": self.enemy_container.enemy_ID,
                "Boss_Ending_Health": self.boss_current_health,
                "Player_Ending_Health": self.__game.get_player_health(),
                "Total_Time": self.end_time - self.begin_time,
                "Victory": (self.boss_current_health <= 0)
            }

            database_helper.write_to_database_run(run_info)

            if (run_info["Victory"]):
                database_helper.beat_boss(run_info["Boss_ID"])

            self.kill_player()

        self.time_step_run += 1
        self.time_step_total += 1

        return self.state(), self.reward, done, truncated, {}