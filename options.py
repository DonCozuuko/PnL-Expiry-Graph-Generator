import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import math

MIN_STRIKE = 0
MAX_STRIKE = 130

def solve_for_y(slope: int, b: float, x: float) -> float:
    y = slope * x + b
    return float(y)

def solve_for_b(slope: int, y: float, x: float) -> float:
    b = y - (slope * x)
    return float(b)

def solve_for_x(slope:int, y: float, b: float) -> float:
    x = (y - b) / slope
    return float(x)

def ret_range(m: float, b: float, x: tuple[float, float]) -> tuple[float, float]:
    x1, x2 = x[0], x[1]
    y_range = sorted([m * x1 + b, m * x2 + b])
    return tuple(y_range)


class Call:
    def __init__(self, strike: int, premium: float) -> None:
        self.strike = strike
        self.premium = float(premium)
    
    def break_even(self) -> float:
        return self.strike + self.premium
    
    def payoff(self, spot: float) -> float:
        option_value = max(spot - self.strike, 0.0) - self.premium
        return option_value


class Put:
    def __init__(self, strike: float, premium: float) -> None:
        self.strike = strike
        self.premium = premium

    def break_even(self) -> float:
        return self.strike - self.premium
    
    def payoff(self, spot: float) -> float:
        option_value = max(self.strike - spot, 0.0) - self.premium
        return option_value

class Stock:
    def __init__(self, price_of_stock) -> None:
        self.price_of_stock = price_of_stock

class Order:
    def __init__(self, contract: Call | Put, quantity: int) -> None:
        # contract is either a Call or Put object
        self.contract = contract
        self.quantity = quantity
    
    def order_pnl(self, position: str, underlying_price: int) -> dict[str, int | float]:
        # returns a hashmap of the pnl information about the order
        price = None    
        if isinstance(self.contract, Call) or isinstance(self.contract, Put):
            price = self.contract.strike
        else:
            price = self.contract.price_of_stock

        contract_value = None
        if isinstance(self.contract, Call):
            contract_value = underlying_price - price
        elif isinstance(self.contract, Put):
            contract_value = price - underlying_price
        elif isinstance(self.contract, Stock):
            contract_value = underlying_price

        if contract_value <= 0:
            contract_value = 0

        premium = None    
        if isinstance(self.contract, Call) or isinstance(self.contract, Put):
            premium = self.contract.premium
        else:
            premium = underlying_price

        contract_pnl = None
        if position == "Long":
            contract_pnl = contract_value - premium
        elif position == "Short":
            contract_pnl = premium - contract_value
        

        pnl = {
            "Contract_Price": premium,
            "Contract_Value": contract_value, 
            "Contract_PNL": contract_pnl,
            "Total_PNL": contract_pnl * self.quantity 
            }
        
        return pnl


