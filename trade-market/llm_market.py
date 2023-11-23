# 导入 openai 库
import openai
import os
from dotenv import load_dotenv
import logging
import copy
import pickle
import json
import re
import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(process)d \n\t %(" "message)s",
    filename="log/trade.log",
)


def openai_login(azure=False):
    load_dotenv()
    if azure is True:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # 请替换为您的 Azure OpenAI 服务的版本
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


openai_login(azure=True)
# openai_login(azure=False)


class Agent:
    def __init__(self, role, name, type="", personality=""):
        self.role = role
        self.name = name
        self.type = type
        self.personality = personality

    def evaluate(self):
        pass

    def decision(self, env_information):
        instruction = ""
        instruction += self.get_input_content(env_information)
        instruction += self.get_output_content()
        print("Instruction: ", instruction)

        max_attempts = 3  # 设置最大尝试次数
        attempts = 0

        while attempts < max_attempts:
            messages = [{"role": "system", "content": instruction}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, temperature=0.4,
                deployment_id="gpt35",  # azure 需要
            )
            txt = response.choices[0].message.content
            print("----------------debug---response")
            print(txt)
            print("----------------debug")

            if isinstance(txt, dict):
                return txt

            try:
                # 尝试将字符串转换为字典
                result_dict = json.loads(txt.replace("'", '"'))
                return result_dict  # 成功转换为字典，退出循环
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                attempts += 1
                print(f"Attempt {attempts}/{max_attempts}. Retrying...")
                time.sleep(1)  # 增加延迟，避免频繁调用 API

        print("Reached maximum attempts. Unable to decode JSON.")
        return None  # 如果达到最大尝试次数仍无法成功，返回None或者其他适当的值

        # messages = [{"role": "system", "content": instruction}]
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo", messages=messages, temperature=0.4,
        #     deployment_id="gpt35", # azure 需要
        # )
        # txt = response.choices[0].message.content
        # print("----------------debug")
        # print(txt)
        # print("----------------debug")
        # # GPT-3 API返回结果为字符串，需要将其转化为字典。
        # result_dict = json.loads(txt.replace("'", '"'))
        # return result_dict
        # return instruction

    def get_input_content(self, env_information):
        instruction = ""
        # instruction += agent_information
        instruction += env_information
        return instruction

    def get_output_content(self):
        instruction = ""
        return instruction


class Buyer(Agent):
    def __init__(self, role, name, type="", personality="", budget=1000):
        super().__init__(role, name, type, personality)
        self.budget = budget

    def evaluate(self):
        pass

    def decision(self, env_information):
        return super().decision(env_information)

    def get_input_content(self, env_information):
        # instruction = super().get_input_content(env_information)
        instruction = "[no prose]\n [Output only JSON]"
        instruction += f"You name is {self.name} and you are a buyer with the following personality and preferences:[{self.personality}]."
        instruction += f"Your budget for the purchase is [{self.budget}]."
        instruction += f"In the market, there are various products available, including [{env_information}]."
        # instruction += new_information
        # budget

        return instruction

    def get_output_content(self):
        instruction = super().get_output_content()
        instruction += "Now, considering your personality, budget, and the available products, make a decision on which product from a specific seller you would like to purchase."
        instruction += "Provide the following information in Python dictionary format: {'Buyer':'[Your Name]', 'Seller':'[Seller Name]', 'Product':'[Product Name]', 'Price': [Product Price], 'Reason':'[Your reasons for choosing this product, less than 20 words]', 'Score':[Your score on a 10-point scale]}."
        # instruction += new_information
        # 买哪个
        # 反馈口碑
        # 商品质量（分数+文本）
        # 卖家信用
        return instruction


class Seller(Agent):
    def __init__(self, role, name, type="", personality=""):
        super().__init__(role, name, type, personality)

    def evaluate(self):
        pass

    def decision(self, env_information):
        return super().decision(env_information)

    def get_input_content(self, env_information):
        # instruction = super().get_input_content(env_information)
        instruction = "[no prose]\n [Output only JSON]"
        instruction += f"You are a seller named [{self.name}], " \
                       f"operating in the current market conditions of [{env_information}]. "
        # sale strategy
        return instruction

    def get_output_content(self):
        instruction = super().get_output_content()
        instruction += "You have the option to maintain your current approach or make changes to the products you sell and your sales strategy. Consider the market dynamics and make a decision on how to optimize your sales for the day."
        instruction += "Provide the following information in Python dictionary format: {'Seller':'[Seller Name]', 'Products': [{'[Your Product for the new day]': {'Price': [Price for the product]},}], 'Promotions':'[Your new business strategy for the day, e.g., discounts on specific products or any other promotional activities]'}."
        # instruction += new_information
        # 商品属性调整
        # 销售策略调整
        return instruction

