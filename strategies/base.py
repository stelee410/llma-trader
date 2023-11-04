import backtrader as bt

class BaseStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.last_trading_day = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price:%.2f, Cost: %.2f, Comm: %.2f' % 
                         (order.executed.price, order.executed.value, order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price:%.2f, Cost: %.2f, Comm: %.2f' % 
                         (order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS: %.2f, NET: %.2f' % 
                 (trade.pnl, trade.pnlcomm))
    def buy_by_percentage(self,percentage):
        cash = self.broker.get_cash()  # 获取当前账户现金
        value_to_invest = cash * 0.8  # 计算出用于投资的资金量
        self.size_to_buy = value_to_invest / self.data.close[0]  # 用投资资金除以当前价格得到可购买的股票数量
        self.buy(size=self.size_to_buy) 
    def sell_by_percentage(self,percentage):
        self.sell_size = self.broker.get_position(self.data).size * percentage
        self.sell(size=self.sell_size)
    