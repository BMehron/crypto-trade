from trading_system.indicators.exp_moving_average_handler import ExpMovingAverageHandler
from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface


class MovingAverageCDHandler(TradingSystemHandler):
    """ Moving Average Convergence/Divergence(MACD) """
    def __init__(self, trading_interface: TradingInterface, short=12, long=26, average=9):
        """
        MACD = EMA_s - EMA_l
        Signal = EMA_a(MACD)
        """
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.short = short
        self.long = long
        self.average = average
        self.short_handler = None
        self.long_handler = None

        self.macd_values = []
        self.signal_values = []

    def get_name(self):
        return f'{type(self).__name__}_s{self.short}_l{self.long}'

    def pre_add(self, handlers):
        short_handler = ExpMovingAverageHandler(self.ti, self.short)
        if short_handler.get_name() not in handlers:
            handlers.add(short_handler)
        self.short_handler = handlers[short_handler.get_name()]

        long_handler = ExpMovingAverageHandler(self.ti, self.long)
        if long_handler.get_name() not in handlers:
            handlers.add(long_handler)
        self.long_handler = handlers[long_handler.get_name()]

    def update(self):
        if not super().received_new_candle():
            return

        ema_short = self.short_handler.get_last_n_values(1)
        ema_long = self.long_handler.get_last_n_values(1)
        if len(ema_long) == 0 or len(ema_short) == 0:
            return
        ema_short = ema_short[0]
        ema_long = ema_long[0]

        self.macd_values.append(ema_short - ema_long)
        self.signal_values.append(ExpMovingAverageHandler.get_from(self.macd_values[-self.average:]))

    def get_last_n_values(self, n):
        return zip(self.macd_values[-n:], self.signal_values[-n:])
