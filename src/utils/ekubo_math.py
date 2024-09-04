import math

def get_token_order(address1: str, address2: str) -> tuple:
    """
    Compares two token addresses and returns the addresses as token0_address and token1_address.

    Parameters:
    - address1: str, first token address (in hexadecimal format).
    - address2: str, second token address (in hexadecimal format).

    Returns:
    - A tuple with (token0_address, token1_address), where token0_address < token1_address.
    """
    # Convert the hexadecimal addresses to integers
    address1_int = int(address1, 16)
    address2_int = int(address2, 16)
    
    # Compare the integer values and return them in the correct order
    if address1_int < address2_int:
        return (address1, address2)  # address1 is token0_address, address2 is token1_address
    else:
        return (address2, address1)  # address2 is token0_address, address1 is token1_address

import math

def get_pool_fee_touse(pool_fee: float) -> int:
    """
    Calculate the pool fee to use, scaled by 2^128.

    Parameters:
    - pool_fee: float, the pool fee as a percentage (e.g., for 0.3% pass 0.3).

    Returns:
    - int, the pool fee to use, scaled by 2^128.
    """
    return math.floor((pool_fee / 100) * 2**128)

def get_tick_spacing_touse(tick_spacing: float) -> int:
    """
    Calculate the tick spacing to use, based on logarithmic operations.

    Parameters:
    - tick_spacing: float, the tick spacing percentage.

    Returns:
    - int, the calculated tick spacing to use.
    """
    return math.ceil(math.log(1 + tick_spacing / 100) / math.log(1.000001))

def bool_to_sign(x):
    if x == 0:
        return 1
    elif x == 1:
        return -1
    else:
        raise Exception("invalid input")
        
def price_to_nearest_tick(price, tick_spacing_touse=20):
    return round(int(math.log(price) / math.log(1.000001)) / tick_spacing_touse) * tick_spacing_touse

def price_to_tick(price):
    return int(math.log(price) / math.log(1.000001))

def impermanent_loss(price_ratio):
    return 1 - math.sqrt((4 * price_ratio) / ((price_ratio + 1) ** 2))
