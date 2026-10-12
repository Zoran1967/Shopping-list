"""
Tema boja aplikacije. Theme je EventDispatcher pa kv fajlovi koji citaju
app.theme.accent automatski dobiju novu boju kad se tema promeni - bez
potrebe da se app restartuje.
"""
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

# naziv teme -> (r, g, b, a) akcentna boja, i tamnija varijanta za pozadinu
THEMES = {
    "Plava": (0.16, 0.50, 0.85, 1),
    "Zelena": (0.20, 0.62, 0.35, 1),
    "Ljubicasta": (0.52, 0.30, 0.78, 1),
    "Narandzasta": (0.90, 0.45, 0.15, 1),
    "Crvena": (0.80, 0.22, 0.22, 1),
    "Tirkizna": (0.10, 0.60, 0.60, 1),
}

DEFAULT_THEME = "Plava"


class Theme(EventDispatcher):
    accent = ListProperty(THEMES[DEFAULT_THEME])
    name = StringProperty(DEFAULT_THEME)

    def set_theme(self, naziv):
        if naziv in THEMES:
            self.name = naziv
            self.accent = THEMES[naziv]

    def darker(self, factor=0.65):
        r, g, b, a = self.accent
        return (r * factor, g * factor, b * factor, a)
