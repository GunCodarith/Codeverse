import sys
from typing import Dict
from storage import Product, CashManager, FileManager


# -------------------------------
# VendingMachine class
# -------------------------------
class VendingMachine:
    """This class is the vending machine system."""

    def __init__(self, password="1234"):
        """Create vending machine with password, products, and cash."""
        self.password = password
        self.products = FileManager.load_goods()
        self.cash_mgr = CashManager()
        self.cash_mgr.cash = FileManager.load_wallet()

    def format_cash(self, cash: Dict[int, int]) -> str:
        """Return cash as text."""
        lines = []
        for d in sorted(cash.keys(), reverse=True):
            lines.append(f"  {d} Baht x {cash[d]}")
        return "\n".join(lines) if lines else "  -"

    def show_products(self):
        """Show all products on screen."""
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
        """Menu for buying products."""
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
        """Collect money from user. Return total and dict."""
        total = 0
        inserted = {}
        while total < product.price:
            money = input(
                f"💰 Insert cash (Need {product.price - total} Baht, c=Cancel Payment): "
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
                    print("\n❌ [FAILED] Unsupported denomination")
                    return None, inserted
            except:
                print("\n❌ [FAILED] Invalid input")
                return None, inserted
        return total, inserted

    def process_purchase(self, product: Product):
        """Process buying a product."""
        if not product.is_available():
            print(f"\n❌ [FAILED] {product.name} is out of stock")
            print(f"📦 Product: {product.name}")
            print(f"💰 Price: {product.price} Baht")
            print(f"💳 Paid: 0 Baht")
            print("💰 Refund 0 Baht:")
            print(self.format_cash({}))
            return

        print(f"\n🎯 Selected {product.name}, Price {product.price} Baht")
        total, inserted = self.collect_cash(product)

        if total is None:
            print(f"\n🚫 [PURCHASE CANCELED]")
            print(f"📦 Product: {product.name}")
            print(f"💰 Price: {product.price} Baht")
            paid = sum([k * v for k, v in inserted.items()])
            print(f"💳 Paid: {paid} Baht")
            print(f"💰 Refund {paid} Baht:")
            print(self.format_cash(inserted))
            return

        for d, c in inserted.items():
            self.cash_mgr.add(d, c)

        change_amt = total - product.price
        change = {}

        if change_amt > 0:
            change = self.cash_mgr.make_change(change_amt)
            if change is None:
                print(f"\n❌ [FAILED] Cannot give change")
                print(f"📦 Product: {product.name}")
                print(f"💰 Price: {product.price} Baht")
                print(f"💳 Paid: {total} Baht")
                print(f"💰 Refund {total} Baht:")
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
        """Menu for maintenance."""
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
        """Setup products in machine."""
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
        """Setup cash in machine."""
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
        """Shutdown the machine if password correct."""
        pwd = input("🔐 Enter password to shutdown: ")
        if pwd == self.password:
            print("🔌 System shutdown")
            sys.exit()
        else:
            print("❌ Wrong password")

    def run(self):
        """Run the vending machine main menu."""
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
