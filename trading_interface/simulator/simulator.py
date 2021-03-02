import datetime

from trading_interface.trading_interface import TradingInterface
from market_data_api.market_data_downloader import MarketDataDownloader

from trading.order import Order, Direction
from trading.asset import AssetPair

PRICE_SHIFT = 0.001


class Simulator(TradingInterface):
    def __init__(self, asset_pair: AssetPair, timeframe, from_ts, to_ts, clock):
        ts_offset = int(datetime.timedelta(days=1).total_seconds())
        self.candles = MarketDataDownloader().get_candles(
            asset_pair, timeframe, from_ts - ts_offset, to_ts)
        self.candle_index_offset = ts_offset // (timeframe * 60)
        self.clock = clock
        self.active_orders = []
        self.last_used_order_id = 0
        self.filled_order_ids = set()
        self.balance = 0

    def is_alive(self):
        self.__fill_orders()
        self.clock.next_iteration()
        return self.__get_current_candle_index(truncated_index=False) < len(self.candles)

    def get_timestamp(self):
        return self.clock.get_timestamp()

    def get_balance(self):
        return self.balance

    def buy(self, asset_pair: AssetPair, amount: int, price: float):
        order = Order(self.__get_new_order_id(), asset_pair, amount, price, Direction.BUY)
        self.active_orders.append(order)
        return order

    def sell(self, asset_pair: AssetPair, amount: int, price: float):
        order = Order(self.__get_new_order_id(), asset_pair, amount, price, Direction.SELL)
        self.active_orders.append(order)
        return order

    def cancel_order(self, order: Order):
        pass

    def order_is_filled(self, order: Order):
        return order.order_id in self.filled_order_ids

    def get_sell_price(self):
        return self.__get_current_price() * (1 + PRICE_SHIFT)

    def get_buy_price(self):
        return self.__get_current_price() * (1 - PRICE_SHIFT)

    def get_last_n_candles(self, n: int):
        candle_index = self.__get_current_candle_index()
        return self.candles[max(0, candle_index - n): candle_index]

    def __fill_orders(self):
        order_is_filled = lambda order: (order.direction == Direction.BUY and order.price > self.get_sell_price()) or \
                                        (order.direction == Direction.SELL and order.price < self.get_buy_price())
        filled_orders = list(filter(order_is_filled, self.active_orders))
        self.active_orders = list(filter(lambda order: not order_is_filled(order), self.active_orders))
        for order in filled_orders:
            self.filled_order_ids.add(order.order_id)
            self.balance += int(order.direction) * order.price * order.amount

    def __get_current_price(self):
        candle = self.candles[self.__get_current_candle_index()]
        return candle.open + \
               candle.get_delta() * (self.clock.get_current_candle_lifetime() / self.clock.candles_lifetime)

    def __get_current_candle_index(self, truncated_index=True):
        index = self.candle_index_offset + self.clock.get_iterated_candles_cnt()
        if not truncated_index:
            return index
        return min(index, len(self.candles) - 1)

    def __get_new_order_id(self):
        self.last_used_order_id += 1
        return self.last_used_order_id
