from typing import Dict, Optional, Tuple
import time
import getpass

# -------------------------------
# Class Product (สินค้า)
# -------------------------------
class Product:
    """Represents a product in the vending machine."""

    def __init__(self, name: str, price: int, stock: int):
        # ตรวจสอบความถูกต้องของข้อมูลสินค้า
        if not name or not isinstance(name, str):
            raise ValueError("ชื่อสินค้าต้องเป็นสตริงและไม่ว่าง")
        if price <= 0:
            raise ValueError("ราคาสินค้าต้องมากกว่า 0 บาท")
        if stock < 0:
            raise ValueError("จำนวนสต็อกไม่สามารถติดลบได้")
        self.name = name       # ชื่อสินค้า
        self.price = price     # ราคาสินค้า
        self.stock = stock     # จำนวนคงเหลือ

    def __str__(self):
        return f"{self.name} - Price: {self.price} Baht - Stock: {self.stock}"

    def is_available(self) -> bool:
        """Check if the product is available in stock."""
        # มีของพร้อมขายหรือไม่
        return self.stock > 0

    def buy(self) -> bool:
        """Attempt to buy one unit of the product."""
        # ลดสต็อก 1 ชิ้น ถ้ามีอยู่
        if self.is_available():
            self.stock -= 1
            return True
        return False


# -------------------------------
# Class CashMgr (จัดการเงินในเครื่อง)
# -------------------------------
class CashMgr:
    """Manages the cash inside the vending machine."""

    COINS = [1, 2, 5, 10]
    NOTES = [20, 50, 100, 500, 1000]
    DENOMINATIONS = COINS + NOTES

    def __init__(self):
        # dict เก็บจำนวนเงินแต่ละชนิด {denom: count}
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        """Add money to the machine (user insert or admin top-up)."""
        # เพิ่มจำนวนธนบัตร/เหรียญในเครื่อง
        if denom in self.DENOMINATIONS and count >= 0:
            self.cash[denom] = self.cash.get(denom, 0) + count

    def remove(self, denom: int, count: int):
        """Remove given count of denom from the machine (for making change)."""
        # ตัดจำนวนธนบัตร/เหรียญออกเมื่อทอน
        if count < 0:
            raise ValueError("จำนวนที่ลบต้องไม่ติดลบ")
        current = self.cash.get(denom, 0)
        if count > current:
            raise ValueError("เงินในเครื่องไม่พอที่จะตัดออก")
        self.cash[denom] = current - count

    def snapshot(self) -> Dict[int, int]:
        """Return a copy of current cash state."""
        # สำเนาสภาพเงินในเครื่อง เพื่อรองรับ transaction/rollback
        return dict(self.cash)

    def restore(self, snap: Dict[int, int]):
        """Restore machine cash to a previous snapshot."""
        # คืนค่าเงินในเครื่องกลับเป็นสภาพก่อนหน้า
        self.cash = dict(snap)

    def _bounded_min_items_change(self, amt: int, available: Dict[int, int]) -> Optional[Dict[int, int]]:
        """
        Compute change using bounded coin change (minimize number of items),
        respecting available counts. Returns {denom: count} or None if impossible.
        """
        # อัลกอริทึม bounded change แบบ DP: ใช้จำนวนเหรียญ/ธนบัตรให้น้อยที่สุด ภายใต้ข้อจำกัดจำนวนที่มีจริง
        if amt < 0:
            return None
        if amt == 0:
            return {}

        # dp[a] = dict ของชุดเงินที่รวมกันได้ a บาท (และเป็นชุดที่มีจำนวนชิ้นน้อยที่สุด ณ ตอนพบ)
        dp: list[Optional[Dict[int, int]]] = [None] * (amt + 1)
        dp[0] = {}

        # เดินทีละชนิด โดยแตกการใช้เป็น "ครั้งละ 1 ใบ/เหรียญ" แบบ bounded
        # วิธีนี้รับประกันว่าใช้ไม่เกิน available[denom] และถ้าเจอวิธีใหม่ที่จำนวนชิ้นน้อยกว่า จะอัปเดต
        for denom in sorted(available.keys()):
            count = max(0, int(available.get(denom, 0)))
            for _ in range(count):
                # วิ่งจาก amt ลงมา เพื่อไม่ใช้ banknote/coin เดิมซ้ำในการคำนวณรอบเดียวกัน
                for a in range(amt, denom - 1, -1):
                    if dp[a - denom] is not None:
                        prev_combo = dp[a - denom]
                        candidate = dict(prev_combo)
                        candidate[denom] = candidate.get(denom, 0) + 1
                        if dp[a] is None:
                            dp[a] = candidate
                        else:
                            # เลือกชุดที่จำนวนชิ้นรวม (notes+coins) น้อยกว่า เพื่อ UX ที่ดีกว่า
                            if sum(candidate.values()) < sum(dp[a].values()):
                                dp[a] = candidate

        return dp[amt]

    def can_change(self, amt: int) -> bool:
        """Check if change can be provided with current cash."""
        # ตรวจสอบว่า "สามารถทอน" ได้จริง โดยพิจารณาจำนวนที่มีอยู่จริง
        if amt < 0:
            return False
        return self._bounded_min_items_change(amt, self.cash) is not None

    def make_change(self, amt: int) -> Optional[Dict[int, int]]:
        """Return and COMMIT the actual change distribution if possible."""
        # คำนวณเงินทอน และ "ตัด" ออกจากเครื่องทันที (commit)
        if amt == 0:
            return {}
        combo = self._bounded_min_items_change(amt, self.cash)
        if combo is None:
            return None
        for d, c in combo.items():
            self.remove(d, c)
        return combo

    def show_change(self, change: Dict[int, int]):
        """Display details of the change given."""
        # แสดงรายละเอียดเงินทอน แยกเหรียญ/ธนบัตรเพื่อความอ่านง่าย
        coin_change = {d: c for d, c in change.items() if d in self.COINS}
        note_change = {d: c for d, c in change.items() if d in self.NOTES}

        if note_change:
            print("       💵 BANKNOTES:")
            for note in sorted(note_change.keys()):
                print(f"          • {note} Baht × {note_change[note]} notes")
        if coin_change:
            print("       🪙 COINS:")
            for coin in sorted(coin_change.keys()):
                print(f"          • {coin} Baht × {coin_change[coin]} coins")


