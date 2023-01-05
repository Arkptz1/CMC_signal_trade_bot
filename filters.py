import variables
import parse_cmc
import save_load
from loguru import logger


def send_tg(txt):
    logger.warning(txt)
    if variables.bot_work:
        variables.bot.send_message(variables.id_chat, "❌" + txt + '❌')


save_list, load_list, save_dict, read_dict = save_load.save_list, save_load.load_list, save_load.save_dict, save_load.read_dict


def filters(msg):
    if ("NEW TOKEN FOUND" in msg[0].upper()):
        trade = parse_cmc.cicle_am(variables.sender_address)
        if not trade:
            txt = f'Токен не был куплен, так как баланс меньше нужного.'
            send_tg(txt)
        liq = None
        if variables.only_cmc:
            if not ("COINMARKETCAP" in msg[0].upper()):
                trade = False
                txt = f'Токен залистился на коингеко. -> пропускаем.'
                send_tg(txt)
        if trade:
            if variables.only_cg:
                if not ("COINGECKO" in msg[0].upper()):
                    trade = False
                    txt = f'Токен залистился на коинмаркеткап -> пропускаем.'
                    send_tg(txt)
        for i in msg:
            if "Liquidity" in i:
                liq = float(i.split()[1].replace(',', ''))
                if variables.max_liq:
                    if liq > variables.max_liq:
                        trade = False
                        txt = f'У токена {name} ликвидность больше максимальной -> пропускаем.'
                        send_tg(txt)
                    elif liq < variables.min_liq:
                        trade = False
                        txt = f'У токена {name} ликвидность меньше минимальной -> пропускаем.'
                        send_tg(txt)
            if ("Slippage" in i) and ("(buy)" in i):
                slip_buy = int(i.split()[1].replace('%', ''))
            elif ("Slippage" in i) and ("(sell)" in i):
                slip_sell = int(i.split()[1].replace('%', ''))
            if "0x" in i:
                cont = i
            if "Name" in i:
                name = i.split('(')[1].split(')')[0]
        if trade:
            if liq == None:
                if variables.if_no_liq:
                    trade = False
                    txt = f'У токена {name} не указана ликвидность -> пропускаем.'
                    send_tg(txt)
        if trade:
            if variables.pred_list_cmc:
                lsd = load_list()
                if cont.upper() in lsd:
                    trade = False
                    txt = f'Токен {name} уже листился на CMC -> пропускаем.'
                    send_tg(txt)
        if trade:
            if variables.max_slip_s:
                if slip_sell > variables.max_slip_s:
                    trade = False
                    txt = f'У токена {name} Большая ликвидность на продажу -> пропускаем.'
                    send_tg(txt)
        if trade:
            if variables.max_slip_b:
                if slip_buy > variables.max_slip_b:
                    trade = False
                    txt = f'У токена {name} Большая ликвидность на покупку -> пропускаем.'
                    send_tg(txt)
        if trade:
            if variables.max_sum_slip:
                if slip_buy + slip_sell > variables.max_sum_slip:
                    trade = False
                    txt = f'У токена {name} Сумма ликвидности очень большая -> пропускаем.'
                    send_tg(txt)
        if trade:
            if variables.if_slip_bol_1:
                if (slip_buy == 1 and slip_sell == 1):
                    trade = False
                    txt = f'У токена {name} оба slippage равны одному -> пропускаем.'
                    send_tg(txt)
        if trade:
            if "usd" in name.lower():
                trade = False
                txt = f'Токен {name} является стейблкоином -> пропускаем.'
                send_tg(txt)
        return trade, cont, liq, slip_buy, slip_sell, name
