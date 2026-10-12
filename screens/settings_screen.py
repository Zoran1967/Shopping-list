from kivy.uix.screenmanager import Screen
from kivy.app import App

from theme import THEMES
from database import db


class SettingsScreen(Screen):
    """Podesavanja - trenutno samo izbor teme boje aplikacije."""

    def on_pre_enter(self, *args):
        self.build_theme_buttons()

    def build_theme_buttons(self):
        box = self.ids.theme_box
        box.clear_widgets()
        from widgets import PrimaryButton, SecondaryButton
        from kivy.metrics import dp

        app = App.get_running_app()
        for naziv in THEMES:
            is_current = naziv == app.theme.name
            btn_cls = PrimaryButton if is_current else SecondaryButton
            btn = btn_cls(
                text=(f"{naziv}  (aktivna)" if is_current else naziv),
                size_hint_y=None, height=dp(48),
            )
            btn.bind(on_release=lambda inst, n=naziv: self.choose_theme(n))
            box.add_widget(btn)

    def choose_theme(self, naziv):
        app = App.get_running_app()
        app.theme.set_theme(naziv)
        db.set_setting("tema", naziv)
        self.build_theme_buttons()

    def go_back(self):
        self.manager.current = "home"
