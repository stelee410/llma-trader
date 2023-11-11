from runner import backtesting
import utils.utils as utils
from argsense import cli

@cli.cmd()
def yearly_trade(tickername, securityname,strategy='openai'):
    cerebro = backtesting.run(strategy=strategy, tickername=tickername,securityname=securityname)
    print("total prompt_token: " + str(utils.prompt_token))
    print("total completion_token: " + str(utils.completion_token))
    cerebro.plot()

@cli.cmd()
def daily_trade(tickername, securityname,strategy='openai'):
    cerebro = backtesting.run(strategy=strategy, 
                              tickername=tickername,
                              securityname=securityname,
                              period = '1d',
                              interval = '1m',
                              enterbars = 30,
                              data_frame = 30,
                              trade_freq = 60,
                              cmf_period = 20,
                              sma_period = 20,
                              line_unit = 'minutes'
                              )
    print("total prompt_token: " + str(utils.prompt_token))
    print("total completion_token: " + str(utils.completion_token))
    cerebro.plot()

@cli.cmd()
def five_d_trade(tickername, securityname, strategy='openai'):
    cerebro = backtesting.run(strategy=strategy, 
                              tickername=tickername,
                              securityname=securityname,
                              period = '5d',
                              interval = '1m',
                              enterbars = 480,
                              data_frame = 300,
                              trade_freq = 238, #every 4 hours trading once
                              cmf_period = 240,
                              sma_period = 480,
                              line_unit = 'minutes'
                              )
    print("total prompt_token: " + str(utils.prompt_token))
    print("total completion_token: " + str(utils.completion_token))
    cerebro.plot()

@cli.cmd()
def future_trade(tickername, securityname, strategy='dry'):
    tickername = tickername + "=F" #e.g. CL=F
    cerebro = backtesting.run_future(strategy=strategy, 
                              tickername=tickername,
                              securityname=securityname,
                              commission=1.25, #每手手续费
                              margin=2000, #保证金
                              mult=10 #一份合约规模
                              )
    print("total prompt_token: " + str(utils.prompt_token))
    print("total completion_token: " + str(utils.completion_token))
    cerebro.plot()

if __name__ == '__main__':
    cli.run()