import pickle
def save_list(obj):
    with open('buys.pkl', 'wb') as f:
        pickle.dump(obj, f)
def load_list():
    with open('buys.pkl', 'rb') as f:
        loaded_lict = pickle.load(f)
        return loaded_lict
def save_dict(obj):
    with open('saved_dictionary.pkl', 'wb') as f:
        pickle.dump(obj, f)
def read_dict():
    with open('saved_dictionary.pkl', 'rb') as f:
        loaded_dict = pickle.load(f)
    return loaded_dict