import csv

class Environment:
    def __init__(self, trade_history_file, market_state_file):
        self.trade_history_file = trade_history_file
        self.market_state_file = market_state_file
        self.trade_history = self.load_trade_history()
        self.market_state = self.load_market_state()

    def load_trade_history(self):
        try:
            with open(self.trade_history_file, 'r', newline='') as file:
                reader = csv.DictReader(file, delimiter='\t')  # Assuming TSV format
                trade_history = []
                for row in reader:
                    trade_history.append({
                        'time': int(row['Time']),
                        'buyer': row['Buyer'],
                        'seller': row['Seller'],
                        'product': row['Product'],
                        'quantity': int(row['Quantity']),
                        'price': float(row['Price']),
                    })
        except FileNotFoundError:
            trade_history = []
        return trade_history

    def save_trade_history(self):
        with open(self.trade_history_file, 'w', newline='') as file:
            fieldnames = ['Time', 'Buyer', 'Seller', 'Product', 'Quantity', 'Price']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')

            writer.writeheader()
            for trade in self.trade_history:
                writer.writerow({
                    'Time': trade['time'],
                    'Buyer': trade['buyer'],
                    'Seller': trade['seller'],
                    'Product': trade['product'],
                    'Quantity': trade['quantity'],
                    'Price': trade['price'],
                })

    def load_market_state(self):
        try:
            with open(self.market_state_file, 'r', newline='') as file:
                reader = csv.DictReader(file, delimiter='\t')  # Assuming TSV format
                market_state = {}
                for row in reader:
                    seller = row['Seller']
                    prev_day_sales = float(row['PrevDaySales'])
                    total_sales = float(row['TotalSales'])
                    products = json.loads(row['Products']) if 'Products' in row else {}
                    promotions = row['Promotions'] if 'Promotions' in row else ''
                    market_state[seller] = {
                        'PrevDaySales': prev_day_sales,
                        'TotalSales': total_sales,
                        'Products': products,
                        'Promotions': promotions
                    }
        except FileNotFoundError:
            market_state = {}
        return market_state

    def save_market_state(self):
        with open(self.market_state_file, 'w', newline='') as file:
            fieldnames = ['Seller', 'PrevDaySales', 'TotalSales', 'Products', 'Promotions']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')

            writer.writeheader()
            for seller, sales_data in self.market_state.items():
                writer.writerow({
                    'Seller': seller,
                    'PrevDaySales': sales_data['PrevDaySales'],
                    'TotalSales': sales_data['TotalSales'],
                    'Products': json.dumps(sales_data.get('Products', {})),
                    'Promotions': sales_data.get('Promotions', '')
                })

    def update(self, role, new_sale_data=None, new_sale_strategy=None):
        # Update the market_state based on the latest sales information
        if role == "buyer":
            if new_sale_data is None:
                return
            for entry in new_sale_data:
                # print("debug------------------------------")
                # print(entry)
                time, decision, quantity = entry
                buyer = decision['Buyer']
                seller = decision['Seller']
                product = decision['Product']
                price = decision['Price']
                # reason = decision['Reason']
                # score = decision['Score']
                self.trade_history.append({
                    'time': time,
                    'buyer': buyer,
                    'seller': seller,
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                })

            # Update market state based on the trade entries
            self.calculate_sales_info(new_sale_data)

            self.save_trade_history()
            self.save_market_state()

        elif role == "seller":
            if new_sale_strategy is None:
                return
            for entry in new_sale_strategy:
                decision = entry
                # print("----------------debug---decision")
                # print(decision)
                # print("----------------debug")

                if decision is None:
                    print("---------decision is None, continue")
                    continue

                seller = decision['Seller']
                new_products = decision['Products']
                sale_strategy = decision['Promotions']
                if seller not in self.market_state:
                    self.market_state[seller] = {
                        'PrevDaySales': 0,
                        'TotalSales': 0,
                        'Products': {},
                        'Promotions': ''
                    }
                self.market_state[seller]['Products'] = {}

                # print("----------------debug---new_products")
                # print(new_products)
                # print("----------------debug")

                for product in new_products:
                    # Assuming each product is a tuple (product_name, initial_quantity, initial_price)
                    # print("----------------debug---product")
                    # print(product)
                    # print("----------------debug")
                    # product_name, initial_price = product
                    # self.market_state[seller]['Products'][product_name] = {
                    #     'Price': initial_price
                    # }
                    for product_name, product_info in product.items():
                        # print("----------------debug---product")
                        # print(product_name)
                        # print("----------------debug")
                        initial_price = product_info['Price']
                        # cost_price = product_info['Cost Price']

                        self.market_state[seller]['Products'][product_name] = {
                            'Price': initial_price,
                            # 'Cost Price': cost_price
                        }

                    # Apply discount strategy
                self.market_state[seller]['Promotions'] = sale_strategy

            self.save_market_state()
        else:
            pass

    def check(self):
        # Calculate and return information about the current sales situation
        return str(self.market_state)

    def calculate_sales_info(self, trade_entries):
        # Implement logic to calculate and return sales information
        for seller in self.market_state:
            self.market_state[seller]['PrevDaySales'] = 0

        for entry in trade_entries:
            time, decision, quantity = entry
            seller = decision['Seller']
            product = decision['Product']
            price = decision['Price']

            if seller not in self.market_state:
                self.market_state[seller] = {'PrevDaySales': 0, 'TotalSales': 0}

            # Update market state based on the trade entry
            self.market_state[seller]['PrevDaySales'] += quantity * price
            self.market_state[seller]['TotalSales'] += quantity * price
        return self.market_state

