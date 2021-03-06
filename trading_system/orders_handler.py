import typing as tp

from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface

from trading import Order

from logger.log_events import FilledOrderEvent
from logger.logger import Logger
from copy import copy


class OrdersHandler(TradingSystemHandler):
    def __init__(self, trading_interface: TradingInterface):
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.logger = Logger("OrdersHandler")
        self.active_orders: tp.Set[Order] = set()
        self.new_filled_orders: tp.Set[Order] = set()

    def update(self) -> bool:
        filled_orders = set(
            filter(self.ti.order_is_filled, self.active_orders))
        for order in filled_orders:
            self.logger.trading_event(FilledOrderEvent(order.order_id))
        self.new_filled_orders |= filled_orders
        self.active_orders = self.active_orders - filled_orders
        return len(filled_orders) > 0

    def get_active_orders(self) -> tp.Set[Order]:
        return copy(self.active_orders)

    def get_new_filled_orders(self) -> tp.Set[Order]:
        orders = self.new_filled_orders
        self.new_filled_orders = set()
        return orders

    def add_new_order(self, order: Order) -> None:
        self.active_orders.add(order)

    def cancel_order(self, order: Order) -> None:
        self.active_orders.discard(order)

    def cancel_all(self) -> None:
        self.active_orders.clear()
