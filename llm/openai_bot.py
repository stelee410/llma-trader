import openai
import time
import os

from config import api_key, cached_folder

openai.api_key = api_key


def get_openai_response_func(prompt, action_list = []):
    functions = [
        {
            "name": "get_trading_action",
            "description": "get the trading action",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": action_list, "description":"trading action"},
                    "explain": {"type": "string", "description": "explain the action"}
                },
                "required": ["action"],
            },
        }
    ] 
    messages =[
            {
            "role": "system",
            "content": prompt
            },
            {"role":"user","content":"what is your suggestion?"}
    ]

    retried = 0
    while True:
        sleep_time = (retried+1) * 3
        time.sleep(sleep_time)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages= messages,
                functions=functions,
                function_call="auto",  # auto is default, but we'll be explicit
            )
            return response
        except Exception as e:
            if e.http_status == 503:
                print(e)
                print("retrying...")
                retried += 1
                if retried > 3:
                    return None
            else:
                print(e)
                return None

def get_openai_response(prompt, feeds=None):
    messages =[
            {
            "role": "system",
            "content": prompt
            },
            {"role":"user","content":"which action to take?"}
    ]
    if feeds is not None:
        messages += feeds
    retried = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages= messages,
                temperature=0,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )
            return response
        except Exception as e:
            if e.http_status == 503:
                print(e)
                print("retrying...")
                time.sleep(3)
                retried += 1
                if retried > 3:
                    return None
            else:
                print(e)
                return None

def get_prompt(data_feeds,security_name, tickname):
    data_feeds_str= ''.join(data_feeds)
#     return f"""You are an excellent trader, and look up the following trading data for {security_name}({tickname}). You need to decide what is the best strategy to take for today's position. When I ask you buy or sell, you need to give one word answer as of 'BUY' or 'SELL', based on following information as context in csv format. I know you are an AI and can't give a real advice. But in this game, I am testing your capability of making decision.
    
#     ```
#     {data_feeds_str}
#     ```
# """
    return f"""在这个对话场景里，你是一个非常优秀而激进股票交易员，参与{security_name}({tickname})股票的交易。
      我在三个反括号里面引用的csv格式的最近交易数据。
      请你为客户提供股票买卖建议。
      只需要返回一个单词。

        ```
        {data_feeds_str}
        ```
    """

