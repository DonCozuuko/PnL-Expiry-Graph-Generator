# Profit & Loss Expiry Graph Generator
A python utility to generate P&L Expiry graphs for multi-leg option strategies, parsed from CSV. Also contains a library to help calculate net cost, total slopes across the relevent exercise price intervals, max profit, max loss, break evens, and plotting the p&l expiry graph. 
## Features
- Handles both options contracts and underlying contracts (Stocks).
- Note for adding underlying contracts in the .csv, since underlying contracts don't have a premium, the premium will not be processed. So just don't put anything stupid in there.
- Displays the Max Profit, Max Loss, and the Break Even points of the order.
- I can't believe I have to say this but; Red means Loss and Green means Profit.
- Y-Axis ticks are in 100's
## Demo
- **Iron Condor on Waste Management -- Ticker $WM**
![[resources/long_iron_condor_csv.png]]
![[resources/long_iron_condor_graph.png]]

- **Long Straddle on Tesla Automotive -- Ticker $TSLA**
![[resources/long_straddle_csv.png]]
![[resources/long_straddle_graph.png]]

## Dependencies
- pandas
- matplotlib
- math (built-in module)
```
$ pip install -r requirements.txt
```

## Usage
1. Create an empty csv file, or override the example_order.csv file.
2. Enter in your multi-leg option order in the position.csv file, with each row representing one leg in that order, and remember to save it.
![[resources/covered_call_csv.png]]
3. Input the csv file that you want to use, full filename + type.
```
$ python gen_pnl.py
Input the CSV file: example_order.csv
```
4. Sit back and watch the magic.
![[resources/covered_call_graph.png]]