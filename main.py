import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle

# ---------------- WINDOW ----------------
Window.clearcolor = get_color_from_hex("#0E0F1A")
Window.softinput_mode = "resize"

# ---------------- COLORS ----------------
BG_MAIN = "#0E0F1A"
CARD_BG = "#181A33"
TEXT_MAIN = "#F9FAFB"
TEXT_SUB = "#B5B8D1"
ACCENT = "#6366F1"
SUCCESS = "#22C55E"
WARNING = "#F97316"
INPUT_BG = "#0B0D1C"

DB_NAME = "digipayattu.db"


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone TEXT UNIQUE,
            received TEXT,
            returned TEXT,
            return_date TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------------- CARD ----------------
class Card(BoxLayout):
    def __init__(self, bg_color, radius=28, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ---------------- MAIN UI ----------------
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", size_hint=(1, 1), **kwargs)

        # -------- HEADER --------
        header = BoxLayout(
            orientation="vertical",
            padding=(24, 36),
            size_hint_y=None,
            height=170
        )

        header.add_widget(Label(
            text="DIGIPAYATTU",
            font_size=40,
            bold=True,
            color=get_color_from_hex(TEXT_MAIN),
            size_hint_y=None,
            height=70
        ))

        header.add_widget(Label(
            text="Developer • JITHESH KOTTAKKAL",
            font_size=18,
            color=get_color_from_hex(TEXT_SUB),
            size_hint_y=None,
            height=35
        ))

        self.add_widget(header)

        # -------- SCROLL --------
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical",
            padding=24,
            spacing=26,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        # -------- CARD --------
        card = Card(
            CARD_BG,
            orientation="vertical",
            padding=26,
            spacing=18,
            size_hint_y=None
        )
        card.bind(minimum_height=card.setter("height"))

        self.name = self.input_field("Name")
        self.address = self.input_field("Address")
        self.phone = self.input_field("Phone Number")
        self.received = self.input_field("Received Item")
        self.returned = self.input_field("Return Status")
        self.return_date = self.input_field("Return Date (YYYY-MM-DD)")

        for f in [
            self.name, self.address, self.phone,
            self.received, self.returned, self.return_date
        ]:
            card.add_widget(f)

        card.add_widget(self.button("ADD RECORD", ACCENT, self.add_data))
        card.add_widget(self.button("SEARCH RECORD", SUCCESS, self.search_data))
        card.add_widget(self.button("UPDATE RETURN", WARNING, self.update_return))

        self.status = Label(
            text="",
            font_size=18,
            color=get_color_from_hex(TEXT_SUB),
            size_hint_y=None,
            height=44
        )

        card.add_widget(self.status)

        content.add_widget(card)
        scroll.add_widget(content)
        self.add_widget(scroll)

    # ---------------- UI ELEMENTS ----------------
    def input_field(self, hint):
        return TextInput(
            hint_text=hint,
            font_size=22,
            size_hint_y=None,
            height=68,
            multiline=False,
            padding=(18, 20),
            background_color=get_color_from_hex(INPUT_BG),
            foreground_color=get_color_from_hex(TEXT_MAIN),
            hint_text_color=(0.6, 0.6, 0.6, 1),
            cursor_color=(1, 1, 1, 1)
        )

    def button(self, text, color, action):
        btn = Button(
            text=text,
            font_size=20,
            size_hint_y=None,
            height=66,
            background_normal="",
            background_color=get_color_from_hex(color),
            color=(1, 1, 1, 1)
        )
        btn.bind(on_press=action)
        return btn

    # ---------------- LOGIC ----------------
    def add_data(self, instance):
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO records
                (name, address, phone, received, returned, return_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.name.text,
                self.address.text,
                self.phone.text,
                self.received.text,
                self.returned.text,
                self.return_date.text
            ))
            conn.commit()
            conn.close()
            self.status.text = "Record added successfully"
            self.clear()
        except sqlite3.IntegrityError:
            self.status.text = "Phone number already exists"

    def search_data(self, instance):
        if not self.name.text and not self.phone.text:
            self.status.text = "Enter Name or Phone to search"
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        if self.phone.text:
            cur.execute("SELECT * FROM records WHERE phone = ?", (self.phone.text,))
        else:
            cur.execute("SELECT * FROM records WHERE name LIKE ?", (self.name.text + "%",))

        row = cur.fetchone()
        conn.close()

        if row:
            self.name.text = row[1]
            self.address.text = row[2]
            self.phone.text = row[3]
            self.received.text = row[4]
            self.returned.text = row[5]
            self.return_date.text = row[6]
            self.status.text = "Record loaded"
        else:
            self.status.text = "No record found"

    def update_return(self, instance):
        if not self.phone.text:
            self.status.text = "Search record first"
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            UPDATE records
            SET returned = ?, return_date = ?
            WHERE phone = ?
        """, (self.returned.text, self.return_date.text, self.phone.text))
        conn.commit()
        conn.close()

        self.status.text = "Return details updated"

    def clear(self):
        for f in [
            self.name, self.address, self.phone,
            self.received, self.returned, self.return_date
        ]:
            f.text = ""


# ---------------- APP ----------------
class DigiPayattuApp(App):
    def build(self):
        init_db()
        return MainLayout()


if __name__ == "__main__":
    DigiPayattuApp().run()
