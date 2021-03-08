import sys

sys.path.append('.')

import os
import pickle
import logger.log_events as log_events
import typing as tp
from pathlib import Path
from collections import defaultdict
from visualizer import Visualizer
from logger.object_log import PATH_TO_DUMPS


def get_log_path():
    path = Path(sys.argv[1] if len(sys.argv) == 2 else PATH_TO_DUMPS)
    logs = list(path.rglob('*.dump')) if path.is_dir() else [path]
    if len(logs) == 0:
        return None
    return max(logs, key=os.path.getctime)


def load_log(filename):
    with open(filename, 'rb') as f:
        log = pickle.load(f)
    return log


def decompose_log(log: tp.List[tp.Mapping[str, tp.Any]]):
    events = defaultdict(list)
    for event in log:
        events[event['event_type']].append(event)
    return events


def get_candles(candles_log):
    return [candle['candle'] for candle in candles_log]


def process_buy_sell_events(events):
    timestamps = [event['ts'] for event in events]
    amounts = [event['amount'] for event in events]
    prices = [event['price'] for event in events]
    meta = events.copy()
    for i, item in enumerate(meta):
        item.pop('event_type')
        meta[i] = '<br>'.join(
            str(key) + ': ' + str(value) for key, value in item.items())
    return timestamps, prices, amounts, meta


def decompose_moving_average(moving_averages):
    ma_by_window = defaultdict(list)
    for event in moving_averages:
        ma_by_window[event['window_size']].append(event)
    return ma_by_window


if __name__ == '__main__':
    path = get_log_path()
    print(path)
    log = load_log(path)
    decomposed_log = decompose_log(log)
    vis = Visualizer()
    vis.add_candles(get_candles(decomposed_log[log_events.NewCandleEvent]))
    vis.add_trend_lines(decomposed_log[log_events.TrendLinesEvent])
    for window_size, moving_average in decompose_moving_average(
            decomposed_log[log_events.MovingAverageEvent]).items():
        vis.add_moving_average(moving_average, window_size)
    vis.add_buy_events(
        *process_buy_sell_events(decomposed_log[log_events.BuyEvent]))
    vis.add_sell_events(
        *process_buy_sell_events(decomposed_log[log_events.SellEvent]))
    fig = vis.plot()
    fig.show()
