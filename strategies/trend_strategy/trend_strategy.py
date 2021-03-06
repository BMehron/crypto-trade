import typing as tp

import trading_system.trading_system as ts

from helpers.typing.common_types import Config
from strategies.strategy_base import StrategyBase
from logger.logger import Logger

from trading_system.indicators import TrendHandler
from trading import Trend, TrendType, Asset, AssetPair


class TrendStrategy(StrategyBase):
    def __init__(self, config: Config) -> None:
        self.asset_pair = AssetPair(*config['asset_pair'])
        self.logger = Logger('TrendStrategy')
        self.order_balance = 0
        self.active_trends: tp.List[Trend] = []
        self.ts: tp.Optional[ts.TradingSystem] = None

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system
        self.ts.add_handler(TrendHandler, params={})

    def update(self) -> None:
        assert self.ts is not None
        active_trends = []
        for trend in self.active_trends:
            deactivated = False
            if trend.trend_type == TrendType.UPTREND:
                if trend.lower_trend_line.get_value_at(  # type: ignore
                        self.ts.get_timestamp()) >= self.ts.get_buy_price():
                    self.ts.sell(self.asset_pair, 1, self.ts.get_buy_price())
                    deactivated = True
            else:
                if trend.upper_trend_line.get_value_at(  # type: ignore
                        self.ts.get_timestamp()) <= self.ts.get_sell_price():
                    self.ts.buy(self.asset_pair, 1, self.ts.get_sell_price())
                    deactivated = True
            if not deactivated:
                active_trends.append(trend)
            else:
                self.order_balance -= 1
        self.active_trends = active_trends

    def handle_new_trend_signal(self, trend: Trend) -> None:
        assert self.ts is not None
        self.logger.info(f'Strategy received trend of type {trend.trend_type}')

        if self.order_balance > 3:
            return

        if trend.trend_type == TrendType.UPTREND:
            self.ts.buy(self.asset_pair, 1, self.ts.get_sell_price())
        else:
            self.ts.sell(self.asset_pair, 1, self.ts.get_buy_price())
        self.active_trends.append(trend)
        self.order_balance += 1
