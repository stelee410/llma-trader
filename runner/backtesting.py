import backtrader as bt
from utils.trading_data import get_yfinance_data
from strategies import load_strategy

def run(**kwargs):
    """
    Runs the backtesting strategy.
    :Parameters:
        init_cash : float
            Initial cash for the strategy. Default is 100000.0.
        securityname : str
            Name of the security. Default is 'unspecified'.
        tickername : str
            Ticker symbol of the security. Must be specified.
        strategy : str
            Name of the strategy to be used. Must be specified, 
            The possible value would be:
            'dry' | 'openai'.
        commission : float
            Commission for each transaction. Default is 0.001.
        ... : ...
            Other parameters for the strategy would be passed to the strategy.
    """
    init_cash = kwargs.get('init_cash', 100000.0)
    tickername = kwargs.get('tickername', None) #e.g. GOOG
    strategy = kwargs.get('strategy', None)
    commission = kwargs.get('commission', 0.001)
    period = kwargs.get('period', '1y')
    interval = kwargs.get('interval', '1h')
    if tickername is None:
        raise ValueError('tickername is not specified')
    if strategy is None:
        raise ValueError('strategy is not specified')
    strategy = load_strategy(strategy)
    
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(init_cash)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    raw_data,__ = get_yfinance_data(tickername=tickername, period=period, interval=interval)
    if raw_data.empty:
        raise ValueError('The DataFrame is empty for ', tickername)

    data = bt.feeds.PandasData(dataname=raw_data)
    cerebro.broker.setcommission(commission=commission)
    cerebro.adddata(data)

    params = {}
    for key, value in strategy.params._getitems():
        params[key] = kwargs.get(key, value)
    cerebro.addstrategy(strategy,
                        **params
                        )
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    return cerebro


def run_future(**kwargs):
    """
    Runs the backtesting strategy.
    :Parameters:
        init_cash : float
            Initial cash for the strategy. Default is 100000.0.
        securityname : str
            Name of the security. Default is 'unspecified'.
        tickername : str
            Ticker symbol of the security. Must be specified.
        strategy : str
            Name of the strategy to be used. Must be specified, 
            The possible value would be:
            'dry' | 'openai'.
        commission : float
            Commission for each transaction. Default is 0.001.
        margin : int
            Margin for each transaction. Default is 2000.
        mult : int
            Multiplier for each transaction. Default is 10.
        ... : ...
            Other parameters for the strategy would be passed to the strategy.
    """
    init_cash = kwargs.get('init_cash', 100000.0)
    tickername = kwargs.get('tickername', None) #e.g. GOOG
    strategy = kwargs.get('strategy', None)
    commission = kwargs.get('commission', 0.001)
    period = kwargs.get('period', '1y')
    interval = kwargs.get('interval', '1h')
    margin = kwargs.get('margin', 2000)
    mult = kwargs.get('mult', 10)

    if tickername is None:
        raise ValueError('tickername is not specified')
    if strategy is None:
        raise ValueError('strategy is not specified')
    strategy = load_strategy(strategy)

    
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(init_cash)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    raw_data,__ = get_yfinance_data(tickername=tickername, period=period, interval=interval,on_fly = True)
    if raw_data.empty:
        raise ValueError('The DataFrame is empty for ', tickername)

    data = bt.feeds.PandasData(dataname=raw_data)
    cerebro.broker.setcommission(commission=commission,margin=margin,mult=mult,commtype=bt.CommInfoBase.COMM_FIXED)
    cerebro.adddata(data)

    params = {}
    for key, value in strategy.params._getitems():
        params[key] = kwargs.get(key, value)
    cerebro.addstrategy(strategy,
                        **params
                        )
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    return cerebro