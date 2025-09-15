from typing import Dict
import os
import sys

# ===============================================================
# 🏪 VENDING MACHINE PROGRAM
# - All code/messages in English
# - Comments in Thai (อธิบายการทำงาน)
# ===============================================================


# -------------------------------
# Product class (คลาสสินค้า)
# -------------------------------
class Product:
    """Represents a product in the vending machine."""

    def __init__(self, name: str, price: int, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"{self.name} Price {self.price} Baht (Stock {self.stock})"

    def is_available(self) -> bool:
        return self.stock > 0

    def buy(self) -> bool:
        if self.is_available():
            self.stock -= 1
            return True
        return False


# -------------------------------
# CashManager class (จัดการเงิน)
# -------------------------------
class CashManager:
    DENOMINATIONS = [1000, 500, 100, 50, 20, 10, 5, 2, 1]

    def __init__(self):
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        self.cash[denom] = self.cash.get(denom, 0) + count

    def make_change(self, amount: int):
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
# FileManager class (จัดการไฟล์)
# -------------------------------
class FileManager:
    @staticmethod
    def load_goods(file="Goods.txt") -> Dict[int, Product]:
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
        with open(file, "w", encoding="utf-8") as f:
            for slot, p in products.items():
                f.write(f"{slot},{p.name},{p.price},{p.stock}\n")

    @staticmethod
    def load_wallet(file="Wallet.txt") -> Dict[int, int]:
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
        with open(file, "w", encoding="utf-8") as f:
            for d, c in cash.items():
                f.write(f"{d},{c}\n")


# -------------------------------
# VendingMachine class
# -------------------------------
class VendingMachine:
    def __init__(self, password="1234"):
        self.password = password
        self.products = FileManager.load_goods()
        self.cash_mgr = CashManager()
        self.cash_mgr.cash = FileManager.load_wallet()

    def format_cash(self, cash: Dict[int, int]) -> str:
        lines = []
        for d in sorted(cash.keys(), reverse=True):
            lines.append(f"  {d} Baht x {cash[d]}")
        return "\n".join(lines) if lines else "  -"

    def show_products(self):
        print("=" * 61)
        print("🛒 PRODUCT LIST 🛒")
        print("=" * 61)
        print(f"{'Slot':<10}{'Name':<22}{'Price':<8}{'Stock':<12}{'Status':<18}")
        print("-" * 61)
        for i in range(1, 10):
            if i in self.products:
                p = self.products[i]
                status = "✅ Available" if p.is_available() else "❌ Out"
                print(f" {i:<4}{p.name:<28}{p.price:<8}{p.stock:<8}{status:<12}")
            else:
                print(f" {i:<4}{'Empty':<22}{'-':<8}{'-':<8}{'⚪ ---':<12}")
        print("-" * 61)
        print("(e) Exit")

    def buy_menu(self):
        while True:
            self.show_products()
            choice = input("🎯 Select product slot: ")
            if choice == "e":
                break
            if not choice.isdigit() or int(choice) not in self.products:
                print("\n❌ [FAILED] Invalid product selection")
                continue
            self.process_purchase(self.products[int(choice)])

    def collect_cash(self, product: Product):
        """รับเงินจากผู้ใช้ คืน dict เงินและยอดรวม"""
        total = 0
        inserted = {}
        while total < product.price:
            money = input(
                f"💰 Insert cash (Need {product.price - total} Baht, c=Cancel): "
            )
            if money == "c":
                return None, inserted
            try:
                m = int(money)
                if m in CashManager.DENOMINATIONS:
                    inserted[m] = inserted.get(m, 0) + 1
                    total += m
                    print(f"💳 Total inserted: {total} Baht")
                else:
                    print("❌ Unsupported denomination")
            except:
                print("❌ Invalid input")
        return total, inserted

    def process_purchase(self, product: Product):
        if not product.is_available():
            print(f"\n❌ {product.name} is out of stock")
            return

        print(f"\n🎯 Selected {product.name}, Price {product.price} Baht")
        total, inserted = self.collect_cash(product)
        if total is None:
            print("\n🚫 Purchase canceled, refunding:")
            print(self.format_cash(inserted))
            return

        for d, c in inserted.items():
            self.cash_mgr.add(d, c)

        change_amt = total - product.price
        change = {}
        if change_amt > 0:
            change = self.cash_mgr.make_change(change_amt)
            if change is None:
                print("❌ Cannot give change, refunding:")
                print(self.format_cash(inserted))
                for d, c in inserted.items():
                    self.cash_mgr.cash[d] -= c
                return

        product.buy()
        print("\n🎉 [PURCHASE SUCCESSFUL!] 🎉")
        print(f"📦 Product: {product.name}")
        print(f"💰 Price: {product.price} Baht")
        print(f"💳 Paid: {total} Baht")
        if change_amt > 0:
            print(f"🔄 Change {change_amt} Baht:")
            print(self.format_cash(change))

        FileManager.save_goods(self.products)
        FileManager.save_wallet(self.cash_mgr.cash)

    def maintenance(self):
        pwd = input("🔐 Enter admin password: ")
        if pwd != self.password:
            print("❌ Wrong password")
            return

        while True:
            print("\n" + "=" * 30)
            print("🛠️  Maintenance Menu")
            print("=" * 30)
            print("(g) 📦 Setup Goods")
            print("(w) 💰 Setup Wallet")
            print("(c) 🚪 Exit")
            print("=" * 30)

            cmd = input("🎯 Select: ")
            if cmd == "g":
                self.setup_goods()
            elif cmd == "w":
                self.setup_wallet()
            elif cmd == "c":
                break

    def setup_goods(self):
        print("\n📦 SETTING UP PRODUCTS...")
        self.products.clear()
        for i in range(1, 10):
            name = input(f"📦 Slot {i} product name (empty=skip): ")
            if name == "":
                continue
            try:
                price = int(input("💰 Price (10-100): "))
                stock = int(input("📊 Quantity: "))
                self.products[i] = Product(name, price, stock)
            except:
                print("❌ Invalid input, skipped")
        FileManager.save_goods(self.products)
        print("💾 Products saved!")

    def setup_wallet(self):
        print("\n💰 SETTING UP WALLET...")
        for d in CashManager.DENOMINATIONS:
            try:
                cnt = int(input(f"💵 Quantity of {d} Baht: "))
                self.cash_mgr.cash[d] = cnt
            except:
                self.cash_mgr.cash[d] = 0
        FileManager.save_wallet(self.cash_mgr.cash)
        print("💾 Wallet saved!")

    def shutdown(self):
        pwd = input("🔐 Enter password to shutdown: ")
        if pwd == self.password:
            print("🔌 System shutdown")
            sys.exit()
        else:
            print("❌ Wrong password")

    def run(self):
        while True:
            print("\n" + "=" * 30)
            print("🏠 MAIN MENU")
            print("=" * 30)
            print("(b) 🛒 Buy Menu")
            print("(m) 🛠️  Maintenance")
            print("(s) 🔌 Shutdown")
            print("=" * 30)
            cmd = input("🎯 Select: ")
            if cmd == "b":
                self.buy_menu()
            elif cmd == "m":
                self.maintenance()
            elif cmd == "s":
                self.shutdown()


# ===============================================================
# MAIN PROGRAM
# ===============================================================
if __name__ == "__main__":
    vm = VendingMachine(password="1234")
    vm.run()
