import pytest
import math
import sys
import os

# Add the parent directory of the test file to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.ekubo_math import (
    get_liquidity,
    get_x,
    get_y,
)

def bool_to_sign(x):
    if x == 0:
        return 1
    elif x == 1:
        return -1
    else:
        raise Exception("invalid input")

        
# Test data for each function
# Test case 1-Position updated event: https://starkscan.co/event/0x02d401d2563cdd0ce008cb49a42e2b1e0e9f1dafbf7fe08f59d08e5dd0208d5b_2
# Test case 1-swapped event: https://starkscan.co/event/0x04cbb6944a936bb124ad2d499922ee487b732e29426be6ba1b7231ed0acbc6da_1

# Test case 2-Position updated event: https://starkscan.co/event/0x00ee5967783616a8ebcc87668f6ffae1bf7bfbe415d13b55a81cd2ed080f2c7d_3
# Test case 2-swapped event: https://starkscan.co/event/0x07ff3b56778a5e0be00cba705dfc1c156a2f2f2c9f92a401fa4f85b9c74657c0_6

# Test case 3-Position updated event: https://starkscan.co/event/0x00ff4f373d608d6e8bb2d6291c4bafbc54961873d16196b6cd0efedce218e99a_4
# Test case 3-Swapped event: https://starkscan.co/event/0x0241c54ae5cb79738aab505fa28bb490289673e63f310e052173265e7294c129_3

# Test data for each function

testdata_get_liquidity = [
    (
        0, #x
        2147718844699912146 * bool_to_sign(1),#y
        math.sqrt(1.000001 ** (158482 * bool_to_sign(0))), #sp
        math.sqrt(1.000001 ** (158400 * bool_to_sign(0))), #sa
        math.sqrt(1.000001 ** (158440 * bool_to_sign(0))), #sb
        99209107691145427163307 * bool_to_sign(1) # L
    ),
    (
        2380000000000000000 * bool_to_sign(0),
        3064071012072246010 * bool_to_sign(0),
        math.sqrt(1.000001 ** (158474 * bool_to_sign(0))),
        math.sqrt(1.000001 ** (158240 * bool_to_sign(0))),
        math.sqrt(1.000001 ** (158860 * bool_to_sign(0))),
        17442970835766897709847 * bool_to_sign(0)

    ),
    (
        179901791914979877 * bool_to_sign(1),
        0,
        math.sqrt(1.000001 ** (158574 * bool_to_sign(0))),
        math.sqrt(1.000001 ** (158580 * bool_to_sign(0))),
        math.sqrt(1.000001 ** (158840 * bool_to_sign(0))),
        1498166625277028332296 * bool_to_sign(1)        
    )   
]

testdata_get_x = [
    (          
        99209107691145427163307 * bool_to_sign(1), #L
        math.sqrt(1.000001 ** (158482 * bool_to_sign(0))), # sp
        math.sqrt(1.000001 ** (158400 * bool_to_sign(0))), # sa
        math.sqrt(1.000001 ** (158440 * bool_to_sign(0))), # sb
        0  # Expected result is 0 #x
    ),
    (
        17442970835766897709847 * bool_to_sign(0), #L
        math.sqrt(1.000001 ** (158474 * bool_to_sign(0))), # sp
        math.sqrt(1.000001 ** (158240 * bool_to_sign(0))), # sa
        math.sqrt(1.000001 ** (158860 * bool_to_sign(0))), # sb
        2380000000000000000 * bool_to_sign(0),
    ),
    (
        1498166625277028332296 * bool_to_sign(1), #L
        math.sqrt(1.000001 ** (158574 * bool_to_sign(0))), # sp
        math.sqrt(1.000001 ** (158580 * bool_to_sign(0))), # sa
        math.sqrt(1.000001 ** (158840 * bool_to_sign(0))), # sb
        179901791914979877 * bool_to_sign(1) #x
    )
]


testdata_get_y = [
    (          
        99209107691145427163307 * bool_to_sign(1), #L
        math.sqrt(1.000001 ** (158482 * bool_to_sign(0))), # sp
        math.sqrt(1.000001 ** (158400 * bool_to_sign(0))), # sa
        math.sqrt(1.000001 ** (158440 * bool_to_sign(0))), # sb
        2147718844699912146 * bool_to_sign(1)  # Expected result is 0 #y
    ),
    (
        17442970835766897709847 * bool_to_sign(0), #L
        math.sqrt(1.000001 ** (158474 * bool_to_sign(0))), # sp
        math.sqrt(1.000001 ** (158240 * bool_to_sign(0))), # sa
        math.sqrt(1.000001 ** (158860 * bool_to_sign(0))), # sb
        3064071012072246010 * bool_to_sign(0)  # Expected result is 0 #x 
    ),
    (
        1498166625277028332296 * bool_to_sign(1), #L
        math.sqrt(1.000001 ** (158574 * bool_to_sign(0))), # sp
        math.sqrt(1.000001 ** (158580 * bool_to_sign(0))), # sa
        math.sqrt(1.000001 ** (158840 * bool_to_sign(0))), # sb
        0  # Expected result is 0 #y
    )
]

@pytest.mark.parametrize("x, y, sqrt_price, sqrt_lower_bound, sqrt_upper_bound, expected_result", testdata_get_liquidity)
def test_get_liquidity(x, y, sqrt_price, sqrt_lower_bound, sqrt_upper_bound, expected_result):
    result = get_liquidity(x, y, sqrt_price, sqrt_lower_bound, sqrt_upper_bound)
    assert pytest.approx(result, rel=1e-8) == expected_result, f"Expected {expected_result}, but got {result}"

@pytest.mark.parametrize("L, sqrt_price, sqrt_lower_bound, sqrt_upper_bound, expected_result", testdata_get_x)
def test_get_x(L, sqrt_price, sqrt_lower_bound, sqrt_upper_bound, expected_result):
    result = get_x(L, sqrt_price, sqrt_lower_bound, sqrt_upper_bound)
    assert pytest.approx(result, rel=1e-8) == expected_result, f"Expected {expected_result}, but got {result}"

@pytest.mark.parametrize("L, sqrt_price, sqrt_lower_bound, sqrt_upper_bound, expected_result", testdata_get_y)
def test_get_y(L, sqrt_price, sqrt_lower_bound, sqrt_upper_bound, expected_result):
    result = get_y(L, sqrt_price, sqrt_lower_bound, sqrt_upper_bound)
    assert pytest.approx(result, rel=1e-8) == expected_result, f"Expected {expected_result}, but got {result}"