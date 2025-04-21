import time
from configs.environment import get_environment_variables
from models.base_model import create_tables

create_tables()

print(f'settings = {get_environment_variables()}')

while True:
    print(f'hi {time.time()}')
    time.sleep(5)
