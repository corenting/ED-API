from environs import Env

env = Env()
env.read_env()

DATABASE_URI = env.str("DATABASE_URI")
DEBUG = env.str("DEBUG", False)
FCM_API_KEY = env.str("FCM_API_KEY")
INARA_API_KEY = env.str("INARA_API_KEY")