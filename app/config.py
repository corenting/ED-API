from environs import Env

env = Env()
env.read_env()

DEBUG = env.str("DEBUG", False)

INARA_API_KEY = env.str("INARA_API_KEY")
