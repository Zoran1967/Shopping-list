from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from widgets import PrimaryButton, SecondaryButton
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db


class ShoppingListScreen(Screen):
    """
    Ekran aktivne liste za kupovinu.
    Izbor prodavnice, dodavanje proizvoda (autopopuna zadnje cene iz baze),
    racunanje totala, cuvanje zatvorene liste u istoriju.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lista_id = None
        self.prodavnica_id = None
        self.stavke_total = 0.0

    def on_pre_enter(self, *args):
        if self.lista_id is None:
            self.open_store_picker()

    def reset_for_new_list(self):
        self.lista_id = None
        self.prodavnica_id = None
        self.stavke_total = 0.0
        self.ids.items_box.clear_widgets()
        self.ids.store_label.text = "Prodavnica: (izbor dolazi)"
        self.ids.total_label.text = "0.00"

    # ---------- Izbor prodavnice ----------

    def open_store_picker(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        search = TextInput(
            hint_text="Pretrazi ili unesi novu prodavnicu",
            size_hint_y=None, height=dp(44), multiline=False,
        )
        content.add_widget(search)

        results_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(results_box)
        content.add_widget(scroll)

        # auto_dismiss=False: bira se prodavnica ili eksplicitno otkazuje,
        # da korisnik ne ostane "zaglavljen" bez liste ako slucajno dodirne van popup-a
        popup = Popup(
            title="Izaberi prodavnicu", content=content,
            size_hint=(0.9, 0.75), auto_dismiss=False,
        )

        def choose_store(pid, naziv):
            self.set_store(pid, naziv)
            popup.dismiss()

        def refresh_results(*a):
            results_box.clear_widgets()
            query = search.text.strip().lower()
            for pid, naziv in db.get_prodavnice():
                if query in naziv.lower():
                    btn = SecondaryButton(text=naziv, size_hint_y=None, height=dp(44))
                    btn.bind(on_release=lambda inst, pid=pid, naziv=naziv: choose_store(pid, naziv))
                    results_box.add_widget(btn)

        def add_new_store(*a):
            naziv = search.text.strip()
            if not naziv:
                return
            pid = db.add_prodavnica(naziv)
            self.set_store(pid, naziv)
            popup.dismiss()

        def cancel(*a):
            popup.dismiss()
            self.go_back()

        search.bind(text=refresh_results)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text="+ Dodaj novu prodavnicu")
        add_btn.bind(on_release=add_new_store)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=cancel)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        refresh_results()
        popup.open()

    def set_store(self, prodavnica_id, naziv):
        self.prodavnica_id = prodavnica_id
        self.ids.store_label.text = f"Prodavnica: {naziv}"
        if self.lista_id is None:
            self.lista_id = db.create_lista(prodavnica_id)

    # ---------- Dodavanje proizvoda ----------

    def add_item(self):
        if self.prodavnica_id is None:
            self.open_store_picker()
            return
        self.open_add_item_popup()

    def open_add_item_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        naziv_input = TextInput(
            hint_text="Naziv proizvoda", size_hint_y=None, height=dp(44), multiline=False,
        )
        content.add_widget(naziv_input)

        suggestions_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        suggestions_box.bind(minimum_height=suggestions_box.setter("height"))
        sugg_scroll = ScrollView(size_hint_y=None, height=dp(140))
        sugg_scroll.add_widget(suggestions_box)
        content.add_widget(sugg_scroll)

        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        jedinica_input = TextInput(hint_text="Jedinica (kg/l/kom)", multiline=False)
        kolicina_input = TextInput(hint_text="Kolicina", input_filter="float", multiline=False)
        cena_input = TextInput(hint_text="Cena po jedinici", input_filter="float", multiline=False)
        row.add_widget(jedinica_input)
        row.add_widget(kolicina_input)
        row.add_widget(cena_input)
        content.add_widget(row)

        total_label = Label(text="Total: 0.00", size_hint_y=None, height=dp(30))
        content.add_widget(total_label)

        def update_total(*a):
            try:
                k = float(kolicina_input.text.replace(",", "."))
                c = float(cena_input.text.replace(",", "."))
                total_label.text = f"Total: {k * c:.2f}"
            except ValueError:
                total_label.text = "Total: 0.00"

        kolicina_input.bind(text=update_total)
        cena_input.bind(text=update_total)

        def pick_suggestion(naziv, jedinica, cena):
            naziv_input.unbind(text=refresh_suggestions)
            naziv_input.text = naziv
            naziv_input.bind(text=refresh_suggestions)
            jedinica_input.text = jedinica
            cena_input.text = f"{cena:.2f}"
            update_total()
            suggestions_box.clear_widgets()

        def refresh_suggestions(*a):
            suggestions_box.clear_widgets()
            query = naziv_input.text.strip().lower()
            if not query:
                return
            for pid, naziv, jedinica, cena in db.search_proizvodi(query):
                btn = SecondaryButton(
                    text=f"{naziv}  ({jedinica}, {cena:.2f})",
                    size_hint_y=None, height=dp(36),
                )
                btn.bind(
                    on_release=lambda inst, n=naziv, j=jedinica, c=cena: pick_suggestion(n, j, c)
                )
                suggestions_box.add_widget(btn)

        naziv_input.bind(text=refresh_suggestions)

        btn_row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        add_btn = PrimaryButton(text="Dodaj u listu")
        cancel_btn = SecondaryButton(text="Otkazi")
        btn_row2.add_widget(add_btn)
        btn_row2.add_widget(cancel_btn)
        content.add_widget(btn_row2)

        popup = Popup(title="Dodaj proizvod", content=content, size_hint=(0.9, 0.85))
        cancel_btn.bind(on_release=popup.dismiss)

        def confirm(*a):
            naziv = naziv_input.text.strip()
            jedinica = jedinica_input.text.strip() or "kom"

            if not naziv:
                return
            try:
                kolicina = float(kolicina_input.text.replace(",", "."))
                cena = float(cena_input.text.replace(",", "."))
            except ValueError:
                return
            if kolicina <= 0 or cena < 0:
                return

            proizvod_id = db.add_or_update_proizvod(naziv, jedinica, cena, self.prodavnica_id)
            total = db.add_stavka(self.lista_id, proizvod_id, naziv, kolicina, cena)

            self.add_item_row(naziv, kolicina, jedinica, cena, total)
            self.stavke_total += total
            self.ids.total_label.text = f"{self.stavke_total:.2f}"

            popup.dismiss()

        add_btn.bind(on_release=confirm)
        popup.open()

    def add_item_row(self, naziv, kolicina, jedinica, cena, total):
        row = BoxLayout(size_hint_y=None, height=dp(48))
        row.add_widget(Label(text=naziv))
        row.add_widget(Label(text=f"{kolicina:g} {jedinica}", size_hint_x=0.4))
        row.add_widget(Label(text=f"{cena:.2f}", size_hint_x=0.5))
        row.add_widget(Label(text=f"{total:.2f}", size_hint_x=0.5))
        self.ids.items_box.add_widget(row)

    # ---------- Zatvaranje liste ----------

    def close_list(self):
        if self.lista_id is None:
            self.go_back()
            return
        db.close_lista(self.lista_id, self.stavke_total)
        self.reset_for_new_list()
        self.manager.current = "home"

    def go_back(self):
        self.manager.current = "home"
