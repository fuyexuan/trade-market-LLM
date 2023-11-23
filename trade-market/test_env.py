from llm_market import Environment


def test():

    file_path = 'market_data.tsv'
    trade_history_file_path = 'test_trade_history.tsv'
    market_state_file_path = 'test_market_state.tsv'

    environment = Environment(trade_history_file_path, market_state_file_path)

    # Check the current sales situation
    current_sale_info = environment.check()
    print("Current Sales Information:", current_sale_info)

    # Simulate new sales data (this can be obtained from agents or other sources)
    sale_strategy_data_list = [
        {'Seller': 'Seller1', 'Products': [{'Product1': {'Price': 10}}, {'Product2': {'Price': 15}}],
         'Promotions': "no discount"},
        {'Seller': 'Seller2', 'Products': [{'Product1': {'Price': 10}}, {'Product2': {'Price': 15}}],
         'Promotions': "discount {'Product1': 0.15}"},
        # Add more sale_strategy_data tuples as needed
    ]

    # 测试时需要新update new_sale_strategy才能保证products非空，不会报错
    environment.update(role="seller", new_sale_strategy=sale_strategy_data_list)

    decision = {'Seller': 'Seller2', 'Product': 'ProductE', 'Price': 15.0,
                'Reason': 'I chose this product because it is within my budget and there is a discount available.',
                'Score': 9.5}
    new_sale_data_list = [(1, decision, 1)]  # time, decision, quantity

    # Update the environment with the new sales data
    environment.update("buyer", new_sale_data_list)

    # Check the updated sales situation
    updated_sale_info = environment.check()
    print("Updated Sales Information:", updated_sale_info)


if __name__ == "__main__":

    test()
