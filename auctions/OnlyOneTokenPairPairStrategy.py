from auctions.StrategyResult import StrategyResult
from auctions.Strategy import Strategy


# we trade only on our token pair
class OnlyOneTokenPairPairStrategy(Strategy):
    def __init__(self, selling_token, buying_token, next_strategy):
        self.selling_token = selling_token
        self.buying_token = buying_token
        self.next_strategy = next_strategy

    def perform(self, auctionlet, context):
        auction = auctionlet.get_auction()
        if (auction.selling == self.selling_token) and (auction.buying == self.buying_token):
            return self.next_strategy.perform(auctionlet, context)
        else:
            return StrategyResult("Unrecognized token pair. Forgetting it.", forget=True)
