from typing import Dict, Optional, Tuple
import time
import sys

# -------------------------------
# Class Product
# -------------------------------
class Product:
    def __init__(self, name: str, price: int, stock: int):
        self.name = name
        self.price = max(price, 1)  # price ≥ 1
        self.stock = max(stock, 0)  # stock ≥ 0

    def __str__(self):
        return f"{self.name} - Price: {self.price} Baht - Stock: {self.stock}"

    def is_available(self) -> bool:
        return self.stock > 0

    def buy(self) -> bool:
        if self.is_available():
            self.stock -= 1
            return True
        return False

# -------------------------------
# Class CashMgr
# -------------------------------
class CashMgr:
    COINS = [1, 2, 5, 10]
    NOTES = [20, 50, 100, 500, 1000]
    DENOMINATIONS = COINS + NOTES

    def __init__(self):
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        if denom in self.DENOMINATIONS and count > 0:
            self.cash[denom] = self.cash.get(denom, 0) + count

    def can_change(self, amt: int) -> bool:
        return self._calc_change(amt, simulate=True) is not None

    def make_change(self, amt: int) -> Optional[Dict[int, int]]:
        return self._calc_change(amt, simulate=False)

    def _calc_change(self, amt: int, simulate=False) -> Optional[Dict[int, int]]:
        # Greedy + ตรวจสอบ stock จริง
        change = {}
        temp_cash = self.cash.copy()

        for denom in sorted(self.DENOMINATIONS, reverse=True):
            available = temp_cash.get(denom, 0)
            count = 0
            while amt >= denom and available > 0:
                amt -= denom
                available -= 1
                count += 1
            if count > 0:
                change[denom] = count
                temp_cash[denom] = available

        if amt == 0:
            if not simulate:
                for denom, count in change.items():
                    self.cash[denom] -= count
            return change
        return None

    def show_change(self, change: Dict[int, int]):
        coin_change = {d: c for d, c in change.items() if d in self.COINS}
        note_change = {d: c for d, c in change.items() if d in self.NOTES}

        if coin_change:
            print("       🪙 COINS:")
            for coin in sorted(coin_change.keys()):
                print(f"          • {coin} Baht × {coin_change[coin]} coins")
        if note_change:
            print("       💵 BANKNOTES:")
            for note in sorted(note_change.keys()):
                print(f"          • {note} Baht × {note_change[note]} notes")

# -------------------------------
# Class FileMgr
# -------------------------------
class FileMgr:
    @staticmethod
    def load_goods(file: str = "Goods.txt") -> Dict[int, Product]:
        products = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        try:
                            num, name, price, stock = parts
                            products[int(num)] = Product(name, int(price), int(stock))
                        except ValueError:
                            continue
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return products

    @staticmethod
    def save_goods(products: Dict[int, Product], file: str = "Goods.txt"):
        try:
            with open(file, 'w', encoding='utf-8') as f:
                for num, p in products.items():
                    f.write(f"{num},{p.name},{p.price},{p.stock}\n")
        except Exception as e:
            print(f"        ❌ Error saving goods: {e}")

    @staticmethod
    def load_wallet(file: str = "Wallet.txt") -> Dict[int, int]:
        cash = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        try:
                            denom, count = parts
                            cash[int(denom)] = int(count)
                        except ValueError:
                            continue
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return cash

    @staticmethod
    def save_wallet(cash: Dict[int, int], file: str = "Wallet.txt"):
        try:
            with open(file, 'w', encoding='utf-8') as f:
                for denom, count in cash.items():
                    f.write(f"{denom},{count}\n")
        except Exception as e:
            print(f"        ❌ Error saving wallet: {e}")

