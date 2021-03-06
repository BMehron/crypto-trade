from __future__ import annotations

import typing as tp

from collections import OrderedDict
from copy import copy
import math

from helpers.typing.common_types import Config
from trading_interface.trading_interface import TradingInterface

from trading_system.candles_handler import CandlesHandler
from trading_system.orders_handler import OrdersHandler
from trading_system.indicators import *

from trading_system.trading_statistics import TradingStatistics

from logger.log_events import BuyEvent, SellEvent, CancelEvent
from logger.logger import Logger

from trading import Asset, AssetPair, Signal, Order, Direction, Candle

from helpers.typing import TradingSystemHandlerT
from helpers.typing.utils import require


class Handlers(OrderedDict):  # type: ignore
    def add(self, handler: TradingSystemHandler) -> Handlers:
        if handler.get_name() in self.keys():
            return self

        handlers = handler.get_required_handlers()
        for i, dependent_handler in enumerate(handlers):
            if dependent_handler.get_name() in self.keys():
                handlers[i] = self[dependent_handler.get_name()]
            else:
                self.add(dependent_handler)

        handler.link_required_handlers(handlers)
        self[handler.get_name()] = handler
        return self


class TradingSystem:
    def __init__(self, trading_interface: TradingInterface, config: Config):
        self.logger = Logger('TradingSystem')
        self.ti = trading_interface
        self.currency_asset = Asset(config['currency_asset'])
        self.wallet: tp.Dict[Asset, float] = {Asset(asset_name): amount
            for asset_name, amount in config['wallet'].items()}
        self.stats = TradingStatistics(
            price_asset=self.currency_asset,
            initial_wallet=self.wallet,
            initial_balance=self.get_total_balance(),
            start_timestamp=self.ti.get_timestamp(),
            initial_coin_balance=self.get_total_coin_balance())
        self.trading_signals: tp.List[Signal] = []
        self.handlers = Handlers() \
            .add(CandlesHandler(trading_interface)) \
            .add(OrdersHandler(trading_interface))
        self.logger.info('Trading system initialized')

    def add_handler(self, handler_type: tp.Any, params: tp.Dict[str, tp.Any]) -> TradingSystemHandlerT:
        handler = handler_type(trading_interface=self.ti, **params)
        self.handlers.add(handler)
        return self.handlers[handler.get_name()]

    def stop_trading(self) -> None:
        self.cancel_all()
        self.update()

    def get_trading_statistics(self) -> TradingStatistics:
        stats = copy(self.stats)
        stats.set_hodl_result(require(self.stats.initial_coin_balance) * self.ti.get_sell_price())
        stats.set_final_wallet(self.get_wallet())
        stats.set_final_balance(self.get_total_balance())
        stats.set_finish_timestamp(self.get_timestamp())
        return stats

    def update(self) -> None:
        for handler in self.handlers.values():
            handler.update()
        for order in self.get_handler(OrdersHandler).get_new_filled_orders():
            self._handle_filled_order(order)
            self.trading_signals.append(Signal('filled_order', copy(order)))

    def get_trading_signals(self) -> tp.List[Signal]:
        signals = self.trading_signals
        self.trading_signals = []
        return signals

    def exchange_is_alive(self) -> bool:
        return self.ti.is_alive()

    def get_timestamp(self) -> int:
        return self.ti.get_timestamp()

    def create_order(self, asset_pair: AssetPair, amount: float) -> tp.Optional[Order]:
        if amount > 0:
            return self.buy(asset_pair, amount, self.get_sell_price())
        elif amount < 0:
            return self.sell(asset_pair, -amount, self.get_buy_price())
        return None

    def buy(self, asset_pair: AssetPair, amount: float, price: float) -> tp.Optional[Order]:
        if self.wallet[asset_pair.price_asset] < price * amount:
            self.logger.warning(
                f"Not enough {asset_pair.price_asset}. "
                f"Order is not placed.")
            return None
        self.wallet[asset_pair.price_asset] -= price * amount
        order = self.ti.buy(amount, price)
        if not order:
            return None
        self.logger.trading_event(BuyEvent(asset_pair,
                                           amount,
                                           price,
                                           order.order_id))
        self.get_handler(OrdersHandler).add_new_order(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: float, price: float) -> tp.Optional[Order]:
        if self.wallet[asset_pair.amount_asset] < amount:
            self.logger.warning(
                f"Not enough {asset_pair.amount_asset}. "
                f"Order is not placed.")
            return None
        self.wallet[asset_pair.amount_asset] -= amount
        order = self.ti.sell(amount, price)
        if not order:
            return None
        self.logger.trading_event(SellEvent(asset_pair,
                                            amount,
                                            price,
                                            order.order_id))
        self.get_handler(OrdersHandler).add_new_order(copy(order))
        return order

    def cancel_order(self, order: Order) -> None:
        self.ti.cancel_order(order)
        self._handle_canceled_order(order)

    def cancel_all(self) -> None:
        self.ti.cancel_all()
        active_orders = self.get_handler(OrdersHandler).get_active_orders()
        for order in active_orders:
            self._handle_canceled_order(order)

    def order_is_filled(self, order: Order) -> bool:
        return self.ti.order_is_filled(order)

    def get_price_by_direction(self, direction: Direction) -> float:
        return self.get_buy_price() if direction == Direction.BUY else self.get_sell_price()

    def get_buy_price(self) -> float:
        return self.ti.get_buy_price()

    def get_sell_price(self) -> float:
        return self.ti.get_sell_price()

    def get_active_orders(self) -> tp.Set[Order]:
        return self.get_handler(OrdersHandler).get_active_orders()

    def get_balance(self) -> float:
        balance = self.wallet[self.currency_asset]
        self.logger.info(f'Checking balance: {balance}')
        return balance

    def get_total_coin_balance(self) -> float:
        total_coins = 0.0
        for asset, amount in self.wallet.items():
            if asset != self.currency_asset:
                total_coins += amount
            else:
                if not math.isclose(require(self.ti.get_buy_price()), 0):
                    total_coins += amount / self.ti.get_buy_price()
        return total_coins

    def get_total_balance(self) -> float:
        total_balance = 0.0
        for asset, amount in self.wallet.items():
            if asset == self.currency_asset:
                total_balance += amount
            else:
                direction = Direction.from_value(-amount)
                total_balance += amount * self.get_price_by_direction(direction)
        return total_balance

    def get_wallet(self) -> tp.Dict[Asset, float]:
        self.logger.info(f'Checking wallet: {self.wallet.items()}')
        return copy(self.wallet)

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        return self.ti.get_last_n_candles(n)

    def get_handler(self, cls: tp.Type[TradingSystemHandlerT]) \
            -> TradingSystemHandlerT:
        return self.handlers[cls.__name__]

    def _handle_canceled_order(self, order: Order) -> None:
        self.get_handler(OrdersHandler).cancel_order(order)
        if order.direction == Direction.BUY:
            self.wallet[order.asset_pair.price_asset] += order.price * order.amount
        else:  # Direction.SELL
            self.wallet[order.asset_pair.amount_asset] += order.amount
        self.logger.trading_event(CancelEvent(order))

    def _handle_filled_order(self, order: Order) -> None:
        if order.direction == Direction.BUY:
            self.wallet[order.asset_pair.amount_asset] += order.amount
        else:  # Direction.SELL
            self.wallet[order.asset_pair.price_asset] += order.price * order.amount
        self.stats.add_filled_order(copy(order))
