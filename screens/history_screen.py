from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton, Card


class HistoryScreen(Screen):
    """
    Istorija kupovina - organizovano po prodavnicama.
    Klik na prodavnicu -> spisak racuna (po datumu) za tu prodavnicu.
    Klik na racun -> stavke (namirnice, kolicine, cene) tog racuna,
    sa mogucnoscu trajnog brisanja tog racuna.
    """

    def on_pre_enter(self, *args):
        self.load_history()

    def load_history(self):
        box = self.ids.history_box
        box.clear_widgets()
        prodavnice = db.get_prodavnice_sa_istorijom()

        if not prodavnice:
            box.add_widget(
                Label(
                    text="Nema jos zatvorenih listi.",
                    size_hint_y=None, height=dp(60), color=(0.7, 0.7, 0.7, 1),
                )
            )
            return

        for pid, naziv, broj_racuna in prodavnice:
            btn = SecondaryButton(
                text=f"{naziv}   ({broj_racuna} racun/a)",
                size_hint_y=None, height=dp(52), font_size="16sp",
            )
            btn.bind(
                on_release=lambda inst, pid=pid, naziv=naziv: self.open_store_history(pid, naziv)
            )
            box.add_widget(btn)

    # ---------- Nivo 1: racuni jedne prodavnice ----------

    def open_store_history(self, prodavnica_id, naziv):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(
            Label(text=naziv, bold=True, font_size="18sp",
                  size_hint_y=None, height=dp(32))
        )

        receipts_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        receipts_box.bind(minimum_height=receipts_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(receipts_box)
        content.add_widget(scroll)

        popup = Popup(title="Racuni", content=content, size_hint=(0.92, 0.8))

        def refresh_receipts():
            receipts_box.clear_widgets()
            liste = db.get_liste_za_prodavnicu(prodavnica_id)
            if not liste:
                # Nema vise racuna za ovu prodavnicu (npr. svi obrisani) - zatvori popup
                popup.dismiss()
                self.load_history()
                return
            for lista_id, datum, ukupno in liste:
                btn = SecondaryButton(
                    text=f"{datum}\nUkupno: {ukupno:.2f} din",
                    size_hint_y=None, height=dp(56), halign="center",
                )
                btn.bind(
                    on_release=lambda inst, lid=lista_id, d=datum, u=ukupno:
                        self.open_receipt_detail(lid, d, u, popup, refresh_receipts)
                )
                receipts_box.add_widget(btn)

        close_btn = SecondaryButton(text="Zatvori", size_hint_y=None, height=dp(48))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        refresh_receipts()
        popup.open()

    # ---------- Nivo 2: stavke jednog racuna ----------

    def open_receipt_detail(self, lista_id, datum, ukupno, parent_popup, refresh_parent):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        content.add_widget(
            Label(text=datum, bold=True, font_size="16sp",
                  size_hint_y=None, height=dp(28))
        )

        header = BoxLayout(size_hint_y=None, height=dp(30))
        header.add_widget(Label(text="Proizvod", bold=True, font_size="13sp"))
        header.add_widget(Label(text="Kol.", bold=True, size_hint_x=0.4, font_size="13sp"))
        header.add_widget(Label(text="Cena/j.", bold=True, size_hint_x=0.5, font_size="13sp"))
        header.add_widget(Label(text="Total", bold=True, size_hint_x=0.5, font_size="13sp"))
        content.add_widget(header)

        items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        items_box.bind(minimum_height=items_box.setter("height"))
        scroll = ScrollView(size_hint_y=1)
        scroll.add_widget(items_box)
        content.add_widget(scroll)

        stavke = db.get_lista_stavke(lista_id)
        for naziv, kolicina, cena, total in stavke:
            row = BoxLayout(size_hint_y=None, height=dp(36))
            row.add_widget(Label(text=naziv, font_size="13sp"))
            row.add_widget(Label(text=f"{kolicina:g}", size_hint_x=0.4, font_size="13sp"))
            row.add_widget(Label(text=f"{cena:.2f}", size_hint_x=0.5, font_size="13sp"))
            row.add_widget(Label(text=f"{total:.2f}", size_hint_x=0.5, font_size="13sp"))
            items_box.add_widget(row)

        total_row = BoxLayout(size_hint_y=None, height=dp(36))
        total_row.add_widget(Label(text="UKUPNO:", bold=True))
        total_row.add_widget(Label(text=f"{ukupno:.2f} din", bold=True))
        content.add_widget(total_row)

        detail_popup = Popup(title="Racun", content=content, size_hint=(0.94, 0.85))

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = "Sigurno? Klikni jos jednom za trajno brisanje"
                return
            db.delete_lista(lista_id)
            detail_popup.dismiss()
            refresh_parent()

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        back_btn = SecondaryButton(text="Nazad")
        back_btn.bind(on_release=detail_popup.dismiss)
        delete_btn = DangerButton(text="Obrisi ovaj racun")
        delete_btn.bind(on_release=delete)
        btn_row.add_widget(back_btn)
        btn_row.add_widget(delete_btn)
        content.add_widget(btn_row)

        detail_popup.open()

    def go_back(self):
        self.manager.current = "home"
