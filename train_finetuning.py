#! /usr/bin/env python
import os
import pickle

import d4rl
import d4rl.gym_mujoco
import d4rl.locomotion
import dmcgym
import gym
import numpy as np
import tqdm
from absl import app, flags
import time
import math

from ml_collections import config_flags

import wandb
from rlproject.agents import SACLearner
from rlproject.data.replay_buffer import ReplayBuffer
from rlproject.data.wings_datasets import WingsDataset #to process our own data

from rlproject.evaluation import evaluate
from rlproject.wrappers import wrap_gym

try:
    from flax.training import checkpoints
except:
    print("Not loading checkpointing functionality.")

import random



FLAGS = flags.FLAGS

flags.DEFINE_string("project_name", "rlproject", "wandb project name.") #change the default name from rlpd to rlproject
flags.DEFINE_string("env_name", "rlproject/RLproject-v0", "D4rl dataset name.") #change the default name from half-cheetha to RLproject-v0
flags.DEFINE_float("offline_ratio", 0.5, "Offline ratio.")
flags.DEFINE_integer("seed", 42, "Random seed.")
flags.DEFINE_integer("eval_episodes", 10, "Number of episodes used for evaluation.")
flags.DEFINE_integer("log_interval", 1000, "Logging interval.")
flags.DEFINE_integer("eval_interval", 5000, "Eval interval.")
flags.DEFINE_integer("batch_size", 256, "Mini batch size.")
flags.DEFINE_integer("max_steps", int(1e6), "Number of training steps.")
flags.DEFINE_integer(
    "start_training", int(1e4), "Number of training steps to start training."
)
flags.DEFINE_integer("pretrain_steps", 0, "Number of offline updates.")
flags.DEFINE_boolean("tqdm", True, "Use tqdm progress bar.")
flags.DEFINE_boolean("save_video", False, "Save videos during evaluation.")
flags.DEFINE_boolean("checkpoint_model", False, "Save agent checkpoint on evaluation.")
flags.DEFINE_boolean(
    "checkpoint_buffer", False, "Save agent replay buffer on evaluation."
)
flags.DEFINE_integer("utd_ratio", 1, "Update to data ratio.")
flags.DEFINE_boolean(
    "binary_include_bc", True, "Whether to include BC data in the binary datasets."
)

config_flags.DEFINE_config_file(
    "config",
    "rlproject/configs/sac_config.py", #change the path to config file
    "File path to the training hyperparameter configuration.",
    lock_config=False,
)


def combine(one_dict, other_dict):
    combined = {}

    for k, v in one_dict.items():
        if isinstance(v, dict):
            combined[k] = combine(v, other_dict[k])
        else:
            tmp = np.empty(
                (v.shape[0] + other_dict[k].shape[0], *v.shape[1:]), dtype=v.dtype
            )
            tmp[0::2] = v
            tmp[1::2] = other_dict[k]
            combined[k] = tmp

    return combined

# #set a global variable to memorize the time since last done
# last_done_time = 


