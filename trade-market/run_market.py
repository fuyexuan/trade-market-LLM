import logging
from llm_market import Environment, Seller, Buyer

if __name__ == "__main__":

    EXP_NUM = 7

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(process)d \n\t %(" "message)s",
        filename=f"log/trade_{EXP_NUM}.log",
    )

    logging.info(f"start Experiment No.{EXP_NUM}")

    trade_history_file_path = f'result/trade_history_{EXP_NUM}.tsv'
    market_state_file_path = f'result/market_state_{EXP_NUM}.tsv'

    environment = Environment(trade_history_file_path, market_state_file_path)

    # Check the current sales situation
    current_sale_info = environment.check()
    print("Current Sales Information:", current_sale_info)

    # 设置初始卖家销售策略
    sale_strategy_data_list = [
        {'Seller': 'Seller1',
         'Products':
             [{'Product1': {'Price': 80,
                            # 'Cost Price': 5
                            }},
              {'Product2': {'Price': 80,
                            # 'Cost Price': 7
                            }}],
         'Promotions': "no discount"},
        {'Seller': 'Seller2',
         'Products':
             [{'Product1+Product2': {'Price': 100,
                            # 'Cost Price': 5
                            }}],
         'Promotions': "no discount"},
        {'Seller': 'Seller3',
         'Products':
             [{'Product1': {'Price': 90,
                            # 'Cost Price': 5
                            }},
              {'Product2': {'Price': 90,
                            # 'Cost Price': 7
                            }},
              {'Product1+Product2': {'Price': 120,
                                    # 'Cost Price': 5
                            }}],
         'Promotions': "no discount"},
        {'Seller': 'Seller4',
         'Products':
             [{'Product1': {'Price': 80,
                            # 'Cost Price': 5
                            }},
              {'Product2': {'Price': 80,
                            # 'Cost Price': 7
                            }}],
         'Promotions': "no discount"},
        # Add more sale_strategy_data tuples as needed
    ]

    # environment.update(role="seller", new_sale_strategy=sale_strategy_data_list)

    # 设定初始销售量
    # decision = {'Buyer': 'Buyer1', 'Seller': 'Seller1', 'Product': 'Product2', 'Price': 150.0,
    #             'Reason': 'I chose this product because it is within my budget.',
    #             'Score': 9.5}
    # new_sale_data_list = [(1, decision, 1)]  # 日期、购买商品、数量
    #
    # environment.update("buyer", new_sale_data_list)

    buyer_budget = 200
    buyer_prompt = " Each product will bring you 100 benefits"

    buyers_list = [
        Buyer(role="buyer", name="Buyer1", type="standard", personality="Innovator Customer, female" + buyer_prompt, budget=buyer_budget),
        Buyer(role="buyer", name="Buyer2", type="standard", personality="Innovator Customer, male" + buyer_prompt, budget=buyer_budget),
        Buyer(role="buyer", name="Buyer4", type="standard", personality="Laggard Customer, female" + buyer_prompt, budget=buyer_budget),
        Buyer(role="buyer", name="Buyer5", type="standard", personality="Laggard Customer, male" + buyer_prompt, budget=buyer_budget),
        # Add more buyers as needed
    ]

    sellers_list = [
        Seller(role="seller", name="Seller1", type="standard", personality="friendly"),
        Seller(role="seller", name="Seller2", type="standard", personality="friendly"),
        Seller(role="seller", name="Seller3", type="standard", personality="friendly"),
        Seller(role="seller", name="Seller4", type="standard", personality="friendly"),
        # Add more buyers as needed
    ]

    cnt = 1
    epoch_NUM = 10

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
            if seller.name != "Seller4":
                continue
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
