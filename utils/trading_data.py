import yfinance as yf
import utils.utils as utils

def get_yfinance_data(**kwargs):
    """
    Get historical data from yfinance
    Return pandas dataframe
    :Parameters:
        on_fly: Boolean
            if True, will not use cache
        parse_dates : str array
            The array for dates columns
        tickername : str
            Ticker name, e.g. "MSFT", "AAPL"
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime, inclusive.
            Default is 99 years ago
            E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
        end: str
            Download end date string (YYYY-MM-DD) or _datetime, exclusive.
            Default is now
            E.g. for end="2023-01-01", the last data point will be on "2022-12-31"
        prepost : bool
            Include Pre and Post market data in results?
            Default is False
        auto_adjust: bool
            Adjust all OHLC automatically? Default is True
        back_adjust: bool
            Back-adjusted data to mimic true historical prices
        repair: bool
            Detect currency unit 100x mixups and attempt repair.
            Default is False
        keepna: bool
            Keep NaN rows returned by Yahoo?
            Default is False
        proxy: str
            Optional. Proxy server URL scheme. Default is None
        rounding: bool
            Round values to 2 decimal places?
            Optional. Default is False = precision suggested by Yahoo!
        timeout: None or float
            If not None stops waiting for a response after given number of
            seconds. (Can also be a fraction of a second e.g. 0.01)
            Default is 10 seconds.
        debug: bool
            If passed as False, will suppress message printing to console.
            DEPRECATED, will be removed in future version
        raise_errors: bool
            If True, then raise errors as Exceptions instead of logging.
    """
    uuid = utils.get_dict_uuid(kwargs)
    tickername = kwargs.pop('tickername', None)
    parse_dates = kwargs.pop('parse_dates', ["Datetime"])
    on_fly = kwargs.pop('on_fly', True)

    if on_fly is False and utils.is_cached(uuid):
        hist_data =  utils.load_data(uuid,parse_dates)
        return hist_data,uuid
    if tickername is None:
        raise ValueError("ticker_name must be specified")
    ticker = yf.Ticker(tickername)
    hist_data = ticker.history(**kwargs)
    if on_fly is False:
        utils.dump_data(hist_data, uuid)
    return hist_data, uuid
