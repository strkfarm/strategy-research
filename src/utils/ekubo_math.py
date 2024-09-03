import math
import numpy as np

def bool_to_sign(x):
    if x == 0:
        return 1
    elif x == 1:
        return -1
    else:
        raise Exception("invalid input")

def price_to_tick_id(price, tick_spacing_touse=20):
    return round(int(np.log(price) / np.log(1.000001)) / tick_spacing_touse) * tick_spacing_touse

def price_to_tick(price):
    return int(math.log(price) / math.log(1.0001))

def impermanent_loss(price_ratio):
    return 1 - math.sqrt((4 * price_ratio) / ((price_ratio + 1) ** 2))