class Position:
    def __init__(self) -> None:
        self.longs = []
        self.shorts = []

    def buy(self, contract: Call | Put, quantity: int) -> None:
        order = Order(contract, quantity)
        self.longs.append(order)

    def sell(self, contract: Call | Put, quantity: int) -> None:
        order = Order(contract, quantity)
        self.shorts.append(order)

    def strikes(self) -> list[int]:
        # returns sorted list of all strike prices, no duplicates
        all_trades = self.longs + self.shorts
        strikes = []
        for order in all_trades:
            price = None
            if isinstance(order.contract, Call) or isinstance(order.contract, Put):
                price = order.contract.strike
            else:  # Stock
                price = order.contract.price_of_stock

            if price not in strikes:
                strikes.append(price)

        return sorted(strikes)

    def _calc_slope_for_interval(self, interval: tuple, order: Order) -> int:
        # private
        # returns the slope of contract at the given price interval
        contract_type = order.contract
        price = None
        if isinstance(contract_type, Call) or isinstance(contract_type, Put):
            price = order.contract.strike
        else:
            price = order.contract.price_of_stock

        quantity = order.quantity
        lower_bound, upper_bound = interval[0], interval[1]
        slope = 0
        if isinstance(contract_type, Call):
            if price in range(lower_bound, upper_bound) or price < lower_bound:
                if order in self.longs:
                    slope = 1
                elif order in self.shorts:
                    slope = -1
        
        elif isinstance(contract_type, Put):
            if price in range(lower_bound + 1, upper_bound + 1) or price > upper_bound:
                if order in self.longs:
                    slope = -1
                elif order in self.shorts:
                    slope = 1
        else:
            if order in self.longs:
                slope = 1
            elif order in self.shorts:
                slope = -1

        return slope * quantity
    
    def _generate_position_intervals_list(self) -> list[int]:
        # private
        # returns a formatted list of the strikes
        strikes = self.strikes()
        intv = [MIN_STRIKE]
        for i in strikes:
            intv.append(i)
        max_strike = strikes[-1] + strikes[0]
        intv.append(max_strike)

        return intv

    def _generate_position_intervals_pairs(self) -> dict[tuple, int]:
        # private
        # returns an interval-pair slope hashmap, where every key is a tuple of price pairs
        # and every value is the P&L slope of that contract at that price interval.
        # BY DEFAULT it is set to 0.
        intv = self._generate_position_intervals_list()
        intervals = {}
        for i in range(len(intv) - 1):
            interval = (intv[i], intv[i + 1])
            intervals[interval] = 0
        return intervals

    def _populate_intervals_with_order_slopes(self) -> list[tuple, int]:
        # private
        # returns a hashmap where the key is the price pair interval, and the value 
        # is the slope of the position at that price interval.
        # right now only includes strike prices
        # { (0, 90): 0, (90, 100): 0,(100, 100000): 0 }
        orders = self.longs + self.shorts
        orders_to_slopes = []
        for order in orders:
            intervals = self._generate_position_intervals_pairs()

            for interval in intervals:
                intervals[interval] = self._calc_slope_for_interval(interval, order)
            orders_to_slopes.append(intervals)

        return orders_to_slopes

    def total_slope_over_intervals(self) -> dict[tuple, int]:
        # returns the total summed interval slopes of all orders
        populated_intvs = self._populate_intervals_with_order_slopes()
        total_slope_intvs_pairs= self._generate_position_intervals_pairs()

        for intv in range(len(populated_intvs)):
            order_row = populated_intvs[intv]  # the individual order
            for pair in order_row: 
                total_slope_intvs_pairs[pair] += order_row[pair]
        
        return total_slope_intvs_pairs

    def total_pnl(self, strike_price: int) -> float:
        total_pnl = 0
        orders = self.longs + self.shorts
        for order in orders:
            if order in self.longs:
                order_pnl = order.order_pnl("Long", strike_price)
                total_pnl += order_pnl["Total_PNL"]
            elif order in self.shorts:
                order_pnl = order.order_pnl("Short", strike_price)
                total_pnl += order_pnl["Total_PNL"]
        
        return total_pnl

    def _pnl_for_strikes(self) -> dict[int, float]:
        strikes = self.strikes()
        pnls = {}
        for s in strikes:
            pnls[s] =  self.total_pnl(s)
        return pnls

    def break_evens(self) -> list[float, float]:
        interval_slopes = self.total_slope_over_intervals()
        pnls = self._pnl_for_strikes()
    
        # print(interval_slopes)
        # print(pnls)

        break_even_prices = []
        num_interval_slopes = len(interval_slopes)
        intv_num = 0
        # If it isn't clear by this amazing code,
        # First, we find the equation of the line that goes through each strike, with the pnl (y-val) of
        # each strike (x-val) and the slope (m-val) given by the slopes over intervals hashmap, to then solve for the b-val
        # Then, we plug in both bounds of the current iterated price interval (lower and upper) to find
        # their y-vals and see if y = 0 is in that range of y-vals, and if it is then we have a break even in that
        # price interval.
        for intv in interval_slopes:
            x = intv[1]
            if intv_num == num_interval_slopes - 1:
                x = intv[0]
            slope = interval_slopes[intv]
            y = pnls[x]
            b = solve_for_b(slope, y, x)
            y_range = ret_range(slope, b, intv)
            # print(f"{intv}: y = {slope}x + ({b})")
            if 0 in range(int(y_range[0]), int(y_range[1])):
                break_even = solve_for_x(slope, 0, b)
                break_even_prices.append(break_even)

            intv_num += 1

        return break_even_prices
    
    def _calc_maxes(self) -> list[float, float]:
        # pnls is NOT sorted
        interval_slopes = self.total_slope_over_intervals()
        pnls = self._pnl_for_strikes()

        break_evens = self.break_evens()
        for b in break_evens:
            pnls[b] = 0
        pos = self._generate_position_intervals_list()
    
        all_x_points = sorted(list(set(break_evens + pos)))
        # We replace the ridiculous bounds, since we now know the lowest and highest x prices (including all break evens)
        all_x_points[0] = all_x_points[1] - 5.0
        all_x_points[-1] = all_x_points[-2] + 5.0
        
        # print(interval_slopes)
        # print(pnls)
        # print(all_x_points)

        # get the max pnl from all the x prices
        loss = math.inf
        profit = -math.inf
        for i in all_x_points[1:-1]:
            if pnls[i] > profit:
                profit = pnls[i]
            if pnls[i] < loss:
                loss = pnls[i]
        
        slopes = list(interval_slopes.values())
        first_slope, last_slope = slopes[0], slopes[-1]

        maxes = {'Profit': 0, 'Loss': 0}
        if first_slope < 0 or last_slope > 0:
            profit = math.inf
            maxes['Profit'] = profit
        if first_slope > 0 or last_slope < 0:
            loss = -math.inf
            maxes['Loss'] = loss
        if first_slope == 0 or last_slope == 0:
            maxes['Profit'] = profit
            maxes['Loss'] = loss

        return maxes
        
    def max_profit(self) -> float:
        maxes = self._calc_maxes()
        return maxes['Profit'] * 100.0
    
    def max_loss(self) -> float:
        maxes = self._calc_maxes()
        return maxes['Loss'] * 100.0

    def net_cost(self) -> float:
        long_prems = []
        short_prems = []
        
        for order in self.longs:
            long_prems.append(order.contract.premium)

        for order in self.shorts:
            short_prems.append(order.contract.premium)
        
        return sum(long_prems) - sum(short_prems)

    def points_to_plot(self) -> dict[tuple[float, float]]:
        # {(0, 95): 0, (95, 190): 1}
        interval_slopes = self.total_slope_over_intervals()
        pnls = self._pnl_for_strikes()

        break_evens = self.break_evens()
        for b in break_evens:
            pnls[b] = 0
        pos = self._generate_position_intervals_list()
    
        all_x_points = sorted(list(set(break_evens + pos)))
        # We replace the ridiculous bounds, since we now know the lowest and highest x prices (including all break evens)
        all_x_points[0] = all_x_points[1] - 5.0
        all_x_points[-1] = all_x_points[-2] + 5.0
        
        # list[tuple(x, y)]
        all_points = []
        for p in all_x_points[1:-1]:
            if p in break_evens:
                all_points.append((float(p), 0.0))
            elif p in pnls:
                all_points.append((float(p), pnls[p]))
        
        first_price, last_price = all_x_points[0], all_x_points[-1]
        first_slope, last_slope = None, None
        length = len(interval_slopes)
        idx = 0
        for i in interval_slopes:
            if idx == 0:
                first_slope = interval_slopes[i]
            elif idx == length - 1:
                last_slope = interval_slopes[i]
            idx += 1
        
        b1 = solve_for_b(first_slope, pnls[all_x_points[1]], all_x_points[1])
        first_pos_val = solve_for_y(first_slope, b1, first_price)
        first_point = (first_price, first_pos_val)
        
        b2 = solve_for_b(last_slope, pnls[all_x_points[-2]], all_x_points[-2])
        last_pos_val = solve_for_y(last_slope, b2, last_price)
        last_point = (last_price, last_pos_val)

        all_points.insert(0, first_point)
        all_points.append(last_point)

        # all points should be sorted by x
        return all_points 

    def plot(self) -> None:
        fig, ax = plt.subplots()
        ax.axhline(y=0, color="grey", ls="--")
        points = self.points_to_plot()

        # Drawing Line segments
        for i in range(len(points) - 1):
            x1 = points[i][0]
            y1 = points[i][1]
            x2 = points[i + 1][0]
            y2 = points[i + 1][1]
            
            draw_line(x1, y1, x2, y2)

        # Filling in profit or loss sections
        profit_x_fill, profit_y_fill = [], []
        loss_x_fill, loss_y_fill = [], []
        break_even_dots = []
        break_even_label = []
        for i in range(len(points)):
            x = points[i][0]
            y = points[i][1]
            if y > 0:
                profit_x_fill.append(x)
                profit_y_fill.append(y)
            elif y < 0:
                loss_x_fill.append(x)
                loss_y_fill.append(y)
            else:
                profit_x_fill.append(x)
                profit_y_fill.append(y)
                loss_x_fill.append(x)
                loss_y_fill.append(y)
                break_even_dots.append((x, y))
                break_even_label.append(x)
        
        plt.fill_between(profit_x_fill, profit_y_fill, y2=0, color='green', interpolate=True, alpha=0.3)
        plt.fill_between(loss_x_fill, loss_y_fill, y2=0, color='red', interpolate=True, alpha=0.3)

        # Axis labels
        plt.ylabel("Profit or Loss at expiration")
        plt.xlabel("Underlying Price")

        # Break Even prices
        for i in break_even_dots:
            x, y = i[0], i[1]
            plt.plot(x, y, marker='o', color='orange')
        
        ax.text(
            0.06, 1.03, 
            f'Max Profit: {self.max_profit()}\nMax Loss: {self.max_loss()}\nBreak Evens: {self.break_evens()}', 
            transform=ax.transAxes,
            fontsize=8,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray')
        )

        ax.grid(True)
        plt.show()
        
def draw_line(x1, y1, x2, y2) -> None:
    plt.plot([x1, x2], [y1, y2], color='black', ls='-', lw=1, alpha=0.5)

def iron_condor(p: Position) -> None:
    p.buy(Put(90, 0.5), 1)
    p.sell(Put(95, 1.0), 1)
    p.sell(Call(105, 1.0), 1)
    p.buy(Call(110, 0.5), 1)

def straddle(p: Position) -> None:
    p.buy(Call(100, 6.5), 1)
    p.buy(Put(100, 6.5), 1)

def covered_call(p: Position) -> None:
    p.buy(Stock(95), 1)
    p.sell(Call(95, 6.25), 1)

# if __name__ == "__main__":
#     p = Position()

    # iron_condor(p)
    # staddle(p)
    # covered_call(p)

    # most advanced test-suite in the world!
    # print(p.total_slope_over_intervals())
    # print(p._pnl_for_strikes())
    # p.generate_position_intervals()
    # total_slope = p.total_slope_over_intervals()
    # print(p.break_evens())
    # print(p.max_profit(), p.max_loss())
    # print(p.net_cost())
    # p.plot()