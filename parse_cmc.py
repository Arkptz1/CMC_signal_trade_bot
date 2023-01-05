import variables
import time
import save_load
from price import price2
from new import buy_sell
web3 = variables.web3
save_list, load_list, save_dict, read_dict = save_load.save_list, save_load.load_list, save_load.save_dict, save_load.read_dict


def bal_token(contr, sender_address):
    contract_id = web3.toChecksumAddress(contr)
    sellTokenContract = web3.eth.contract(contract_id, abi=variables.sellAbi)
    # Get Token Balance
    bal = sellTokenContract.functions.balanceOf(sender_address).call()
    return bal


def go_token(cont, slip_s, name, sender_address, buy_moment_price=None, stop=None):
    tokens = bal_token(cont, sender_address)
    procen = (100-variables.trailing_stop_loss)/100
    if buy_moment_price == None or stop == None:
        buy_moment_price = int(price2(cont))
        stop = buy_moment_price * procen
    cont2 = str(cont).lower()
    try:
        price = int(price2(cont2))
    except:
        price = int(price2(cont2))
    while price > stop:
        if price*procen > stop * 1.01:
            stop = stop * 1.01
        print(
            f"{name}\nbuy_price: {buy_moment_price}\nprice_now: {price}\nstop: {stop}")
        try:
            save = read_dict()
            save[name] = [cont, slip_s, name, buy_moment_price, stop]
            save_dict(save)
        except:
            pass
        time.sleep(1)
        try:
            price = price = int(price2(cont))
        except:
            price = price = int(price2(cont))
    buy_sell(int(slip_s) + 10, name, amount=tokens).sell(cont)
    try:
        save = read_dict()
        del save[name]
        save_dict(save)
    except:
        pass


def cicle_am(sender_address):
    balance = web3.eth.get_balance(sender_address)
    balance = float(web3.fromWei(balance, 'ether'))
    global trade
    if (balance - 0.01) * (10**18) < variables.amount:
        trade = False
    else:
        trade = True
    return trade