def demo():
    logging.info("start demo")

    file_path = 'market_data.tsv'
    trade_history_file_path = 'trade_history.tsv'
    market_state_file_path = 'market_state.tsv'

    environment = Environment(trade_history_file_path, market_state_file_path)

    # Check the current sales situation
    current_sale_info = environment.check()
    print("Current Sales Information:", current_sale_info)

    # Simulate new sales data (this can be obtained from agents or other sources)
    # new_sale_data_list = [(1, 'Seller1', 'Product1', 1, 10.0),
    #                       (2, 'Seller2', 'Product1', 1, 15.0),
    #                       (3, 'Seller1', 'Product2', 1, 20.0)]
    decision = {'Seller': 'Seller2', 'Product': 'ProductE', 'Price': 15.0,
     'Reason': 'I chose this product because it is within my budget and there is a discount available. Additionally, the seller has a lower price compared to other sellers. The product also seems to be popular based on the previous day sales and total sales.',
     'Score': 9.5}
    new_sale_data_list = [(1, decision, 1)]

    sale_strategy_data_list = [
        ('Seller1', [('ProductC', 200.0), ('ProductD', 150.0)], "no discount"),
        ('Seller2', [('ProductE', 250.0)], "discount {'ProductE': 0.15}"),
        # Add more sale_strategy_data tuples as needed
    ]
    # Update the environment with the new sales data
    environment.update("buyer", new_sale_data_list)

    # Check the updated sales situation
    updated_sale_info = environment.check()
    print("Updated Sales Information:", updated_sale_info)


    buyers_list = [
        Buyer(role="buyer", name="buyer1", type="premium", personality="friendly", budget=1000),
        Buyer(role="buyer", name="buyer2", type="standard", personality="meticulous", budget=800),
        # Add more buyers as needed
    ]

    sellers_list = [
        Seller(role="seller", name="seller1", type="premium", personality="friendly"),
        Seller(role="seller", name="seller2", type="standard", personality="meticulous"),
        # Add more buyers as needed
    ]

    cnt = 1
    epoch_NUM = 2

    while True:
        logging.info(f"--------------------now epoch {cnt}--------------------")
        print(f"--------------------now epoch {cnt}--------------------")

        # 环境信息：广告、政策
        # （后期）商品对应的口碑
        # 商品销售情况、（商品价格波动情况）
        env_information = environment.check()
        history = []
        print(f"-------------------------------------------------")
        print(f"Env_information:{env_information}")
        print(f"-------------------buyer turn--------------------")

        # Iterate through the list of buyers
        for buyer in buyers_list:
            # Access attributes or methods of each buyer
            print(f"Buyer: {buyer.name}, Budget: {buyer.budget}")
            decision = buyer.decision(env_information)  # Get buyer's decision
            logging.info(decision)
            print(f"Decision: {decision}")
            history.append((cnt, decision, 1))

        environment.update(role="buyer", new_sale_data=history)
        env_information = environment.check()

        history = []
        print(f"-------------------------------------------------")
        print(f"Env_information:{env_information}")
        print(f"-------------------seller turn--------------------")

        # Iterate through the list of buyers
        for seller in sellers_list:
            # Access attributes or methods of each buyer
            print(f"Seller: {seller.name}")
            decision = seller.decision(env_information)  # Get seller's decision
            logging.info(decision)
            print(f"Decision: {decision}")
            history.append(decision)

        environment.update(role="seller", new_sale_strategy=history)

        cnt += 1
        if cnt > epoch_NUM:
            break


if __name__ == "__main__":

    demo()
