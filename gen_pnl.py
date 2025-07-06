from options import Call, Put, Stock, Position
import pandas as pd

orders = []

df = pd.read_csv('position.csv')
pos = Position()

for i in range(len(df)):
    contract_type = df.loc[i, "Type"]
    premium = float(str(df.loc[i, "Premium"]))
    strike_price = int(str(df.loc[i, "Strike"]))
    volume = int(df.loc[i, "Volume"])
    position = df.loc[i, "Position"]

    # print(contract_type, premium, strike_price, volume, position)
    contract = None
    if contract_type == "Call":
        contract = Call(strike_price, premium)
    elif contract_type == "Put":
        contract = Put(strike_price, premium)
    elif contract_type == "Stock":
        contract = Stock(strike_price)
    

    if position == "Long":
        pos.buy(contract, volume)
    elif position == "Short":
        pos.sell(contract, volume)
    orders.append((contract, position))

pos.plot()
