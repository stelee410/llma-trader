from llm.openai_bot import get_openai_response
from utils.trading_data import get_yfinance_data
from dateutil.relativedelta import relativedelta
import utils.utils as utils
import backtrader as bt
import json

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
        breakpoint()
        self.lines.cmf = bt.indicators.SumN(money_flow_volume, period=self.p.period) / bt.indicators.SumN(self.data.volume, period=self.p.period)


class OpenAIFutureStrategy(BaseStrategy):
    params = (
        ('securityname', None),
        ('tickername', None),
        ('trade_freq', 14),
        ('data_frame', 28),#数据窗口，按照日计算，所以后面参数具体使用的时候需要乘以23
        ('startN', 0), #开始交易时间，按照日计算，所以后面参数具体使用的时候需要乘以23
        ('cmf_period', 28),  # 添加CMF指标的周期作为参数
        ('sma_period', 28),  # 添加SMA指标的周期作为参数
    )
    def __init__(self):
        super().__init__()
        # 添加Chaikin Money Flow指标
        #self.cmf = ChaikinMoneyFlow(self.datas[0], period=self.params.cmf_period*23)
        
        # 添加简单移动平均线指标
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.sma_period*23)

    
    def notify_trade(self, trade):
        super().notify_trade(trade)
        # if trade.isclosed:
        #     if trade.pnl < 0:
        #         utils.messages.append({
        #             "role":"assistant",
        #             "content":"目前收益"
        #         })
        #         utils.messages.append({
        #             "role":"user",
        #             "content":"我已经亏损了，亏损金额是 %.2f,你的建议是什么，请返回一个单词"%(-trade.pnl)
        #         })

    def get_historical_data(self):
        expected_length = self.params.data_frame * 23
        if len(self) < expected_length:
            return None
        output = "Datetime,Open,High,Low,Close,Volume,SMA\n"
        for i in range(expected_length):
            index = i - expected_length +1
            output += "%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n" % (
                self.datas[0].datetime.datetime(index).isoformat(),
                self.datas[0].open[index],
                self.datas[0].high[index],
                self.datas[0].low[index],
                self.datas[0].close[index],
                self.datas[0].volume[index],
                self.sma[index]
            )
        return output
    def get_yearly_data(self):
        current_date = self.datas[0].datetime.date(0)
        start_date = current_date - relativedelta(months=3)

        end_date = current_date.strftime('%Y-%m-%d')
        start_date = start_date.strftime('%Y-%m-%d')

        print("get yearly data from %s to %s"%(start_date,end_date))

        df = get_yfinance_data(tickername=self.params.tickername, start = start_date, end = end_date, interval='1d')
        return df[0].to_csv()


    def get_prompt(self,df_d,df_y = ""):
        return f"""
You are an excellent trader. You are trading {self.params.securityname}({self.params.tickername}) future contract.
Analyze the datas delimited by triple backticks.
You are smart to choose your own stradegy. I am testing your capability of making decision.
You must notice the following points:
    - Consider the price and the volume
    - If it is getting to close to the point of highest price, you must sell. If it is getting to close to the point of lowest price, you must buy.
    - If the trend is getting up from down, you should buy, if the trend is getting down from up, you should sell.
    - Consider the last user action, if last action is buy and the price is high enough, you should sell. If last action is sell and the price is low enough, you should buy.

The output action string can only be "buy","sell" or "hold". The format of output can only be:
/<action> <explanation>

the explanation should be short and the action should be one of "buy","sell" or "hold". Or you will get a low score.
```
{df_d}
```
```
{df_y}
```
"""

    def next(self):
        if self.order:
            return
        if self.last_trading_day is None:
            self.last_trading_day = self.datas[0].datetime.datetime(0)
            return
        if len(self)<self.params.startN * 23:
            return
        diff = (self.datas[0].datetime.datetime(0) - self.last_trading_day).days
    
        if diff < self.params.trade_freq:
            return
        self.last_trading_day = self.datas[0].datetime.datetime(0)
        historical_data = self.get_historical_data()
        yearly_data = self.get_yearly_data()
        if historical_data is None:
            return
        self.log('Asking OpenAI...')
        prompt = self.get_prompt(historical_data,yearly_data)
        response = get_openai_response(prompt, utils.messages)
        if response is None:
            return
        response_message = response["choices"][0]["message"].get("content")
        utils.messages.append(response["choices"][0]["message"])
        self.log(response_message)
        if response_message.find("buy") != -1 and response_message.find("sell") != -1:
            action = "hold"
        else:
            if response_message.find("buy") != -1:
                action = "buy"
            elif response_message.find("sell") != -1:
                action = "sell"
            else:
                action = "hold"

        # if response_message.get("function_call") is None:
        #     return
        # function_name = response_message["function_call"]["name"]
        # if function_name !="get_trading_action":
        #     return
        # function_args = json.loads(response_message["function_call"]["arguments"])
        # action = function_args.get("action")
        # explain = function_args.get("explain")
              
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        self.log("prompt_token: " + str(prompt_tokens))
        self.log("completion_token: " + str(completion_tokens))
        utils.prompt_token += prompt_tokens
        utils.completion_token += completion_tokens
        # self.log("action: %s, explain: %s"%(action,explain))
        if not self.position:
            # 获取保证金要求（例如，每份合约的保证金）
            comminfo = self.broker.getcommissioninfo(self.data)
            margin_per_contract = comminfo.margin
            
            # 获取账户价值
            account_value = self.broker.getvalue()
            
            # 确定保证金安全系数，例如保持至少50%的余额作为安全缓冲
            margin_safety_buffer = 0.5

            # 计算最大可以买入的合约数
            max_contracts = int((account_value * margin_safety_buffer) / margin_per_contract)
            if max_contracts == 0:
                self.log('Not enough cash')
                self.env.runstop()
                return
            if action == 'buy':
                self.log('buy, %.2f' % self.dataclose[0])
                self.buy(size=max_contracts)
                utils.messages.append({
                    "role":"user",
                    "content":('user buy at price of %.2f,which action to take next?' % self.dataclose[0])
                })
            elif action == 'sell':
                self.log('sell, %.2f' % self.dataclose[0])
                self.sell(size=max_contracts)  
                utils.messages.append({
                    "role":"user",
                    "content":('user sell at price of %.2f,which action to take next?' % self.dataclose[0])
                })
            else:
                utils.messages.append({
                    "role":"user",
                    "content":('which action to take next?')
                })
        else:
            possize = self.getposition(self.data, self.broker).size
    
            if possize > 0:
                if action == 'sell':
                    self.log('sell, %.2f' % self.dataclose[0])
                    self.close()
                    utils.messages.append({
                        "role":"user",
                        "content":('user sell at price of %.2f,which action to take next?' % self.dataclose[0])
                    })
                else:
                    utils.messages.append({
                        "role":"user",
                        "content":('which action to take next?')
                    })
            else:
                if action == 'buy':
                    self.log('buy, %.2f' % self.dataclose[0])
                    self.close()
                    utils.messages.append({
                        "role":"user",
                        "content":('user buy at price of %.2f, which action to take next?' % self.dataclose[0])
                    })
                else:
                    utils.messages.append({
                        "role":"user",
                        "content":('which action to take next?')
                    })
                
    
    def stop(self):
        self.close()  # 平掉所有仓位