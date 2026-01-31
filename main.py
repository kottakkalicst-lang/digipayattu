from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
import sqlite3

Window.size = (400, 700)

DB_NAME = "digipayattu.db"

PRIMARY = (0.10, 0.65, 0.60, 1)
DARK_BG = (0.08, 0.09, 0.11, 1)
CARD_BG = (0.14, 0.15, 0.18, 1)
TEXT_CLR = (1, 1, 1, 1)


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


# ---------- CARD WIDGET ----------
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*CARD_BG)
            self.rect = RoundedRectangle(radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ---------- MAIN LAYOUT ----------
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=15, padding=15, **kwargs)
        Window.clearcolor = DARK_BG

        # Header
        header = Label(
            text="DIGIPAYATTU",
            size_hint_y=None,
            height=60,
            font_size=24,
            bold=True,
            color=PRIMARY
        )
        self.add_widget(header)

        # Add Account Card
        form_card = Card(orientation='vertical', padding=15, spacing=10, size_hint_y=None, height=320)

        self.name_input = TextInput(hint_text="Name", multiline=False)
        self.address_input = TextInput(hint_text="Address", multiline=False)
        self.phone_input = TextInput(hint_text="Phone", multiline=False)
        self.amount_input = TextInput(hint_text="Amount", multiline=False, input_filter='float')

        form_card.add_widget(self.name_input)
        form_card.add_widget(self.address_input)
        form_card.add_widget(self.phone_input)
        form_card.add_widget(self.amount_input)

        add_btn = Button(text="Save Account", background_color=PRIMARY, size_hint_y=None, height=45)
        add_btn.bind(on_press=self.save_account)
        form_card.add_widget(add_btn)

        self.add_widget(form_card)

        # Search Card
        search_card = Card(orientation='vertical', padding=15, spacing=10, size_hint_y=None, height=140)

        self.search_input = TextInput(hint_text="Search by Name", multiline=False)
        search_btn = Button(text="Search", background_color=PRIMARY, size_hint_y=None, height=45)
        search_btn.bind(on_press=self.search_account)

        search_card.add_widget(self.search_input)
        search_card.add_widget(search_btn)

        self.add_widget(search_card)

        # Results
        self.result_area = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.result_area.bind(minimum_height=self.result_area.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.result_area)
        self.add_widget(scroll)

        # Footer
        footer = Label(
            text="Developed By Jithesh Kottakkal",
            size_hint_y=None,
            height=40,
            font_size=12,
            color=(0.7, 0.7, 0.7, 1)
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
        card = Card(orientation='vertical', padding=12, spacing=8, size_hint_y=None, height=240)

        info = Label(
            text=f"[b]{row[1]}[/b]\n₹{row[4]} | GiveBack ₹{row[5]}\n{row[2]}\n{row[3]}\nLast: {row[6]}",
            markup=True,
            color=TEXT_CLR
        )
        card.add_widget(info)

        giveback_input = TextInput(hint_text="Enter Give Back Amount", multiline=False, input_filter='float')
        card.add_widget(giveback_input)

        btn = Button(text="Give Back", background_color=PRIMARY, size_hint_y=None, height=40)
        btn.bind(on_press=lambda x: self.update_giveback(row[0], giveback_input.text))
        card.add_widget(btn)

        return card

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


class DigiPayattuApp(App):
    def build(self):
        init_db()
        return MainLayout()


if __name__ == "__main__":
    DigiPayattuApp().run()
