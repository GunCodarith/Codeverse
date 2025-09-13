from typing import Dict
import os
import sys

# ===============================================================
# Vending Machine Program
# - All code/messages in English
# - Comments in Thai (อธิบายการทำงาน)
# ===============================================================

# -------------------------------
# Product class (คลาสสินค้า)
# -------------------------------
class Product:
    def __init__(self, name: str, price: int, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"{self.name} Price {self.price} Baht (Stock {self.stock})"

    def is_available(self):
        # ตรวจสอบว่าสินค้ามีคงเหลือหรือไม่
        return self.stock > 0

    def buy(self):
        # ลดจำนวนสินค้าลง 1 เมื่อซื้อสำเร็จ
        if self.is_available():
            self.stock -= 1
            return True
        return False


# -------------------------------
# Cash manager class (จัดการเงิน)
# -------------------------------
class CashManager:
    # ชนิดเงินที่รองรับ
    DENOMINATIONS = [1000, 500, 100, 50, 20, 10, 5, 2, 1]

    def __init__(self):
        self.cash: Dict[int, int] = {}

    def add(self, denom: int, count: int):
        # เพิ่มจำนวนธนบัตร/เหรียญเข้าไป
        self.cash[denom] = self.cash.get(denom, 0) + count

    def make_change(self, amount: int):
        # พยายามทอนเงินจากชนิดเงินที่มีอยู่
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
# File manager class (จัดการไฟล์ .txt)
# -------------------------------
class FileManager:
    @staticmethod
    def load_goods(file="Goods.txt"):
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
    def load_wallet(file="Wallet.txt"):
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
# Vending Machine class (เครื่องขายสินค้า)
# -------------------------------
class VendingMachine:
    def __init__(self, password="1234"):
        self.password = password
        self.products = FileManager.load_goods()
        self.cash_mgr = CashManager()
        self.cash_mgr.cash = FileManager.load_wallet()

    def format_cash(self, cash: Dict[int, int]) -> str:
        # แสดงเงินทอนหรือคืนเงินเป็นข้อความ
        lines = []
        for d in sorted(cash.keys(), reverse=True):
            lines.append(f"  {d} Baht x {cash[d]}")
        return "\n".join(lines) if lines else "  -"

    def show_products(self):
        # แสดงสินค้าเป็นตาราง
        print("\n--- Product List ---")
        print(f"{'Slot':<4}{'Name':<12}{'Price':<8}{'Stock':<8}{'Status':<8}")
        print("-" * 45)
        for i in range(1, 10):
            if i in self.products:
                p = self.products[i]
                status = "Available" if p.is_available() else "Out"
                print(f"{i:<4}{p.name:<12}{p.price:<8}{p.stock:<8}{status:<8}")
            else:
                print(f"{i:<4}{'Empty':<12}{'-':<8}{'-':<8}{'---':<8}")
        print("(e) Exit")

    def buy_menu(self):
        # เมนูซื้อสินค้า
        while True:
            self.show_products()
            choice = input("Select product slot: ")
            if choice == "e":
                break
            if not choice.isdigit() or int(choice) not in self.products:
                print("\n[Failed] Invalid product selection (case 3: Others)")
                continue
            self.process_purchase(self.products[int(choice)])

    def process_purchase(self, product: Product):
        # ขั้นตอนการซื้อสินค้า
        if not product.is_available():
            print(f"\n[Failed] {product.name} is out of stock (case 1)")
            return

        print(f"\nSelected {product.name}, Price {product.price} Baht")
        total = 0
        inserted = {}

        while total < product.price:
            money = input(f"Insert cash (Need {product.price - total} Baht, c=Cancel): ")
            if money == "c":
                if total > 0:
                    print("\n[Purchase Canceled] Return money:")
                    print(self.format_cash(inserted))
                else:
                    print("\n[Purchase Canceled] No cash inserted")
                return
            try:
                m = int(money)
                if m in CashManager.DENOMINATIONS:
                    inserted[m] = inserted.get(m, 0) + 1
                    total += m
                    print(f"Total inserted: {total} Baht")
                else:
                    print("\n[Failed] Unsupported denomination (case 3: Others)")
                    return
            except:
                print("\n[Failed] Invalid input (case 3: Others)")
                return

        # บันทึกเงินเข้าตู้
        for d, c in inserted.items():
            self.cash_mgr.add(d, c)

        # คำนวณเงินทอน
        change_amt = total - product.price
        change = {}
        if change_amt > 0:
            change = self.cash_mgr.make_change(change_amt)
            if change is None:
                print(f"\n[Failed] Cannot give change (case 2)")
                print(f"Refund {total} Baht:")
                print(self.format_cash(inserted))
                return

        # ตัด stock
        product.buy()
        print("\n[Purchase Successful!]")
        print(f"Product: {product.name}")
        print(f"Price: {product.price} Baht")
        print(f"Paid: {total} Baht")
        if change_amt > 0:
            print(f"Change {change_amt} Baht:")
            print(self.format_cash(change))

        FileManager.save_goods(self.products)
        FileManager.save_wallet(self.cash_mgr.cash)

    def admin_menu(self):
        # เมนูแอดมิน
        pwd = input("Enter admin password: ")
        if pwd != self.password:
            print("Wrong password")
            return
        while True:
            print("\n--- Admin Menu ---")
            print("(g) Setup Goods")
            print("(w) Setup Wallet")
            print("(c) Exit")
            cmd = input("Select: ")
            if cmd == "g":
                self.setup_goods()
            elif cmd == "w":
                self.setup_wallet()
            elif cmd == "c":
                break

    def setup_goods(self):
        # ตั้งค่าสินค้าใหม่ทั้งหมด
        self.products.clear()
        for i in range(1, 10):
            name = input(f"Slot {i} product name (empty=skip): ")
            if name == "":
                continue
            try:
                price = int(input("Price: "))
                stock = int(input("Quantity: "))
                self.products[i] = Product(name, price, stock)
            except:
                print("Invalid input, skipped")
        FileManager.save_goods(self.products)

    def setup_wallet(self):
        # ตั้งค่าเงินใหม่ทั้งหมด
        for d in CashManager.DENOMINATIONS:
            try:
                cnt = int(input(f"Quantity of {d} Baht: "))
                self.cash_mgr.cash[d] = cnt
            except:
                self.cash_mgr.cash[d] = 0
        FileManager.save_wallet(self.cash_mgr.cash)

    def shutdown(self):
        # ปิดระบบ
        pwd = input("Enter password to shutdown: ")
        if pwd == self.password:
            print("System shutdown")
            sys.exit()
        else:
            print("Wrong password")

    def run(self):
        # เมนูหลัก
        while True:
            print("\n--- Main Menu ---")
            print("(b) Buy product")
            print("(m) Admin mode")
            print("(s) Shutdown")
            cmd = input("Select: ")
            if cmd == "b":
                self.buy_menu()
            elif cmd == "m":
                self.admin_menu()
            elif cmd == "s":
                self.shutdown()


# -------------------------------
# Main program
# -------------------------------
if __name__ == "__main__":
    try:
        print("🚀 Vending Machine started (Run in Spyder Console)")
        vm = VendingMachine(password="1234")
        vm.run()
    except KeyboardInterrupt:
        print("\nProgram stopped manually.")
