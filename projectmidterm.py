from typing import Dict, Optional, Tuple
from datetime import datetime
import time

class Product:
    def __init__(self, name: str, price: int, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"{self.name} - Price: {self.price} Baht - Stock: {self.stock}"

    def is_available(self) -> bool:
        return self.stock > 0

    def buy(self) -> bool:
        if self.is_available():
            self.stock -= 1
            return True
        return False

class CashMgr:
    # Per requirements: coins 1,2,5,10 Baht and banknotes 20,50,100,500,1000 Baht
    COINS = [1, 2, 5, 10]
    NOTES = [20, 50, 100, 500, 1000]
    DENOMINATIONS = COINS + NOTES

    def __init__(self):
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        if denom in self.DENOMINATIONS and count >= 0:
            self.cash[denom] = self.cash.get(denom, 0) + count

    def can_change(self, amt: int) -> bool:
        return self._calc_change(amt, simulate=True) is not None

    def make_change(self, amt: int) -> Optional[Dict[int, int]]:
        return self._calc_change(amt, simulate=False)

    def _calc_change(self, amt: int, simulate=False) -> Optional[Dict[int, int]]:
        change = {}
        temp_cash = self.cash.copy()
        
        for denom in sorted(self.DENOMINATIONS, reverse=True):
            count = min(amt // denom, temp_cash.get(denom, 0))
            if count > 0:
                change[denom] = count
                amt -= denom * count
                temp_cash[denom] -= count
        
        if amt == 0:
            if not simulate:
                for denom, count in change.items():
                    self.cash[denom] = max(0, self.cash[denom] - count)
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

class FileMgr:
    @staticmethod
    def load_goods(file: str = "Goods.txt") -> Dict[int, Product]:
        products = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        num, name, price, stock = parts
                        products[int(num)] = Product(name, int(price), int(stock))
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return products

    @staticmethod
    def save_goods(products: Dict[int, Product], file: str = "Goods.txt"):
        with open(file, 'w', encoding='utf-8') as f:
            for num, p in products.items():
                f.write(f"{num},{p.name},{p.price},{p.stock}\n")

    @staticmethod
    def load_wallet(file: str = "Wallet.txt") -> Dict[int, int]:
        cash = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        denom, count = parts
                        cash[int(denom)] = int(count)
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return cash

    @staticmethod
    def save_wallet(cash: Dict[int, int], file: str = "Wallet.txt"):
        with open(file, 'w', encoding='utf-8') as f:
            for denom, count in cash.items():
                f.write(f"{denom},{count}\n")

class VendingMachine:
    def __init__(self, password: str = "1234"):
        self.password = password
        self.products: Dict[int, Product] = {}
        self.cash_mgr = CashMgr()
        self.load_data()

    def print_title(self, title: str):
        """Print beautiful title with stars decoration"""
        print("\n")
        print("✨" + "═" * 58 + "✨")
        print(f"    {title}")
        print("✨" + "═" * 58 + "✨")

    def print_section(self, title: str):
        """Print section header"""
        print(f"\n🔸 {title}")
        print("   " + "─" * 50)

    def loading_animation(self, text: str, duration: float = 1.0):
        """Show loading animation"""
        print(f"\n    🔄 {text}", end="", flush=True)
        for _ in range(int(duration * 4)):
            print(".", end="", flush=True)
            time.sleep(0.25)
        print(" ✅ Complete!\n")

    def load_data(self):
        """Load data from Hard Disk to Main Memory"""
        self.loading_animation("Loading data from files", 1.5)
        self.products = FileMgr.load_goods()
        self.cash_mgr.cash = FileMgr.load_wallet()

    def save_data(self):
        """Save data from Main Memory to Hard Disk"""
        self.loading_animation("Saving data to files", 1.0)
        FileMgr.save_goods(self.products)
        FileMgr.save_wallet(self.cash_mgr.cash)

    def show_products(self):
        """Display product list with beautiful formatting"""
        self.print_title("🛍️  PRODUCT SHOWCASE  🛍️")
        
        print()
        for i in range(1, 10):
            if i in self.products:
                p = self.products[i]
                if p.is_available():
                    status = "✅ Available"
                    print(f"      ({i}) {p.name:<20} {p.price:>3}฿  Qty: {p.stock:>2}  {status}")
                else:
                    status = "❌ Out of Stock"
                    print(f"      ({i}) {p.name:<20} {p.price:>3}฿  Qty: {p.stock:>2}  {status}")
            else:
                print(f"      ({i}) {'Empty Slot':<20} {'---':>3}   Qty: {'--':>2}  🚫 No Product")
        
        print("\n      (e) 🚪 Exit Product Selection")
        print("\n" + "─" * 62)

    def buy_menu(self):
        """Buy menu with enhanced UI"""
        while True:
            self.show_products()
            print("\n    🎯 Make your selection:")
            choice = input("    ➤ Enter choice (1-9 or 'e'): ").strip().lower()
            
            if choice == 'e':
                print("\n    👋 Returning to main menu...")
                time.sleep(0.8)
                break
                
            if choice.isdigit() and 1 <= int(choice) <= 9:
                product_num = int(choice)
                if product_num in self.products:
                    result = self.process_purchase(self.products[product_num])
                    if result:
                        self.save_data()
                        input("\n    🎉 Press Enter to continue shopping...")
                else:
                    print("\n    ❌ Sorry, no product available at this position!")
                    time.sleep(1.5)
            else:
                print("\n    ⚠️  Please select numbers 1-9 or 'e' only")
                time.sleep(1.5)

    def process_purchase(self, product: Product) -> bool:
        """Product purchase process with beautiful UI"""
        # Check product availability
        if not product.is_available():
            self.show_sale_failed(product, 0, 1, "Out of stock")
            return False

        self.print_title("💳  PAYMENT TERMINAL  💳")
        print(f"    🛍️  Selected Product: {product.name}")
        print(f"    💰 Price: {product.price} Baht")
        print(f"    📦 Stock Available: {product.stock} units")
        
        # Collect payment
        total_paid, inserted_money = self.collect_payment(product.price)
        if total_paid is None:
            return False

        change_amount = total_paid - product.price
        
        # Check change availability
        if change_amount > 0:
            if not self.cash_mgr.can_change(change_amount):
                self.show_sale_failed(product, total_paid, 2, "No change available")
                self.return_money(inserted_money)
                return False

        # Processing transaction
        print("\n    ⚙️  Processing transaction...")
        time.sleep(1.5)

        # Add customer money to machine
        for denom, count in inserted_money.items():
            self.cash_mgr.add(denom, count)

        # Make change
        if change_amount > 0:
            change_detail = self.cash_mgr.make_change(change_amount)
        else:
            change_detail = {}

        # Complete sale
        product.buy()
        
        # Show successful sale
        self.show_sale_success(product, total_paid, change_amount, change_detail)
        return True

    def collect_payment(self, price: int) -> Tuple[Optional[int], Optional[Dict[int, int]]]:
        """Collect payment with enhanced UI"""
        total = 0
        inserted = {}
        valid_money = [1, 2, 5, 10, 20, 50, 100, 500, 1000]

        self.print_section(f"💵 PAYMENT REQUIRED: {price} Baht")

        while total < price:
            remaining = price - total
            print(f"\n      💰 Current Total: {total} Baht")
            print(f"      🎯 Amount Needed: {remaining} Baht")
            print(f"      💸 Valid Money: {valid_money}")
            
            choice = input("\n      ➤ Insert money or 'c' to cancel: ").strip().lower()
            
            if choice == 'c':
                print("\n      🚫 Payment cancelled by user")
                if inserted:
                    print("\n      💸 Returning your money...")
                    time.sleep(1.0)
                    self.show_money_detail(inserted, "MONEY RETURNED")
                return None, None

            try:
                amount = int(choice)
                if amount in valid_money:
                    inserted[amount] = inserted.get(amount, 0) + 1
                    total += amount
                    print(f"      ✅ Accepted: {amount} Baht (Running total: {total} Baht)")
                    time.sleep(0.5)
                else:
                    print(f"      ❌ Invalid denomination! Use: {valid_money}")
            except ValueError:
                print("      ⚠️  Numbers only please!")

        return total, inserted

    def show_sale_success(self, product: Product, paid: int, change_amt: int, change_detail: Dict[int, int]):
        """Display successful sale with beautiful formatting"""
        self.print_title("🎉  TRANSACTION SUCCESSFUL  🎉")
        
        print(f"      🛍️  Product: {product.name}")
        print(f"      💰 Unit Price: {product.price} Baht")
        print(f"      💵 Amount Paid: {paid} Baht")
        print(f"      💸 Change Due: {change_amt} Baht")
        print()
        print(f"      📦 Dispensing: {product.name}")
        print(f"      📊 Remaining Stock: {product.stock} units")
        
        if change_detail:
            print("\n    💰 YOUR CHANGE:")
            self.cash_mgr.show_change(change_detail)
            print("\n    🎁 Please collect your product and change!")
        else:
            print("\n    🎁 Please collect your product!")
            print("    ✨ Exact payment - No change required")

    def show_sale_failed(self, product: Product, paid: int, error_type: int, reason: str):
        """Display failed sale with beautiful formatting"""
        self.print_title("❌  TRANSACTION FAILED  ❌")
        
        print(f"      🚫 Reason: {reason}")
        print(f"      🛍️  Product: {product.name}")
        print(f"      💰 Price: {product.price} Baht")
        
        if paid > 0:
            print(f"      💵 Amount Paid: {paid} Baht")

    def return_money(self, money: Dict[int, int]):
        """Return money to customer with beautiful formatting"""
        print("\n    💸 Returning your money...")
        time.sleep(1.0)
        self.show_money_detail(money, "MONEY RETURNED")

    def show_money_detail(self, money: Dict[int, int], title: str = "MONEY DETAILS"):
        """Show money details with enhanced formatting"""
        self.print_title(f"💰  {title}  💰")
        
        coins = {d: c for d, c in money.items() if d in [1, 2, 5, 10]}
        notes = {d: c for d, c in money.items() if d in [20, 50, 100, 500, 1000]}
        
        if coins:
            print("      🪙 COINS:")
            for coin in sorted(coins.keys()):
                print(f"         • {coin} Baht × {coins[coin]} coins")
        
        if notes:
            if coins:
                print()
            print("      💵 BANKNOTES:")
            for note in sorted(notes.keys()):
                print(f"         • {note} Baht × {notes[note]} notes")
        
        if not coins and not notes:
            print("      No money to display")

    def maintenance_menu(self):
        """Maintenance menu with enhanced security UI"""
        self.print_title("🔐  SECURE ACCESS  🔐")
        password = input("    🔑 Enter maintenance password: ")
        
        if password != self.password:
            print("\n    ❌ ACCESS DENIED - Incorrect password!")
            time.sleep(2.0)
            return

        print("\n    ✅ ACCESS GRANTED - Welcome Administrator!")
        time.sleep(1.0)

        while True:
            self.print_title("⚙️   MAINTENANCE CENTER   ⚙️")
            
            print("\n      🌈 ✨ Available Operations ✨ 🌈")
            print("         " + "─" * 30)
            print()
            print("      📦 (g) Setup Products")
            print("           Manage Inventory")
            print()
            print("      💰 (w) Setup Cash")
            print("           Manage Denominations")
            print()
            print("      🚪 (c) Exit Maintenance")
            print("           Return to Main Menu")
            
            choice = input("\n      ➤ Select operation (g/w/c): ").strip().lower()
            
            if choice == 'g':
                self.setup_goods()
            elif choice == 'w':
                self.setup_wallet()
            elif choice == 'c':
                print("\n    👋 Exiting maintenance mode...")
                time.sleep(1.0)
                break
            else:
                print("\n    ⚠️  Please select g, w, or c only")
                time.sleep(1.5)

    def setup_goods(self):
        """Setup goods with beautiful interface"""
        self.print_title("📦  INVENTORY MANAGEMENT  📦")
        print("    💡 Product price must be between 10-100 Baht")
        print("    🎯 Setting up 9 product slots...")
        
        self.products.clear()
        
        for i in range(1, 10):
            self.print_section(f"📝 Configuring Product Slot #{i}")
            
            name = input(f"      ➤ Product name (Enter to skip): ").strip()
            if not name:
                print(f"      ⏭️  Slot {i} skipped - Empty slot")
                continue
                
            while True:
                try:
                    price = int(input("      ➤ Price (10-100 Baht): "))
                    if 10 <= price <= 100:
                        break
                    else:
                        print("      ⚠️  Price must be between 10-100 Baht")
                except ValueError:
                    print("      ⚠️  Please enter numbers only")
            
            while True:
                try:
                    stock = int(input("      ➤ Initial stock quantity: "))
                    if stock >= 0:
                        break
                    else:
                        print("      ⚠️  Quantity cannot be negative")
                except ValueError:
                    print("      ⚠️  Please enter numbers only")
            
            self.products[i] = Product(name, price, stock)
            print(f"      ✅ Slot {i}: {name} configured successfully!")
        
        self.save_data()
        print("\n    🎉 All product configurations saved successfully!")
        input("\n    📋 Press Enter to continue...")

    def setup_wallet(self):
        """Setup wallet with beautiful interface"""
        self.print_title("💰  CASH MANAGEMENT SYSTEM  💰")
        print("    🏦 Configuring machine's cash inventory...")
        
        self.cash_mgr.cash.clear()
        
        self.print_section("🪙 COIN INVENTORY")
        for coin in [1, 2, 5, 10]:
            while True:
                try:
                    count = int(input(f"      ➤ {coin} Baht coins quantity: "))
                    if count >= 0:
                        self.cash_mgr.cash[coin] = count
                        print(f"      ✅ {coin}฿ coins: {count} pieces loaded")
                        break
                    else:
                        print("      ⚠️  Quantity cannot be negative")
                except ValueError:
                    print("      ⚠️  Please enter numbers only")
        
        self.print_section("💵 BANKNOTE INVENTORY")
        for note in [20, 50, 100, 500, 1000]:
            while True:
                try:
                    count = int(input(f"      ➤ {note} Baht notes quantity: "))
                    if count >= 0:
                        self.cash_mgr.cash[note] = count
                        print(f"      ✅ {note}฿ notes: {count} pieces loaded")
                        break
                    else:
                        print("      ⚠️  Quantity cannot be negative")
                except ValueError:
                    print("      ⚠️  Please enter numbers only")
        
        # Show total cash value
        total = sum(denom * count for denom, count in self.cash_mgr.cash.items())
        print(f"\n    💎 Total cash value loaded: {total} Baht")
        
        self.save_data()
        print("    🎉 Cash inventory saved successfully!")
        input("\n    📋 Press Enter to continue...")

    def shutdown(self):
        """Enhanced shutdown with security"""
        self.print_title("🔐  SYSTEM SHUTDOWN  🔐")
        password = input("    🔑 Enter shutdown password: ")
        
        if password == self.password:
            print("\n    ✅ Password accepted")
            print("    ⚠️  Initiating system shutdown sequence...")
            
            for i in range(3, 0, -1):
                print(f"    🔄 Shutting down in {i}...")
                time.sleep(1)
            
            print("\n    🛑 System shutdown complete")
            print("    👋 Thank you for using our vending machine!")
            exit(0)
        else:
            print("\n    ❌ ACCESS DENIED - Incorrect password")
            print("    🛡️  Shutdown cancelled for security")
            time.sleep(2.0)

    def run(self):
        """Main program with beautiful welcome screen"""
        # Welcome screen
        print("\n")
        print("🌟" + "═" * 40 + "🌟")
        print()
        print("      🏪  VENDING MACHINE  🏪")
        print()
        print("      ✨  Welcome to Shopping  ✨")
        print()
        print("🌟" + "═" * 40 + "🌟")
        
        time.sleep(2.0)
        
        while True:
            self.print_title("🎮  MAIN CONTROL PANEL  🎮")
            
            print("\n      🌈 ✨ Available Services ✨ 🌈")
            print("         " + "─" * 30)
            print()
            print("      🛍️  (b) Shopping Center")
            print("           Browse & Buy Products")
            print()
            print("      ⚙️  (m) Maintenance Hub")
            print("           System Administration")
            print()
            print("      🛑 (s) Power Down")
            print("           Safe System Shutdown")
            print()
            print("      💫 Select your desired service below 💫")
            
            choice = input("\n      ➤ Enter your choice (b/m/s): ").strip().lower()
            
            if choice == 'b':
                print("\n    🛍️  Welcome to Shopping Center!")
                time.sleep(1.0)
                self.buy_menu()
            elif choice == 'm':
                self.maintenance_menu()
            elif choice == 's':
                self.shutdown()
            else:
                print("\n    ⚠️  Invalid selection! Please choose b, m, or s")
                time.sleep(1.5)

if __name__ == "__main__":
    # Default password: 1234
    print("🚀 Starting Vending Machine System...")
    time.sleep(1.0)
    
    vending_machine = VendingMachine()
    vending_machine.run()
