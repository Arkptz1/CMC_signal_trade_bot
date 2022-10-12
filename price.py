
import requests
def price2(cont):
    cont = cont.lower()
    try:
        resp = requests.get(f'https://token-prices.1inch.io/v1.1/56/{cont}', timeout=10)
        return resp.json()[cont]
    except:
        try:
            resp = requests.get(f'https://token-prices.1inch.io/v1.1/56/{cont}', timeout=10)
            return resp.json()[cont]
        except:
            resp = requests.get(f'https://token-prices.1inch.io/v1.1/56/{cont}', timeout=10)
            return resp.json()[cont]