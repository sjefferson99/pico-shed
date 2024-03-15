from lib.environment import Environment

env = Environment(log_level=2)

env.init_modules()
env.main_loop()