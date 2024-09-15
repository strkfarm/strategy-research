print(500000000000000000/1e18)
# ZKLEND USDC
R0 = 0
R_optimal = 10.52
Rmax = 258.74
U_optimal = 60

Ut = 100
LR = 126.82

# # ZKLEND ETH
# R0 = 0
# R_optimal = 5.13
# Rmax = 185.77
# U_optimal = 65


# Ut = 100
# LR = 157.28


def get_Ut(total_borrow, total_supply):
    return total_borrow/total_supply

def get_R0(R0):
    return R0
R0 = get_R0(R0)

def get_S1(R_optimal, R0):
    return R_optimal-R0
S1 = get_S1(R_optimal, R0)

def get_S2(Rmax, R0, S1):
    return round(Rmax-R0-S1,2)
S2 = get_S2(Rmax, R0, S1)

print("R0:", R0)
print("S1:", S1)
print("S2:", S2)


def get_R(R0,S1,S2,Ut,U_optimal):
    # Equations to calculate borrow and lending rates
    if Ut < U_optimal:
        Rt = R0 + S1*Ut/U_optimal
    elif Ut >= U_optimal:
        Rt = R0 + S1 + S2 * (Ut - U_optimal) / (100 - U_optimal) 
    return round(Rt,2)

Rt = get_R(R0,S1,S2,Ut,U_optimal)
print('Rt:', Rt)

def get_general_protocol_fee(Rt, Ut, LR):
    return 1-(LR/(Rt*Ut/100))
general_protocol_fee = get_general_protocol_fee(Rt, Ut, LR)
print('GCF:', general_protocol_fee)

def get_LR(Rt, Ut, general_protocol_fee):
    return round((Rt * Ut/100 * (1 - general_protocol_fee)),2)
LR = get_LR(Rt, Ut, general_protocol_fee)
print('LR:', LR)

def get_hf(collateral_USD, collateral_factor, borrow_USD, borrow_factor):
    return collateral_USD * collateral_factor / (borrow_USD/borrow_factor)