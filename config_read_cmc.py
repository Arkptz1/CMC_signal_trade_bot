import json
def config_read():
    with open('config.json', 'r') as f:
        data = json.load(f)
    for i in data.keys():
        if data[i] == 'True':
            data[i] = True
        elif data[i] == 'False':
            data[i] = False
    return data.values()

