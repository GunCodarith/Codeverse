from typing import Dict, Optional, Tuple
import time

# -------------------------------
# Class Product (สินค้า)
# -------------------------------
class Product:
    def __init__(self, name: str, price: int, stock: int):
        self.name = name       # ชื่อสินค้า
        self.price = price     # ราคาสินค้า
        self.stock = stock     # จำนวนคงเหลือ

    def __str__(self):
        return f"{self.name} - Price: {self.price} Baht - Stock: {self.stock}"

    def is_available(self) -> bool:
        # ใช้เช็คว่าสินค้ามีเหลือไหม
        return self.stock > 0

    def buy(self) -> bool:
        # ถ้าซื้อสำเร็จ → ลด stock ลง 1
        if self.is_available():
            self.stock -= 1
            return True
        return False


# -------------------------------
# Class CashMgr (จัดการเงินในเครื่อง)
# -------------------------------
class CashMgr:
    COINS = [1, 2, 5, 10]
    NOTES = [20, 50, 100, 500, 1000]
    DENOMINATIONS = COINS + NOTES

    def __init__(self):
        self.cash: Dict[int, int] = {}  # dict เก็บจำนวนเงินแต่ละชนิด

    def add(self, denom: int, count: int):
        # เติมเงินเข้าตู้ (ตอนผู้ใช้หยอดหรือ admin เติม)
        if denom in self.DENOMINATIONS and count >= 0:
            self.cash[denom] = self.cash.get(denom, 0) + count

    def can_change(self, amt: int) -> bool:
        # ตรวจสอบว่ามีเงินพอทอนหรือไม่
        return self._calc_change(amt, simulate=True) is not None

    def make_change(self, amt: int) -> Optional[Dict[int, int]]:
        # คืน dict รายละเอียดเงินทอนจริง ๆ
        return self._calc_change(amt, simulate=False)

    def _calc_change(self, amt: int, simulate=False) -> Optional[Dict[int, int]]:
        # คำนวณทอนแบบ greedy (เริ่มจากธนบัตรใหญ่สุด)
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
        # แสดงรายละเอียดเงินทอน
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
# Class FileMgr (โหลด/บันทึกไฟล์)
# -------------------------------
class FileMgr:
    @staticmethod
    def load_goods(file: str = "Goods.txt") -> Dict[int, Product]:
        # โหลดสินค้าจากไฟล์
        products = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        num, name, price, stock = parts
                        try:
                            products[int(num)] = Product(name, int(price), int(stock))
                        except ValueError:
                            continue
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return products

    @staticmethod
    def save_goods(products: Dict[int, Product], file: str = "Goods.txt"):
        # เซฟสินค้าเก็บลงไฟล์
        with open(file, 'w', encoding='utf-8') as f:
            for num, p in products.items():
                f.write(f"{num},{p.name},{p.price},{p.stock}\n")

    @staticmethod
    def load_wallet(file: str = "Wallet.txt") -> Dict[int, int]:
        # โหลดจำนวนเงินจากไฟล์
        cash = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        denom, count = parts
                        try:
                            cash[int(denom)] = int(count)
                        except ValueError:
                            continue
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return cash

    @staticmethod
    def save_wallet(cash: Dict[int, int], file: str = "Wallet.txt"):
        # เซฟเงินเก็บลงไฟล์
        with open(file, 'w', encoding='utf-8') as f:
            for denom, count in cash.items():
                f.write(f"{denom},{count}\n")