def main(_):
    # global last_done_time

    assert FLAGS.offline_ratio >= 0.0 and FLAGS.offline_ratio <= 1.0

    wandb.init(project=FLAGS.project_name)
    wandb.config.update(FLAGS)

    exp_prefix = f"s{FLAGS.seed}_{FLAGS.pretrain_steps}pretrain"
    if hasattr(FLAGS.config, "critic_layer_norm") and FLAGS.config.critic_layer_norm:
        exp_prefix += "_LN"

    log_dir = os.path.join(FLAGS.log_dir, exp_prefix)

    if FLAGS.checkpoint_model:
        chkpt_dir = os.path.join(log_dir, "checkpoints")
        os.makedirs(chkpt_dir, exist_ok=True)

    if FLAGS.checkpoint_buffer:
        buffer_dir = os.path.join(log_dir, "buffers")
        os.makedirs(buffer_dir, exist_ok=True)

    env = gym.make(FLAGS.env_name)
    env = wrap_gym(env, rescale_actions=True)
    env = gym.wrappers.RecordEpisodeStatistics(env, deque_size=1)
    env.seed(FLAGS.seed)
    print("For debug - env created") #delete me

    # not ideal, but works for now:
    if "binary" in FLAGS.env_name:
        ds = BinaryDataset(env, include_bc_data=FLAGS.binary_include_bc)
    else:
        # ds = D4RLDataset(env)
        path = "/home/howard/RLproject/rlproject/data/data.json"
        ds = WingsDataset(path) #change to our own dataset
        print("For debug - ds created") #delete me

    # eval_env = gym.make(FLAGS.env_name)
    # eval_env = wrap_gym(eval_env, rescale_actions=True)
    # eval_env.seed(FLAGS.seed + 42)

    kwargs = dict(FLAGS.config)
    model_cls = kwargs.pop("model_cls")
    agent = globals()[model_cls].create(
        FLAGS.seed, env.observation_space, env.action_space, **kwargs
    )
    print("For debug - agent created") #delete me

    replay_buffer = ReplayBuffer(
        env.observation_space, env.action_space, FLAGS.max_steps
    )
    replay_buffer.seed(FLAGS.seed)
    print("For debug - replay_buffer created") #delete me

    # print("For debug - pretrain_steps", FLAGS.pretrain_steps)

    for i in tqdm.tqdm(
        range(0, FLAGS.pretrain_steps), smoothing=0.1, disable=not FLAGS.tqdm
    ):
        # print("For debug - in the first for loop") #delete me
        offline_batch = ds.sample(FLAGS.batch_size * FLAGS.utd_ratio)
        batch = {}
        for k, v in offline_batch.items():
            batch[k] = v
            if "antmaze" in FLAGS.env_name and k == "rewards":
                batch[k] -= 1

        # print("For debug - batch created") #delete me

        agent, update_info = agent.update(batch, FLAGS.utd_ratio)

        # print("For debug - agent updated") #delete me

        if i % FLAGS.log_interval == 0:
            for k, v in update_info.items():
                wandb.log({f"offline-training/{k}": v}, step=i)

        # if i % FLAGS.eval_interval == 0:
        #     eval_info = evaluate(agent, eval_env, num_episodes=FLAGS.eval_episodes)
        #     for k, v in eval_info.items():
        #         wandb.log({f"offline-evaluation/{k}": v}, step=i)

    # print("For debug - first for loop ended") #delete me

    observation, done = env.reset(), False
    #set a global variable to memorize the time since last done
    last_done_time = time.time()
    # observation = env.reset()
    # observation = [random.random() for _ in range(5)]
    # done = False
    # print("For debug - observation(after reset)", observation, np.shape(observation), type(observation)) #delete me

    # print("For debug - env reset") #delete me
    for i in tqdm.tqdm(
        range(0, FLAGS.max_steps + 1), smoothing=0.1, disable=not FLAGS.tqdm
    ):
        start_time = time.time()
        # print("For debug - second for loop started") #delete me

        if i < FLAGS.start_training:
            action = env.action_space.sample()
            # print("For debug - random action ") #delete me
        else:
            # print("For debug - observation", observation, np.shape(observation),type(observation)) #delete me
            action, agent = agent.sample_actions(observation)
            # print("For debug - sample action") #delete me

        # while math.isnan(action[0]):
        #     print(action)
        #     action, agent = agent.sample_actions(observation)
        #     print("For debug - re sample") #delete me

        # print("For debug - action", action, type(action)) #delete me
        next_observation, reward, done, info = env.step(action)
        print("For debug - reward: ", reward, "done:", done) #delete me
        # print(next_observation, reward, done, info) #delete me
        # print("For debug - env step") #delete me

        if not done or "TimeLimit.truncated" in info:
            mask = 1.0
        else:
            mask = 0.0

        replay_buffer.insert(
            dict(
                observations=observation,
                actions=action,
                rewards=reward,
                masks=mask,
                dones=done,
                next_observations=next_observation,
            )
        )
        # print("For debug - replay_buffer inserted") #delete me
        observation = next_observation

        if i >= FLAGS.start_training and (time.time() - last_done_time > 120):
            print("For debug - stuck for 2 min, task fail")
            observation = env.reset()
            last_done_time = time.time()

        if done:
            observation, done = env.reset(), False
            for k, v in info["episode"].items():
                decode = {"r": "return", "l": "length", "t": "time"}
                wandb.log({f"training/{decode[k]}": v}, step=i + FLAGS.pretrain_steps)
            #add a mechanism that prevent the agent from getting stuck
            last_done_time = time.time()

        if i >= FLAGS.start_training:
            online_batch = replay_buffer.sample(
                int(FLAGS.batch_size * FLAGS.utd_ratio * (1 - FLAGS.offline_ratio))
            )
            offline_batch = ds.sample(
                int(FLAGS.batch_size * FLAGS.utd_ratio * FLAGS.offline_ratio)
            )

            batch = combine(offline_batch, online_batch)

            if "antmaze" in FLAGS.env_name:
                batch["rewards"] -= 1
            # start_time = time.time()
            agent, update_info = agent.update(batch, FLAGS.utd_ratio)
            # end_time = time.time()
            # print("For debug - update time: ", end_time - start_time) #delete me

            if i % FLAGS.log_interval == 0:
                for k, v in update_info.items():
                    wandb.log({f"training/{k}": v}, step=i + FLAGS.pretrain_steps)

        # if i % FLAGS.eval_interval == 0:
        #     eval_info = evaluate(
        #         agent,
        #         eval_env,
        #         num_episodes=FLAGS.eval_episodes,
        #         save_video=FLAGS.save_video,
        #     )

        #     for k, v in eval_info.items():
        #         wandb.log({f"evaluation/{k}": v}, step=i + FLAGS.pretrain_steps)

            if FLAGS.checkpoint_model:
                try:
                    checkpoints.save_checkpoint(
                        chkpt_dir, agent, step=i, keep=20, overwrite=True
                    )
                except:
                    print("Could not save model checkpoint.")

            if FLAGS.checkpoint_buffer:
                try:
                    with open(os.path.join(buffer_dir, f"buffer"), "wb") as f:
                        pickle.dump(replay_buffer, f, pickle.HIGHEST_PROTOCOL)
                except:
                    print("Could not save agent buffer.")
        precise_sleep(0.2)

        end_time = time.time()
        # print("For debug -training frequency: ", 1/(end_time - start_time)) #delete me

def precise_sleep(delay):
    start = time.perf_counter()
    while time.perf_counter() - start < delay:
        pass

if __name__ == "__main__":
    app.run(main)
