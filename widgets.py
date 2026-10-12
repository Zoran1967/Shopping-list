"""
Zajednicki stilizovani widget-i za "profi" izgled aplikacije.
Boja se automatski uzima iz app.theme.accent (vidi theme.py), pa se sve
dugmice u aplikaciji menjaju odjednom kad korisnik promeni temu u
Podesavanjima.
"""
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

Builder.load_string("""
#:import dp kivy.metrics.dp
<PrimaryButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    bold: True
    canvas.before:
        Color:
            rgba: app.theme.accent if self.state == "normal" else (app.theme.accent[0]*0.7, app.theme.accent[1]*0.7, app.theme.accent[2]*0.7, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

<SecondaryButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: (0.28, 0.28, 0.30, 1) if self.state == "normal" else (0.38, 0.38, 0.40, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

<DangerButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: (0.75, 0.20, 0.20, 1) if self.state == "normal" else (0.55, 0.15, 0.15, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

<Card>:
    canvas.before:
        Color:
            rgba: (0.16, 0.16, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
""")


class PrimaryButton(Button):
    """Glavno dugme - akcentna boja teme."""
    pass


class SecondaryButton(Button):
    """Sporedno dugme - neutralno sivo."""
    pass


class DangerButton(Button):
    """Dugme za brisanje/opasne akcije - crveno."""
    pass


class Card(BoxLayout):
    """Kartica sa zaobljenom pozadinom, za redove liste."""
    pass
