from llm_market import Seller, Buyer


def test():

    buyer = Buyer(role="buyer", name="buyer1", type="premium", personality="friendly", budget=1000)
    seller = Seller(role="seller", name="seller1", type="premium", personality="friendly")

    env_information = {'seller1': {'PrevDaySales': 30.0,
                                   'TotalSales': 90.0,
                                   'Products': {'Product1': {'Price': 200.0},
                                                'Product2': {'Price': 150.0}},
                                   'Promotions': 'no discount'}
                       }


    # {'Seller1': {'PrevDaySales': 30.0, 'TotalSales': 90.0, 'Products': {'ProductC': {'Price': 200.0}, 'ProductD': {'Price': 150.0}}, 'Promotions': 'no discount'},
    # 'Seller2': {'PrevDaySales': 15.0, 'TotalSales': 45.0, 'Products': {'ProductE': {'Price': 250.0}}, 'Promotions': "discount {'ProductE': 0.15}"}}

    print(f"Buyer: {buyer.name}, Budget: {buyer.budget}")
    decision = buyer.decision(env_information)  # Get buyer's decision
    print(f"Decision: {decision}")

    print(f"Seller: {seller.name}")
    decision = seller.decision(env_information)  # Get seller's decision
    print(f"Decision: {decision}")


if __name__ == "__main__":
    test()

