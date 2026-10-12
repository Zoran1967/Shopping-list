"""
Soping Lista - glavni fajl (rekonstruisan na osnovu ostalih fajlova projekta).

Ovaj fajl:
  1. priprema putanje da importi (database, theme, widgets, screens) rade,
  2. pravi bazu (init_db) i ucitava sacuvanu temu,
  3. ucitava .kv fajlove ekrana,
  4. slaze ScreenManager sa ekranima: home, shopping_list, history,
     database, settings.
"""
import os
import sys

# Folder u kome je main.py - da import "from database import db",
# "from theme import ...", "from widgets import ..." rade i na racunaru
# i u APK-u.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition

from database import db
from theme import Theme, DEFAULT_THEME, THEMES

# widgets MORA da se importuje pre ucitavanja .kv fajlova - tu se
# registruju PrimaryButton, SecondaryButton, DangerButton i Card.
import widgets  # noqa: F401

from screens.home_screen import HomeScreen
from screens.shopping_list_screen import ShoppingListScreen
from screens.history_screen import HistoryScreen
from screens.database_screen import DatabaseScreen
from screens.settings_screen import SettingsScreen

KV_FILES = [
    "home_screen.kv",
    "shopping_list_screen.kv",
    "history_screen.kv",
    "database_screen.kv",
    "settings_screen.kv",
]


def _find_kv(name):
    """Trazi .kv fajl u screens/ folderu, pa u korenu projekta."""
    for folder in (os.path.join(BASE_DIR, "screens"), BASE_DIR):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"Nije nadjen kv fajl: {name}")


class SopingListaApp(App):
    title = "Soping Lista"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # kv pravila citaju app.theme.accent, pa tema mora da postoji
        # pre nego sto se napravi ijedan widget.
        self.theme = Theme()

    def build(self):
        db.init_db()

        # Ucitaj sacuvanu temu iz podesavanja
        sacuvana = db.get_setting("tema", DEFAULT_THEME)
        if sacuvana in THEMES:
            self.theme.set_theme(sacuvana)

        for kv in KV_FILES:
            Builder.load_file(_find_kv(kv))

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ShoppingListScreen(name="shopping_list"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(DatabaseScreen(name="database"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.current = "home"
        return sm


if __name__ == "__main__":
    SopingListaApp().run()
