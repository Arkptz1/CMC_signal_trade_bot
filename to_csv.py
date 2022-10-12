import pandas as pd
import pickle
with open('buys.pkl', 'rb') as file:
    lst = pickle.load(file)
print(lst)
df = pd.DataFrame(columns=['Tokens'])
df['Tokens'] = lst
df.to_csv('tokens.csv')