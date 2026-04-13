from sb3_contrib import RecurrentPPO
from sb3_contrib.ppo_recurrent import CnnLstmPolicy
from gymnasium.wrappers import GrayscaleObservation
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_checker import check_env
import os
import er_environment
from backend import er_helper
import argparse

LEARNING_RATE = 0.0002
CHECKPOINT_DIR = './model/'
LOG_DIR = './logs/'

class CallBack(BaseCallback):
    def __init__(self, freq, path, verbose=1):
        super(CallBack, self).__init__(verbose)
        self.freq = freq
        self.path = path

    def _init_callback(self):
        if self.path is not None:
            os.makedirs(self.path, exist_ok=True)

    def _on_step(self):
        if self.n_calls % self.freq == 0:
            model_path = os.path.join(self.path, 'best_model_{}'.format(self.n_calls))
            self.model.save(model_path)

        if self.n_calls % 1024 == 0:
            er_helper.clean_keys()

        return True

def train_ppo(n_train):
    callback = CallBack(freq=4096, path=CHECKPOINT_DIR)

    env = er_environment.EldenRing(train_mode=2, n_steps=512)
    #print(env.observation_space.shape)
    env = GrayscaleObservation(env, keep_dim=True)
    env = DummyVecEnv([lambda: env]) # maybe in the future make it so there can be multiple environments

    model = RecurrentPPO(CnnLstmPolicy, env, verbose=2, learning_rate=LEARNING_RATE, n_steps=512, batch_size=32, tensorboard_log=LOG_DIR, seed=0)
    #model.load("./model/1.zip")
    model.learn(total_timesteps=(n_train), callback=callback, progress_bar=True)

if __name__ == "__main__":
    par = argparse.ArgumentParser(description="Command-line flags")
    par.add_argument("-t", "--timesteps",
                    help="Specify the number of timesteps for the training process",
                    required=True)

    # TODO: Add back support to disable the database functions
    # TODO: Add in arg that allows changing the n_steps in training loop
    # TODO: Add in arg that allows changing batch size

    n_train = 0

    try:
        n_train = int(par.parse_args().timesteps)
    except:
        raise TypeError("Improper value given for --timesteps")

    train_ppo(n_train)