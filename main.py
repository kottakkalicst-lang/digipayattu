from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from datetime import datetime
import sqlite3

Window.size = (400, 700)

DB_NAME = "digipayattu.db"


# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone TEXT,
            amount REAL,
            giveback REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------- MAIN LAYOUT ----------
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        title = Label(
            text="Digipayattu",
            font_size=26,
            bold=True,
            size_hint_y=None,
            height=50
        )
        self.add_widget(title)

        # -------- Add Account Section --------
        self.name_input = TextInput(hint_text="Name", multiline=False)
        self.address_input = TextInput(hint_text="Address", multiline=False)
        self.phone_input = TextInput(hint_text="Phone", multiline=False)
        self.amount_input = TextInput(hint_text="Amount", multiline=False, input_filter='float')

        self.add_widget(self.name_input)
        self.add_widget(self.address_input)
        self.add_widget(self.phone_input)
        self.add_widget(self.amount_input)

        add_btn = Button(text="My Account (Save)", size_hint_y=None, height=50)
        add_btn.bind(on_press=self.save_account)
        self.add_widget(add_btn)

        # -------- Search Section --------
        self.search_input = TextInput(hint_text="Enter Name to Search", multiline=False)
        self.add_widget(self.search_input)

        search_btn = Button(text="Search Account", size_hint_y=None, height=50)
        search_btn.bind(on_press=self.search_account)
        self.add_widget(search_btn)

        # -------- Result Area --------
        self.result_area = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.result_area.bind(minimum_height=self.result_area.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.result_area)
        self.add_widget(scroll)

        # -------- Footer --------
        footer = Label(
            text="App: Digipayattu\nDeveloped By Jithesh Kottakkal",
            font_size=12,
            size_hint_y=None,
            height=50
        )
        self.add_widget(footer)

    # ---------- Save Account ----------
    def save_account(self, instance):
        name = self.name_input.text
        address = self.address_input.text
        phone = self.phone_input.text
        amount = self.amount_input.text

        if not name or not amount:
            self.popup("Error", "Name and Amount required")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            INSERT INTO accounts (name, address, phone, amount, giveback, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, address, phone, float(amount), 0, ""))
        conn.commit()
        conn.close()

        self.popup("Success", "Account Saved")
        self.clear_inputs()

    # ---------- Search Account ----------
    def search_account(self, instance):
        self.result_area.clear_widgets()
        name = self.search_input.text

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM accounts WHERE name LIKE ?", ('%' + name + '%',))
        rows = c.fetchall()
        conn.close()

        if not rows:
            self.result_area.add_widget(Label(text="No Records Found", size_hint_y=None, height=40))
            return

        for row in rows:
            self.result_area.add_widget(self.create_result_card(row))

    # ---------- Result Card ----------
    def create_result_card(self, row):
        box = BoxLayout(orientation='vertical', padding=10, size_hint_y=None, height=220)

        info = f"""
Name: {row[1]}
Address: {row[2]}
Phone: {row[3]}
Amount: ₹{row[4]}
GiveBack: ₹{row[5]}
Date: {row[6]}
"""
        box.add_widget(Label(text=info))

        giveback_input = TextInput(hint_text="Enter Give Back Amount", multiline=False, input_filter='float')
        box.add_widget(giveback_input)

        btn = Button(text="Give Back", size_hint_y=None, height=40)
        btn.bind(on_press=lambda x: self.update_giveback(row[0], giveback_input.text))
        box.add_widget(btn)

        return box

    # ---------- Update Give Back ----------
    def update_giveback(self, record_id, value):
        if not value:
            self.popup("Error", "Enter amount")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT giveback FROM accounts WHERE id=?", (record_id,))
        old = c.fetchone()[0]

        new_total = old + float(value)
        date_now = datetime.now().strftime("%d-%m-%Y %H:%M")

        c.execute("""
            UPDATE accounts
            SET giveback=?, date=?
            WHERE id=?
        """, (new_total, date_now, record_id))

        conn.commit()
        conn.close()

        self.popup("Success", "Give Back Updated")

    # ---------- Helpers ----------
    def popup(self, title, msg):
        Popup(title=title, content=Label(text=msg),
              size_hint=(None, None), size=(300, 200)).open()

    def clear_inputs(self):
        self.name_input.text = ""
        self.address_input.text = ""
        self.phone_input.text = ""
        self.amount_input.text = ""


# ---------- APP ----------
class DigiPayattuApp(App):
    def build(self):
        init_db()
        return MainLayout()


if __name__ == "__main__":
    DigiPayattuApp().run()
