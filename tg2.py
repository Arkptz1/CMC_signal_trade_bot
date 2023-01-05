import time
import save_load
from price import price2
from new import buy_sell
from telethon import TelegramClient, events
import time
import threading
import traceback
from new import buy_sell
from network import Net
from loguru import logger
import variables
import parse_cmc
import config_read_cmc
import filters
import pandas as pd

web3 = variables.web3
save_list, load_list, save_dict, read_dict = save_load.save_list, save_load.load_list, save_load.save_dict, save_load.read_dict
channels = [-1001517585345]
sender_address = variables.sender_address
client = variables.client
print("Sucess Started")
Lock = threading.Lock()


@client.on(events.NewMessage(chats=channels))
async def my_event_handler(event):
    if event.message:
        mes = event.message.to_dict()["message"].split('\n')
        trade, cont, liq, slip_buy, slip_sell, name = filters.filters(mes)
        lsd = pd.read_csv('tokens.csv')['Tokens'].to_list()
        if "COINMARKETCAP" in mes[0].upper():
            lsd.append(cont.upper())
            df = pd.DataFrame(columns=['Tokens'])
            df['Tokens'] = lsd
            df.to_csv('tokens.csv')
            if trade:
                cont = web3.toChecksumAddress(cont)
                st = time.time()
                global bot
                try:
                    st = 12
                    if liq != None:
                        if liq < 100:
                            st = 25
                        elif liq < 200:
                            st = 20
                    buy_price = float(
                        buy_sell(int(slip_buy) + st, name).buy(cont))
                    print(time.time() - st)
                    global workers
                    thr = threading.Thread(target=parse_cmc.go_token, args=[
                                           cont, slip_sell, name, variables.sender_address])
                    thr.start()
                except:
                    print(traceback.format_exc())


while True:
    try:
        load = read_dict()
        for i in load.keys():
            t = threading.Thread(target=parse_cmc.go_token, args=load[i])
            t.start()
        client.start()
        client.run_until_disconnected()
    except:
        print(traceback.format_exc())
        load = read_dict()
        for i in load.keys():
            t = threading.Thread(target=parse_cmc.go_token, args=load[i])
            t.start()
        time.sleep(1)
        client.start()
        client.run_until_disconnected()
