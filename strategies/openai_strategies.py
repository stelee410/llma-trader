from llm.openai_bot import get_openai_response, get_prompt
import utils.utils as utils
import backtrader as bt

from .base import BaseStrategy

class ChaikinMoneyFlow(bt.Indicator):
    lines = ('cmf',)
    params = dict(
        period=20  # default period for CMF
    )
    
    def __init__(self):
        # Calculate the Money Flow Volume
        money_flow_volume = (self.data.close - self.data.low - self.data.high + self.data.close) / (self.data.high - self.data.low)
        money_flow_volume *= self.data.volume
        
        # Calculate the Chaikin Money Flow
        self.lines.cmf = bt.indicators.SumN(money_flow_volume, period=self.p.period) / bt.indicators.SumN(self.data.volume, period=self.p.period)

class OpenAIStrategy(BaseStrategy):
    params = (
        ('securityname', None),
        ('tickername', None),
        ('enterbars', 30),
        ('data_frame', 20),
        ('trade_freq', 14),
        ('cmf_period', 30),  # 添加CMF指标的周期作为参数
        ('sma_period', 30),  # 添加SMA指标的周期作为参数
        ('line_unit','days')
    )
    def __init__(self):
        super().__init__()
        # 添加Chaikin Money Flow指标
        self.cmf = ChaikinMoneyFlow(self.datas[0], period=self.params.cmf_period)
        
        # 添加简单移动平均线指标
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.sma_period)
    
    def notify_trade(self, trade):
        super().notify_trade(trade)
        if trade.isclosed:
            if trade.pnl < 0:
                utils.messages.append({
                    "role":"assistant",
                    "content":"持有"
                })
                utils.messages.append({
                    "role":"user",
                    "content":"我已经亏损了，亏损金额是 %.2f,你的建议是什么，请返回一个单词"%(-trade.pnl)
                })

    def get_historical_data(self):
        expected_length = self.params.data_frame
        if len(self) < expected_length:
            return None
        output = "Datetime,Open,High,Low,Close,Volume,CMF,SMA\n"
        for i in range(expected_length):
            index = i - expected_length +1
            output += "%s,%.2f,%.2f,%.2f,%.2f,%d,%.2f,%.2f\n" % (
                self.datas[0].datetime.datetime(index).isoformat(),
                self.datas[0].open[index],
                self.datas[0].high[index],
                self.datas[0].low[index],
                self.datas[0].close[index],
                self.datas[0].volume[index],
                self.cmf[index],
                self.sma[index]
            )
        return output
    def next(self):
        if self.order:
            return
        if self.last_trading_day is None:
            self.last_trading_day = self.datas[0].datetime.datetime(0)
            return
        diff = self.datas[0].datetime.datetime(0) - self.last_trading_day
        if self.params.line_unit == 'days':
            diff = diff.days
        elif self.params.line_unit == 'minutes':
            diff = diff.seconds / 60
        else:
            raise ValueError('line_unit must be days or minutes', self.params.line_unit)
        if diff < self.params.trade_freq:
            return
        self.last_trading_day = self.datas[0].datetime.datetime(0)
        historical_data = self.get_historical_data()
        if historical_data is None:
            return
        self.log('Asking OpenAI')
        #print(historical_data)
        prompt = get_prompt(historical_data, self.params.securityname, self.params.tickername)
        response = get_openai_response(prompt, utils.messages)
        if response is None:
            return
        content = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        self.log("prompt_token: " + str(prompt_tokens))
        self.log("completion_token: " + str(completion_tokens))
        utils.prompt_token += prompt_tokens
        utils.completion_token += completion_tokens

        self.log(content)
        utils.messages.append(response.choices[0].message)
        if content.find('买入') != -1:
            if self.position:
                utils.messages.append({"role":"user","content":"我已经持仓，不再买入，正在寻找更好的卖出或者持有的建议，你的建议是什么？"})
            else:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy_by_percentage(0.8)
                utils.messages.append({"role":"user","content":"我按照你的建议于%s买入，未来将寻找更好的卖出或者持有的建议，你的建议是什么？"%self.last_trading_day.isoformat()})
        elif content.find('卖出') != -1:
            if self.position:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.close()
                utils.messages.append({"role":"user","content":"我按照你的建议于%s卖出，未来将寻找更好的买入或者不交易的建议，你的建议是什么？"%self.last_trading_day.isoformat()})
            else:
                utils.messages.append({"role":"user","content":"我未持仓，不能卖出，正在寻找更好的买入或者不交易的建议，你的建议是什么？"})
        else:
            if self.position:
                utils.messages.append({"role":"user","content":"我已经持仓，正在寻找更好的卖出或者持有的建议，你的建议是什么？"})
            else:
                utils.messages.append({"role":"user","content":"我未持仓，正在寻找更好的买入或者不交易的建议，你的建议是什么？"})