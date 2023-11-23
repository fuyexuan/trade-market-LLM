# 导入 openai 库
import openai
import os
from dotenv import load_dotenv
import pickle
import json


def openai_login(azure=False):
    load_dotenv()
    if azure is True:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # 请替换为您的 Azure OpenAI 服务的版本
        openai.deployment_id = os.getenv("DEPLOYMENT")  # 请替换为您的 Azure OpenAI 服务的版本
        print(openai.deployment_id)
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


openai_login(azure=True)


def test1():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        deployment_id="gpt35",
        messages=[
            {"role": "system",
                # "content": "You are a vehicle on the road, equipped with data about the previous road conditions, such as traffic congestion. Your goal is to sell this data to a traffic management authority. Your name is Alice. Start your conversation using the following format:\nAlice: (Your message here)"},
#                 "content": "You are a buyer with the following personality and preferences: [friendly]. Your budget for the purchase is [1000]. In the market, there are various products available, including ['seller1': {'PrevDaySales': 30.0,\
#                                    'TotalSales': 90.0,\
#                                    'Products': {'Product1': {'Price': 200.0},\
#                                                 'Product2': {'Price': 150.0}},\
#                                    'Promotions': 'no discount'}]. \
# Now, considering your personality, budget, and the available products, make a decision on which product from a specific seller you would like to purchase.\
# Provide the following information in Python dictionary format: {'Seller':'[Seller Name]', 'Product':'[Product Name]', 'Reason':'[Your reasons for choosing this product]', 'Score':[Your score on a 10-point scale]}.\
#                            "},

            "content": "You are a seller named [seller1], managing a stall in a bustling food market, where various vendors offer their products. Today's market conditions are influenced by [{'seller1': {'PrevDaySales': 30.0,\
                                   'TotalSales': 90.0,\
                                   'Products': {'Product1': {'Price': 200.0},\
                                                'Product2': {'Price': 150.0}},\
                                   'Promotions': 'no discount'}\
                       }]. \
As a new day begins, you must make decisions on adjusting your sales strategy. You can either stick to your current approach or make changes to the products you sell and your sales strategy. Analyze the market dynamics and decide how to optimize your sales for the day. \
Provide the following information in Python dictionary format: {'Seller':'[Seller Name]', 'Products':[{'[Your Product for the new day]': {'Price': [Price for the product]} }], 'Promotions':'[Your new business strategy for the day]'}.\
                       "},
        ]
    )

    print(completion.choices[0].message)


def test2():

    instuction = "You have the ability to decide when a conversation should come to a natural conclusion. Additionally, kindly offer a brief explanation or reason for ending the conversation"
    # msg = pickle.load(open("log/jc1.pkl", "rb"))
    # json.dump(msg, open("log/jc1.json", "w+"))
    msg = json.load(open("log/jc1.json", "r"))
    messages = [
        {"role": "system", "content": instuction},
        {"role": "user", "content": msg},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100
    )
    print(msg)
    res = response.choices[0].message["content"]
    print(res)


test1()
