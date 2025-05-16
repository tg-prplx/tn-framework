import logging
import numpy as np
import os

if os.path.exists("app.log"):
    os.system("rm app.log")

logging.basicConfig(
    filename='app.log',            
    level=logging.DEBUG,          
    format='[%(asctime)s] - [%(levelname)s] - %(message)s'
)

SYMBOLS = np.array(list("▒▓▓█"))