from gym.envs.registration import register

register(
    id="rlproject/RLproject-v0",
    entry_point="rlproject.envs:RLprojectEnv",
)
