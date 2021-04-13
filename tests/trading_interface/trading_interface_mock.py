from __future__ import annotations

from trading import Candle, AssetPair, Order
from trading_interface.trading_interface import TradingInterface
import typing as tp


class TradingInterfaceMock(TradingInterface):
    def __init__(self, all_candles: tp.Optional[tp.List[Candle]] = None):
        if all_candles is None:
            all_candles = []
        self.all_candles = all_candles
        self.processed_candles: tp.List[Candle] = []

    @classmethod
    def from_price_values(cls, values: tp.List[float]) -> TradingInterfaceMock:
        candles = [Candle(
            ts=i,
            open=values[i],
            close=values[i + 1],
            low=min(values[i], values[i + 1]),
            high=max(values[i], values[i + 1]),
            volume=1) for i in range(len(values) - 1)]
        return cls(candles)

    def refresh(self) -> None:
        self.processed_candles = []

    def update(self) -> bool:
        if len(self.processed_candles) < len(self.all_candles):
            self.processed_candles.append(
                self.all_candles[len(self.processed_candles)])
            return True
        return False

    def is_alive(self) -> bool:
        return len(self.processed_candles) < len(self.all_candles)

    def get_timestamp(self) -> int:
        return len(self.processed_candles)

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        return self.processed_candles[-n:]

    def buy(self, amount: float, price: float) -> Order:
        pass

    def cancel_all(self) -> None:
        pass

    def cancel_order(self, order: Order) -> None:
        pass

    def get_buy_price(self) -> float:
        pass

    def get_sell_price(self) -> float:
        pass

    def order_is_filled(self, order: Order) -> bool:
        pass

    def sell(self, amount: float, price: float) -> Order:
        pass

    def stop_trading(self) -> None:
        pass

    def get_orderbook(self):  # type: ignore
        pass
