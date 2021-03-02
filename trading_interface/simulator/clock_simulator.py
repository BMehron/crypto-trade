from logger.clock import Clock


class ClockSimulator(Clock):
    def __init__(self, start, timeframe, candles_lifetime):
        self.start = start
        self.seconds_per_candle = timeframe * 60
        self.candles_lifetime = candles_lifetime
        self.iteration = 0

    def get_timestamp(self):
        return self.start + self.iteration / self.candles_lifetime * self.seconds_per_candle

    def get_current_candle_lifetime(self):
        return self.iteration % self.candles_lifetime

    def next_iteration(self):
        self.iteration += 1

    def get_iterated_candles_cnt(self):
        return self.iteration // self.candles_lifetime
