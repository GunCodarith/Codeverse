from typing import Dict
import os


# -------------------------------
# Product class
# -------------------------------
class Product:
    """This class is for a product in the vending machine."""

    def __init__(self, name: str, price: int, stock: int):
        """
        Create a product.
        name : product name
        price : product price
        stock : how many in stock
        """
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        """Show product as text."""
        return f"{self.name} Price {self.price} Baht (Stock {self.stock})"

    def is_available(self) -> bool:
        """Return True if product has stock."""
        return self.stock > 0

    def buy(self) -> bool:
        """Reduce stock by 1 if available. Return True if bought."""
        if self.is_available():
            self.stock -= 1
            return True
        return False


# -------------------------------
# CashManager class
# -------------------------------
class CashManager:
    """This class manages money for paying and giving change."""

    DENOMINATIONS = [1000, 500, 100, 50, 20, 10, 5, 2, 1]

    def __init__(self):
        """Create an empty cash storage."""
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        """Add some money to machine."""
        self.cash[denom] = self.cash.get(denom, 0) + count

    def make_change(self, amount: int):
        """
        Try to give change.
        Return dictionary of bills or None if not enough.
        """
        result = {}
        for d in self.DENOMINATIONS:
            while amount >= d and self.cash.get(d, 0) > 0:
                amount -= d
                self.cash[d] -= 1
                result[d] = result.get(d, 0) + 1
        if amount == 0:
            return result
        return None


# -------------------------------
# FileManager class
# -------------------------------
class FileManager:
    """This class reads and writes product and wallet files."""

    @staticmethod
    def load_goods(file="Goods.txt") -> Dict[int, Product]:
        """Load products from a file."""
        products = {}
        if not os.path.exists(file):
            return products
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    slot, name, price, stock = parts
                    try:
                        products[int(slot)] = Product(name, int(price), int(stock))
                    except:
                        continue
        return products

    @staticmethod
    def save_goods(products: Dict[int, Product], file="Goods.txt"):
        """Save products to a file."""
        with open(file, "w", encoding="utf-8") as f:
            for slot, p in products.items():
                f.write(f"{slot},{p.name},{p.price},{p.stock}\n")

    @staticmethod
    def load_wallet(file="Wallet.txt") -> Dict[int, int]:
        """Load wallet from a file."""
        cash = {}
        if not os.path.exists(file):
            return cash
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    try:
                        d, c = int(parts[0]), int(parts[1])
                        cash[d] = c
                    except:
                        continue
        return cash

    @staticmethod
    def save_wallet(cash: Dict[int, int], file="Wallet.txt"):
        """Save wallet to a file."""
        with open(file, "w", encoding="utf-8") as f:
            for d, c in cash.items():
                f.write(f"{d},{c}\n")
