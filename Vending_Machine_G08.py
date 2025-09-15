from typing import Dict
import os
import sys

# ═══════════════════════════════════════════════════════════════════════════════
# 🏪 VENDING MACHINE PROGRAM 🏪
# ═══════════════════════════════════════════════════════════════════════════════
# - All code/messages in English
# - Comments in Thai (อธิบายการทำงาน)
# ═══════════════════════════════════════════════════════════════════════════════


# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📦 PRODUCT CLASS (คลาสสินค้า)                                                │
# └─────────────────────────────────────────────────────────────────────────────┘
class Product:
    """Represents a product in the vending machine."""

    def __init__(self, name: str, price: int, stock: int):
        """
        Initialize a new product.

        Args:
            name (str): Product name.
            price (int): Price in Baht.
            stock (int): Initial stock quantity.
        """
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        """Return a string representation of the product."""
        return f"{self.name} Price {self.price} Baht (Stock {self.stock})"

    def is_available(self) -> bool:
        """
        Check if the product is available in stock.

        Returns:
            bool: True if stock > 0, else False.
        """
        return self.stock > 0

    def buy(self) -> bool:
        """
        Decrease stock by 1 if available.

        Returns:
            bool: True if purchase successful, False if out of stock.
        """
        if self.is_available():
            self.stock -= 1
            return True
        return False


# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 💰 CASH MANAGER CLASS (จัดการเงิน)                                           │
# └─────────────────────────────────────────────────────────────────────────────┘
class CashManager:
    """Manages cash for accepting payments and giving change."""

    # ชนิดเงินที่รองรับ 💵
    DENOMINATIONS = [1000, 500, 100, 50, 20, 10, 5, 2, 1]

    def __init__(self):
        """Initialize with an empty wallet."""
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        """
        Add a given quantity of a denomination to the wallet.

        Args:
            denom (int): Denomination value.
            count (int): Quantity to add.
        """
        self.cash[denom] = self.cash.get(denom, 0) + count

    def make_change(self, amount: int):
        """
        Attempt to give change for a given amount using available cash.

        Args:
            amount (int): Amount to change.

        Returns:
            dict[int, int] | None: A dict of denomination:count if possible, else None.
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


# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 FILE MANAGER CLASS (จัดการไฟล์ .txt)                                       │
# └─────────────────────────────────────────────────────────────────────────────┘
class FileManager:
    """Handles file operations for products and wallet."""

    @staticmethod
    def load_goods(file="Goods.txt") -> Dict[int, Product]:
        """
        Load product data from a file.

        Args:
            file (str): File path.

        Returns:
            dict[int, Product]: Dictionary of slot -> Product.
        """
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
        """
        Save product data to a file.

        Args:
            products (dict[int, Product]): Dictionary of slot -> Product.
            file (str): File path.
        """
        with open(file, "w", encoding="utf-8") as f:
            for slot, p in products.items():
                f.write(f"{slot},{p.name},{p.price},{p.stock}\n")

    @staticmethod
    def load_wallet(file="Wallet.txt") -> Dict[int, int]:
        """
        Load wallet data from a file.

        Args:
            file (str): File path.

        Returns:
            dict[int, int]: Dictionary of denomination -> count.
        """
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
        """
        Save wallet data to a file.

        Args:
            cash (dict[int, int]): Dictionary of denomination -> count.
            file (str): File path.
        """
        with open(file, "w", encoding="utf-8") as f:
            for d, c in cash.items():
                f.write(f"{d},{c}\n")


# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 🏪 VENDING MACHINE CLASS (เครื่องขายสินค้าหยอดเหรียญ)                        │
# └─────────────────────────────────────────────────────────────────────────────┘
class VendingMachine:
    """Represents the vending machine with product and cash management."""

    def __init__(self, password="1234"):
        """
        Initialize vending machine with admin password.

        Args:
            password (str): Admin password.
        """
        self.password = password
        self.products = FileManager.load_goods()
        self.cash_mgr = CashManager()
        self.cash_mgr.cash = FileManager.load_wallet()

    def format_cash(self, cash: Dict[int, int]) -> str:
        """
        Format cash dictionary into readable text.

        Args:
            cash (dict[int, int]): Dictionary of denomination -> count.

        Returns:
            str: Formatted string.
        """
        lines = []
        for d in sorted(cash.keys(), reverse=True):
            lines.append(f"  {d} Baht x {cash[d]}")
        return "\n".join(lines) if lines else "  -"

    def show_products(self):
        """Display the product list in tabular format."""
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
        """Handle user product purchase menu."""
        while True:
            self.show_products()
            choice = input("🎯 Select product slot: ")

            if choice == "e":
                break

            if not choice.isdigit() or int(choice) not in self.products:
                print("\n❌ [FAILED] Invalid product selection (case 3: Others)")
                print("💰 Refund 0 Baht:")
                print(self.format_cash({}))
                continue

            self.process_purchase(self.products[int(choice)])

    def process_purchase(self, product: Product):
        """
        Process the purchase of a given product.

        Args:
            product (Product): Product to be purchased.
        """
        total = 0
        inserted = {}

        # เคสสินค้าหมด 📦❌
        if not product.is_available():
            print(f"\n❌ [FAILED] {product.name} is out of stock (case 1)")
            print(f"📦 Product: {product.name}")
            print(f"💰 Price: {product.price} Baht")
            print(f"💳 Paid: {total} Baht")
            print("💰 Refund 0 Baht:")
            print(self.format_cash({}))
            return

        print(f"\n🎯 Selected {product.name}, Price {product.price} Baht")

        # วนรับเงิน 💰
        while total < product.price:
            money = input(
                f"💰 Insert cash (Need {product.price - total} Baht, c=Cancel): "
            )

            if money == "c":
                print("\n🚫 [PURCHASE CANCELED]")
                print(f"📦 Product: {product.name}")
                print(f"💰 Price: {product.price} Baht")
                print(f"💳 Paid: {total} Baht")
                print(f"💰 Refund {total} Baht:")
                print(self.format_cash(inserted))
                return

            try:
                m = int(money)
                if m in CashManager.DENOMINATIONS:
                    inserted[m] = inserted.get(m, 0) + 1
                    total += m
                    print(f"💳 Total inserted: {total} Baht")
                else:
                    print("\n❌ [FAILED] Unsupported denomination (case 3: Others)")
                    print(f"📦 Product: {product.name}")
                    print(f"💰 Price: {product.price} Baht")
                    print(f"💳 Paid: {total} Baht")
                    print(f"💰 Refund {total} Baht:")
                    print(self.format_cash(inserted))
                    return
            except:
                print("\n❌ [FAILED] Invalid input (case 3: Others)")
                print(f"📦 Product: {product.name}")
                print(f"💰 Price: {product.price} Baht")
                print(f"💳 Paid: {total} Baht")
                print(f"💰 Refund {total} Baht:")
                print(self.format_cash(inserted))
                return

        # บันทึกเงินเข้าตู้ 💼
        for d, c in inserted.items():
            self.cash_mgr.add(d, c)

        # คำนวณเงินทอน 🔄
        change_amt = total - product.price
        change = {}

        if change_amt > 0:
            change = self.cash_mgr.make_change(change_amt)
            if change is None:
                print(f"\n❌ [FAILED] Cannot give change (case 2)")
                print(f"📦 Product: {product.name}")
                print(f"💰 Price: {product.price} Baht")
                print(f"💳 Paid: {total} Baht")
                print(f"💰 Refund {total} Baht:")
                print(self.format_cash(inserted))
                return

        # ตัด stock ✂️
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

    def admin_menu(self):
        """Handle admin menu (setup goods, wallet, exit)."""
        pwd = input("🔐 Enter admin password: ")
        if pwd != self.password:
            print("❌ Wrong password")
            return

        while True:
            print("\n" + "=" * 30)
            print("👨 ADMIN MENU")
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
        """Setup products in all slots."""
        print("\n📦 SETTING UP PRODUCTS...")
        print("=" * 40)

        self.products.clear()
        for i in range(1, 10):
            name = input(f"📦 Slot {i} product name (empty=skip): ")
            if name == "":
                continue

            try:
                price = int(input("💰 Price (10-100): "))
                if price < 10 or price > 100:
                    print("❌ Invalid price (must be 10-100). Skipped")
                    continue

                stock = int(input("📊 Quantity: "))
                self.products[i] = Product(name, price, stock)
                print(f"✅ Added: {name}")
            except:
                print("❌ Invalid input, skipped")

        FileManager.save_goods(self.products)
        print("💾 Products saved!")

    def setup_wallet(self):
        """Setup wallet with cash quantities."""
        print("\n💰 SETTING UP WALLET...")
        print("=" * 40)

        for d in CashManager.DENOMINATIONS:
            try:
                cnt = int(input(f"💵 Quantity of {d} Baht: "))
                self.cash_mgr.cash[d] = cnt
            except:
                self.cash_mgr.cash[d] = 0

        FileManager.save_wallet(self.cash_mgr.cash)
        print("💾 Wallet saved!")

    def shutdown(self):
        """Shutdown the system (requires admin password)."""
        pwd = input("🔐 Enter password to shutdown: ")
        if pwd == self.password:
            print("🔌 System shutdown")
            print("👋 Goodbye!")
            sys.exit()
        else:
            print("❌ Wrong password")

    def run(self):
        """Run the main vending machine program loop."""

        while True:
            print("\n" + "=" * 30)
            print("🏠 MAIN MENU")
            print("=" * 30)
            print("(b) 🛒 Buy product")
            print("(m) 👨 Admin mode")
            print("(s) 🔌 Shutdown")
            print("=" * 30)

            cmd = input("🎯 Select: ")
            if cmd == "b":
                self.buy_menu()
            elif cmd == "m":
                self.admin_menu()
            elif cmd == "s":
                self.shutdown()


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    vm = VendingMachine(password="1234")
    vm.run()
