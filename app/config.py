from environs import Env

env = Env()
env.read_env()

DATABASE_URI = env.str("DATABASE_URI")
DEBUG = env.str("DEBUG", False)
INARA_API_KEY = env.str("INARA_API_KEY")
LOG_LEVEL = env.str("LOG_LEVEL", "WARNING")