# -------------------------------
# Class VendingMachine
# -------------------------------
class VendingMachine:
    def __init__(self, password: str = "1234"):
        self.password = password
        self.products: Dict[int, Product] = {}
        self.cash_mgr = CashMgr()
        self.load_data()

    # -------------------
    # UI Helpers
    # -------------------
    def print_title(self, title: str):
        print("\n" + "✨" + "═" * 58 + "✨")
        print(f"    {title}")
        print("✨" + "═" * 58 + "✨")

    def loading_animation(self, text: str, duration: float = 1.0):
        print(f"\n    🔄 {text}", end="", flush=True)
        for _ in range(int(duration * 4)):
            print(".", end="", flush=True)
            time.sleep(0.25)
        print(" ✅ Complete!\n")

    # -------------------
    # Data
    # -------------------
    def load_data(self):
        self.loading_animation("Loading data from files", 1.0)
        self.products = FileMgr.load_goods()
        self.cash_mgr.cash = FileMgr.load_wallet()

    def save_data(self):
        self.loading_animation("Saving data to files", 0.5)
        FileMgr.save_goods(self.products)
        FileMgr.save_wallet(self.cash_mgr.cash)

    # -------------------
    # Show / Buy
    # -------------------
    def show_products(self):
        self.print_title("🛍️  PRODUCT SHOWCASE  🛍️")
        for i in range(1, 10):
            if i in self.products:
                p = self.products[i]
                status = "✅ Available" if p.is_available() else "❌ Out of Stock"
                print(f"      ({i}) {p.name:<20} {p.price:>3}฿  Qty: {p.stock:>2}  {status}")
            else:
                print(f"      ({i}) {'Empty Slot':<20} ---   Qty: --  🚫 No Product")
        print("\n      (e) 🚪 Exit Product Selection")
        print("─" * 62)

    def buy_menu(self):
        while True:
            self.show_products()
            choice = input("\n    ➤ Enter choice (1-9 or 'e'): ").strip().lower()
            if choice == 'e':
                break
            if choice.isdigit() and 1 <= int(choice) <= 9:
                product_num = int(choice)
                if product_num in self.products:
                    self.process_purchase(self.products[product_num])
                    self.save_data()
                    input("\n    🎉 Press Enter to continue shopping...")
            else:
                print("\n    ⚠️ Invalid selection")

    def process_purchase(self, product: Product) -> bool:
        if not product.is_available():
            print("\n    ❌ Out of stock")
            return False

        self.print_title("💳  PAYMENT TERMINAL  💳")
        print(f"    🛍️  Selected Product: {product.name}")
        print(f"    💰 Price: {product.price} Baht")

        total_paid, inserted_money = self.collect_payment(product.price)
        if total_paid is None:
            return False

        change_amount = total_paid - product.price
        if change_amount > 0 and not self.cash_mgr.can_change(change_amount):
            print("\n    ❌ Transaction failed: no change available")
            return False

        # Add inserted money
        for denom, count in inserted_money.items():
            self.cash_mgr.add(denom, count)

        # Give change
        change_detail = self.cash_mgr.make_change(change_amount) if change_amount > 0 else {}

        # Reduce stock
        product.buy()

        print("\n    🎉 Purchase successful!")
        print(f"    💸 Change: {change_amount} Baht")
        if change_detail:
            self.cash_mgr.show_change(change_detail)
        return True

    def collect_payment(self, price: int) -> Tuple[Optional[int], Optional[Dict[int, int]]]:
        total = 0
        inserted = {}
        valid_money = CashMgr.DENOMINATIONS

        while total < price:
            remaining = price - total
            print(f"\n      💰 Current Total: {total} Baht")
            print(f"      🎯 Amount Needed: {remaining} Baht")
            choice = input("\n      ➤ Insert money or 'c' to cancel: ").strip().lower()

            if choice == 'c':
                print("\n      🚫 Payment cancelled")
                return None, None

            try:
                amount = int(choice)
                if amount in valid_money:
                    inserted[amount] = inserted.get(amount, 0) + 1
                    total += amount
                else:
                    print("      ❌ Invalid money")
            except ValueError:
                print("      ⚠️ Numbers only")
        return total, inserted

    # -------------------
    # Maintenance
    # -------------------
    def maintenance_menu(self):
        self.print_title("🔐  SECURE ACCESS  🔐")
        password = input("    🔑 Enter password: ")
        if password != self.password:
            print("\n    ❌ ACCESS DENIED")
            return
        print("\n    ✅ ACCESS GRANTED")
        time.sleep(1)

        while True:
            self.print_title("⚙️   MAINTENANCE CENTER   ⚙️")
            print("      (g) Setup Products")
            print("      (w) Setup Cash")
            print("      (c) Exit Maintenance")
            choice = input("\n      ➤ Select operation: ").strip().lower()
            if choice == 'g':
                self.setup_goods()
            elif choice == 'w':
                self.setup_wallet()
            elif choice == 'c':
                break

    def setup_goods(self):
        self.products.clear()
        for i in range(1, 10):
            name = input(f"      ➤ Product name for slot {i} (Enter to skip): ").strip()
            if not name:
                continue
            # Input validation
            while True:
                try:
                    price = int(input("      ➤ Price (10-1000 Baht): "))
                    if 10 <= price <= 1000:
                        break
                    print("      ❌ Price out of range")
                except ValueError:
                    print("      ⚠️ Numbers only")
            while True:
                try:
                    stock = int(input("      ➤ Initial stock (0-99): "))
                    if 0 <= stock <= 99:
                        break
                    print("      ❌ Stock out of range")
                except ValueError:
                    print("      ⚠️ Numbers only")
            self.products[i] = Product(name, price, stock)
        self.save_data()

    def setup_wallet(self):
        self.cash_mgr.cash.clear()
        for denom in CashMgr.DENOMINATIONS:
            while True:
                try:
                    count = int(input(f"      ➤ {denom} Baht x count: "))
                    if count >= 0:
                        self.cash_mgr.cash[denom] = count
                        break
                    print("      ❌ Count must be ≥0")
                except ValueError:
                    print("      ⚠️ Numbers only")
        self.save_data()

    # -------------------
    # Shutdown
    # -------------------
    def shutdown(self):
        self.print_title("🔐  SYSTEM SHUTDOWN  🔐")
        password = input("    🔑 Enter shutdown password: ")
        if password == self.password:
            print("\n    ✅ Password accepted")
            for i in range(3, 0, -1):
                print(f"    🔄 Shutting down in {i}...")
                time.sleep(1)
            print("\n    🛑 System shutdown complete")
            sys.exit(0)
        else:
            print("\n    ❌ ACCESS DENIED")

    # -------------------
    # Main Run
    # -------------------
    def run(self):
        print("\n🌟" + "═" * 40 + "🌟")
        print("      🏪  VENDING MACHINE  🏪")
        print("      ✨  Welcome to Shopping  ✨")
        print("🌟" + "═" * 40 + "🌟")
        time.sleep(1.5)

        while True:
            self.print_title("🎮  MAIN CONTROL PANEL  🎮")
            print("\n      🛍️  (b) Shopping Center")
            print("      ⚙️  (m) Maintenance Hub")
            print("      🛑 (s) Power Down")

            choice = input("\n      ➤ Enter your choice (b/m/s): ").strip().lower()
            if choice == 'b':
                self.buy_menu()
            elif choice == 'm':
                self.maintenance_menu()
            elif choice == 's':
                self.shutdown()
            else:
                print("\n    ⚠️  Invalid selection!")
                time.sleep(1.0)

# -------------------------------
# Main Program
# -------------------------------
if __name__ == "__main__":
    print("🚀 Starting Vending Machine System...")
    time.sleep(1.0)
    vending_machine = VendingMachine()
    vending_machine.run()