# -------------------------------
# Class VendingMachine (เครื่องขายอัตโนมัติ)
# -------------------------------
class VendingMachine:
    def __init__(self, password: str = "1234"):
        self.password = password       # รหัสสำหรับเข้า Maintenance
        self.products: Dict[int, Product] = {}
        self.cash_mgr = CashMgr()
        self.load_data()

    def print_title(self, title: str):
        # แสดงหัวข้อแบบมีตกแต่ง
        print("\n")
        print("✨" + "═" * 58 + "✨")
        print(f"    {title}")
        print("✨" + "═" * 58 + "✨")

    def loading_animation(self, text: str, duration: float = 1.0):
        # effect โหลดข้อมูล
        print(f"\n    🔄 {text}", end="", flush=True)
        for _ in range(int(duration * 4)):
            print(".", end="", flush=True)
            time.sleep(0.25)
        print(" ✅ Complete!\n")

    def load_data(self):
        # โหลดสินค้าและเงินจากไฟล์
        self.loading_animation("Loading data from files", 1.5)
        self.products = FileMgr.load_goods()
        self.cash_mgr.cash = FileMgr.load_wallet()

    def save_data(self):
        # เซฟข้อมูลกลับไปเก็บ
        self.loading_animation("Saving data to files", 1.0)
        FileMgr.save_goods(self.products)
        FileMgr.save_wallet(self.cash_mgr.cash)

    def show_products(self):
        # แสดงรายการสินค้า
        self.print_title("🛍️  PRODUCT SHOWCASE  🛍️")
        print()
        for i in range(1, 10):
            if i in self.products:
                p = self.products[i]
                if p.is_available():
                    print(f"      ({i}) {p.name:<20} {p.price:>3}฿  Qty: {p.stock:>2}  ✅ Available")
                else:
                    print(f"      ({i}) {p.name:<20} {p.price:>3}฿  Qty: {p.stock:>2}  ❌ Out of Stock")
            else:
                print(f"      ({i}) {'Empty Slot':<20} ---   Qty: --  🚫 No Product")

        print("\n      (e) 🚪 Exit Product Selection")
        print("\n" + "─" * 62)

    def buy_menu(self):
        # เมนูซื้อสินค้า
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
        # ขั้นตอนซื้อสินค้า
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

        # เติมเงินเข้าตู้
        for denom, count in inserted_money.items():
            self.cash_mgr.add(denom, count)

        # ทำการทอน
        change_detail = self.cash_mgr.make_change(change_amount) if change_amount > 0 else {}

        # ลด stock
        product.buy()

        # แสดงผลลัพธ์
        print("\n    🎉 Purchase successful!")
        print(f"    💸 Change: {change_amount} Baht")
        if change_detail:
            self.cash_mgr.show_change(change_detail)
        return True

    def collect_payment(self, price: int) -> Tuple[Optional[int], Optional[Dict[int, int]]]:
        # รับเงินจากผู้ซื้อ
        total = 0
        inserted = {}
        valid_money = [1, 2, 5, 10, 20, 50, 100, 500, 1000]

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

    def maintenance_menu(self):
        # เมนูผู้ดูแลระบบ
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
        # ตั้งค่าสินค้าใหม่ทั้งหมด
        self.products.clear()
        for i in range(1, 10):
            name = input(f"      ➤ Product name for slot {i} (Enter to skip): ").strip()
            if not name:
                continue
            price = int(input("      ➤ Price (10-100 Baht): "))
            stock = int(input("      ➤ Initial stock: "))
            self.products[i] = Product(name, price, stock)
        self.save_data()

    def setup_wallet(self):
        # ตั้งค่าเงินในเครื่อง
        self.cash_mgr.cash.clear()
        for coin in [1, 2, 5, 10]:
            count = int(input(f"      ➤ {coin} Baht coins: "))
            self.cash_mgr.cash[coin] = count
        for note in [20, 50, 100, 500, 1000]:
            count = int(input(f"      ➤ {note} Baht notes: "))
            self.cash_mgr.cash[note] = count
        self.save_data()

    def shutdown(self):
        # ปิดระบบ (ต้องใช้รหัสผ่าน)
        self.print_title("🔐  SYSTEM SHUTDOWN  🔐")
        password = input("    🔑 Enter shutdown password: ")
        if password == self.password:
            print("\n    ✅ Password accepted")
            for i in range(3, 0, -1):
                print(f"    🔄 Shutting down in {i}...")
                time.sleep(1)
            print("\n    🛑 System shutdown complete")
            exit(0)
        else:
            print("\n    ❌ ACCESS DENIED")

    def run(self):
        # เมนูหลักของเครื่องขาย
        print("\n")
        print("🌟" + "═" * 40 + "🌟")
        print()
        print("      🏪  VENDING MACHINE  🏪")
        print("      ✨  Welcome to Shopping  ✨")
        print()
        print("🌟" + "═" * 40 + "🌟")
        time.sleep(2.0)

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
                time.sleep(1.5)


# -------------------------------
# Main Program
# -------------------------------
if __name__ == "__main__":
    print("🚀 Starting Vending Machine System...")
    time.sleep(1.0)
    vending_machine = VendingMachine()
    vending_machine.run()