# -------------------------------
# Class FileMgr (โหลด/บันทึกไฟล์)
# -------------------------------
class FileMgr:
    """Handles loading and saving of product and wallet data."""

    @staticmethod
    def load_goods(file: str = "Goods.txt") -> Dict[int, Product]:
        # โหลดสินค้าจากไฟล์ .txt รูปแบบ: num,name,price,stock (คอมมา)
        products: Dict[int, Product] = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(',')
                    if len(parts) != 4:
                        continue
                    num, name, price, stock = parts
                    try:
                        slot = int(num)
                        products[slot] = Product(name.strip(), int(price), int(stock))
                    except ValueError:
                        # ข้ามบรรทัดที่ข้อมูลไม่ถูกต้อง
                        continue
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return products

    @staticmethod
    def save_goods(products: Dict[int, Product], file: str = "Goods.txt"):
        # เซฟสินค้าเก็บลงไฟล์ .txt รูปแบบ: num,name,price,stock
        with open(file, 'w', encoding='utf-8') as f:
            f.write("# num,name,price,stock\n")
            for num, p in sorted(products.items()):
                f.write(f"{num},{p.name},{p.price},{p.stock}\n")

    @staticmethod
    def load_wallet(file: str = "Wallet.txt") -> Dict[int, int]:
        # โหลดจำนวนเงินจากไฟล์ .txt รูปแบบ: denom,count (คอมมา)
        cash: Dict[int, int] = {}
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(',')
                    if len(parts) != 2:
                        continue
                    denom, count = parts
                    try:
                        d = int(denom)
                        c = int(count)
                        if d in CashMgr.DENOMINATIONS and c >= 0:
                            cash[d] = c
                    except ValueError:
                        # ข้ามบรรทัดที่ข้อมูลไม่ถูกต้อง
                        continue
        except FileNotFoundError:
            print(f"        ⚠️  File {file} not found")
        return cash

    @staticmethod
    def save_wallet(cash: Dict[int, int], file: str = "Wallet.txt"):
        # เซฟเงินเก็บลงไฟล์ .txt รูปแบบ: denom,count
        with open(file, 'w', encoding='utf-8') as f:
            f.write("# denom,count\n")
            for denom in sorted(cash.keys()):
                f.write(f"{denom},{cash[denom]}\n")


