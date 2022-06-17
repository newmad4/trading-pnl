import unittest
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import List


class Direction(Enum):
    BUY = "Buy"
    SELL = "Sell"


@dataclass
class TradeOperation:
    """Data model for each trading operation with all necessary properties."""

    direction: Direction
    quantity: int
    price: Decimal
    underlying: str


class TradingOperations:
    """Provide functionality of calculation PNL in FIFO manner for a bunch of trading operations."""

    def __init__(self, trades_data: List[dict]):
        self.trades_by_underlying = defaultdict(lambda: list())

        for trades_operation in trades_data:
            underlying = trades_operation["underlying"]
            self.trades_by_underlying[underlying].append(TradeOperation(**trades_operation))

    @staticmethod
    def __price_of_first_n_goods(quantity: int, trades: List[TradeOperation]) -> Decimal:
        result = Decimal(0)
        for t in trades:
            if t.quantity <= quantity:
                result += t.quantity * t.price
                quantity -= t.quantity
            else:
                result += quantity * t.price
                # quantity = 0
                break

        return result

    def __underlying_pnl(self, trades: List[TradeOperation]) -> Decimal:
        buy_trades = [t for t in trades if t.direction == Direction.BUY]
        sell_trades = [t for t in trades if t.direction == Direction.SELL]

        if not buy_trades or not sell_trades:
            return Decimal(0)

        buy_quantity = sum(t.quantity for t in buy_trades)
        sell_quantity = sum(t.quantity for t in sell_trades)
        quantity = min(buy_quantity, sell_quantity)

        total_buy_prices = self.__price_of_first_n_goods(quantity, buy_trades)
        total_sell_prices = self.__price_of_first_n_goods(quantity, sell_trades)
        return total_sell_prices - total_buy_prices

    @property
    def pnl(self) -> Decimal:
        result = Decimal(0)
        for trades in self.trades_by_underlying.values():
            result += self.__underlying_pnl(trades)
        return result


class TestTradingOperations(unittest.TestCase):

    def test_case_1(self):
        transactions = [
            {"direction": Direction.BUY, "quantity": 2, "price": Decimal(100), "underlying": "Oil"},  # 1
            {"direction": Direction.BUY, "quantity": 2, "price": Decimal(110), "underlying": "Oil"},  # 2
            {"direction": Direction.BUY, "quantity": 3, "price": Decimal(102), "underlying": "Oil"},  # 3
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, 0)

    def test_case_2(self):
        transactions = [
            {"direction": Direction.BUY, "quantity": 2, "price": Decimal(100), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 2, "price": Decimal(110), "underlying": "Oil"},  # 2
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, 20)

    def test_case_3(self):
        transactions = [
            {"direction": Direction.BUY, "quantity": 1, "price": Decimal(100), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 4, "price": Decimal(110), "underlying": "Oil"},  # 2
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, 10)

    def test_case_4(self):
        transactions = [
            {"direction": Direction.BUY, "quantity": 1, "price": Decimal(100), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 4, "price": Decimal(110), "underlying": "Oil"},  # 2
            {"direction": Direction.BUY, "quantity": 4, "price": Decimal(120), "underlying": "Oil"},  # 3
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, -Decimal(20))

    def test_case_5(self):
        transactions = [
            {"direction": Direction.BUY, "quantity": 1, "price": Decimal(100), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 4, "price": Decimal(110), "underlying": "Gas"},  # 2
            {"direction": Direction.BUY, "quantity": 2, "price": Decimal(120), "underlying": "Gas"},  # 3
            {"direction": Direction.SELL, "quantity": 5, "price": Decimal(115), "underlying": "Oil"},  # 4
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, -Decimal(5))

    def test_case_6(self):
        transactions = []
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, 0)

    def test_case_7(self):
        transactions = [
            {"direction": Direction.SELL, "quantity": 3, "price": Decimal(10), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 4, "price": Decimal(20), "underlying": "Oil"},  # 2
            {"direction": Direction.BUY, "quantity": 10, "price": Decimal(10), "underlying": "Oil"},  # 3
            {"direction": Direction.BUY, "quantity": 5, "price": Decimal(20), "underlying": "Oil"},  # 4
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, Decimal(40))

    def test_case_8(self):
        transactions = [
            {"direction": Direction.SELL, "quantity": 3, "price": Decimal(11), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 4, "price": Decimal(20), "underlying": "Oil"},  # 2
            {"direction": Direction.BUY, "quantity": 2, "price": Decimal(10), "underlying": "Oil"},  # 3
            {"direction": Direction.BUY, "quantity": 3, "price": Decimal(5), "underlying": "Oil"},  # 4
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, Decimal(38))

    def test_case_9(self):
        transactions = [
            {"direction": Direction.SELL, "quantity": 3, "price": Decimal(1), "underlying": "Oil"},  # 1
            {"direction": Direction.SELL, "quantity": 4, "price": Decimal(2), "underlying": "Oil"},  # 2
            {"direction": Direction.BUY, "quantity": 2, "price": Decimal(3), "underlying": "Oil"},  # 3
            {"direction": Direction.BUY, "quantity": 3, "price": Decimal(4), "underlying": "Oil"},  # 4
        ]
        trader = TradingOperations(transactions)
        self.assertEqual(trader.pnl, -Decimal(11))


if __name__ == "__main__":
    unittest.main()