# -------------------------------
# Class VendingMachine (เครื่องขายอัตโนมัติ)
# -------------------------------
class VendingMachine:
    """Main vending machine system with shopping and admin features."""

    def __init__(self, password: str = "1234"):
        # ตั้งรหัสผ่านตามที่ผู้ใช้ต้องการ (แบบเดิม)
        self.password = password             # รหัสสำหรับเข้า Maintenance
        self.products: Dict[int, Product] = {}
        self.cash_mgr = CashMgr()
        self.load_data()

    # ---------- UI Helpers ----------
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
            time.sleep(0.15)
        print(" ✅ Complete!\n")

    # ---------- Persistence ----------
    def load_data(self):
        # โหลดสินค้าและเงินจากไฟล์
        self.loading_animation("Loading data from files", 0.8)
        self.products = FileMgr.load_goods()
        self.cash_mgr.cash = FileMgr.load_wallet()

    def save_data(self):
        # เซฟข้อมูลกลับไปเก็บ
        self.loading_animation("Saving data to files", 0.5)
        FileMgr.save_goods(self.products)
        FileMgr.save_wallet(self.cash_mgr.cash)

    # ---------- Display ----------
    def show_products(self):
        # แสดงรายการสินค้า
        self.print_title("🛍️  PRODUCT SHOWCASE  🛍️")
        print()
        max_slot = max(self.products.keys(), default=9)
        max_slot = max(max_slot, 9)  # อย่างน้อย 9 ช่องเหมือนเดิม
        for i in range(1, max_slot + 1):
            if i in self.products:
                p = self.products[i]
                status = "✅ Available" if p.is_available() else "❌ Out of Stock"
                print(f"      ({i}) {p.name:<20} {p.price:>3}฿  Qty: {p.stock:>2}  {status}")
            else:
                print(f"      ({i}) {'Empty Slot':<20} ---   Qty: --  🚫 No Product")

        print("\n      (e) 🚪 Exit Product Selection")
        print("\n" + "─" * 62)

    # ---------- Shopping Flow ----------
    def buy_menu(self):
        # เมนูซื้อสินค้า
        while True:
            self.show_products()
            choice = input("\n    ➤ Enter choice (slot number or 'e'): ").strip().lower()
            if choice == 'e':
                break
            if not choice.isdigit():
                print("\n    ⚠️ Invalid selection (numbers only)")
                continue

            product_num = int(choice)
            if product_num not in self.products:
                print("\n    ⚠️ Slot not configured")
                continue

            if self.process_purchase(self.products[product_num]):
                self.save_data()
                input("\n    🎉 Press Enter to continue...")

    def process_purchase(self, product: Product) -> bool:
        # ขั้นตอนซื้อสินค้า (แบบ transaction-safe)
        if not product.is_available():
            print("\n    ❌ Out of stock")
            return False

        self.print_title("💳  PAYMENT TERMINAL  💳")
        print(f"    🛍️  Selected Product: {product.name}")
        print(f"    💰 Price: {product.price} Baht")

        total_paid, inserted_money = self.collect_payment(product.price)
        if total_paid is None:
            # ผู้ใช้ยกเลิก → คืนเงิน (ที่ยังคงอยู่กับผู้ใช้ เพราะยังไม่ใส่เข้าตู้)
            return False

        change_amount = total_paid - product.price

        # ทำงานแบบธุรกรรม: snapshot → add inserted → try change → commit/rollback
        snap = self.cash_mgr.snapshot()

        # เติมเงินเข้าตู้แบบชั่วคราว
        for denom, count in inserted_money.items():
            self.cash_mgr.add(denom, count)

        # คำนวณและ "commit" เงินทอน
        change_detail: Dict[int, int] = {}
        if change_amount > 0:
            change_detail = self.cash_mgr.make_change(change_amount) or {}

        if change_amount > 0 and not change_detail:
            # ทอนไม่ได้ → rollback ทั้งหมด และแจ้งคืนเงิน
            self.cash_mgr.restore(snap)
            print("\n    ❌ Transaction failed: no change available")
            print("    🔁 Refunding inserted money:")
            self.cash_mgr.show_change(inserted_money)  # ใช้ฟังก์ชันเดิมแสดงเป็นรูปแบบเดียวกัน
            return False

        # หักสต็อก (commit ฝั่งสินค้า)
        product.buy()

        # แสดงผลลัพธ์สำเร็จ
        print("\n    🎉 Purchase successful!")
        print(f"    📥 Paid: {total_paid} Baht")
        print(f"    💸 Change: {change_amount} Baht")
        if change_detail:
            self.cash_mgr.show_change(change_detail)
        return True

    def collect_payment(self, price: int) -> Tuple[Optional[int], Optional[Dict[int, int]]]:
        # รับเงินจากผู้ซื้อ (ยังไม่บันทึกเข้าเครื่อง จนกว่าจะรู้ว่าให้ทอนได้)
        total = 0
        inserted: Dict[int, int] = {}
        valid_money = set(CashMgr.DENOMINATIONS)

        while total < price:
            remaining = price - total
            print(f"\n      💰 Current Total: {total} Baht")
            print(f"      🎯 Amount Needed: {remaining} Baht")
            choice = input("\n      ➤ Insert money (1,2,5,10,20,50,100,500,1000) or 'c' to cancel: ").strip().lower()

            if choice == 'c':
                print("\n      🚫 Payment cancelled (no money was taken)")
                return None, None

            try:
                amount = int(choice)
                if amount in valid_money:
                    inserted[amount] = inserted.get(amount, 0) + 1
                    total += amount
                else:
                    print("      ❌ Invalid denomination")
            except ValueError:
                print("      ⚠️ Numbers only")
        return total, inserted

    # ---------- Maintenance ----------
    def maintenance_menu(self):
        # เมนูผู้ดูแลระบบ (แบบเดิมตามคำขอ แต่ใช้ getpass เพื่อ UX ที่ดีกว่าเล็กน้อย)
        self.print_title("🔐  SECURE ACCESS  🔐")
        try:
            password = getpass.getpass("    🔑 Enter password: ")
        except Exception:
            password = input("    🔑 Enter password: ")

        if password != self.password:
            print("\n    ❌ ACCESS DENIED")
            return
        print("\n    ✅ ACCESS GRANTED")
        time.sleep(0.5)

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
        # ตั้งค่าสินค้าใหม่ทั้งหมด (เขียนทับไฟล์เดิม)
        self.products.clear()
        # อนุญาตเกิน 9 ช่องได้ แต่ขั้นต่ำ 1-9 จะโชว์เหมือนเดิม
        print("\n      ℹ️ Leave name empty to skip a slot")
        for i in range(1, 10):
            name = input(f"      ➤ Product name for slot {i} (Enter to skip): ").strip()
            if not name:
                continue
            try:
                price = int(input("      ➤ Price (>=1 Baht): "))
                stock = int(input("      ➤ Initial stock (>=0): "))
                self.products[i] = Product(name, price, stock)
            except ValueError:
                print("      ⚠️ Invalid input, skipping this slot.")
        self.save_data()

    def setup_wallet(self):
        # ตั้งค่าเงินในเครื่อง (เขียนทับไฟล์เดิม)
        self.cash_mgr.cash.clear()
        print("\n      ℹ️ Leave blank for zero")
        for denom in CashMgr.DENOMINATIONS:
            while True:
                raw = input(f"      ➤ {denom} Baht count: ").strip()
                if raw == "":
                    self.cash_mgr.cash[denom] = 0
                    break
                try:
                    cnt = int(raw)
                    if cnt < 0:
                        print("      ⚠️ Must be >= 0")
                        continue
                    self.cash_mgr.cash[denom] = cnt
                    break
                except ValueError:
                    print("      ⚠️ Numbers only")
        self.save_data()

    def shutdown(self):
        # ปิดระบบ (ต้องใช้รหัสผ่าน)
        self.print_title("🔐  SYSTEM SHUTDOWN  🔐")
        try:
            password = getpass.getpass("    🔑 Enter shutdown password: ")
        except Exception:
            password = input("    🔑 Enter shutdown password: ")

        if password == self.password:
            print("\n    ✅ Password accepted")
            for i in range(3, 0, -1):
                print(f"    🔄 Shutting down in {i}...")
                time.sleep(0.8)
            print("\n    🛑 System shutdown complete")
            raise SystemExit(0)
        else:
            print("\n    ❌ ACCESS DENIED")

    # ---------- Main Loop ----------
    def run(self):
        # เมนูหลักของเครื่องขาย
        print("\n")
        print("🌟" + "═" * 40 + "🌟")
        print()
        print("      🏪  VENDING MACHINE  🏪")
        print("      ✨  Welcome to Shopping  ✨")
        print()
        print("🌟" + "═" * 40 + "🌟")
        time.sleep(1.0)

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
    time.sleep(0.5)
    vending_machine = VendingMachine(password="1234")
    vending_machine.run()
