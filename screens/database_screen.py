from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp

from database import db
from widgets import PrimaryButton, SecondaryButton, DangerButton


class DatabaseScreen(Screen):
    """
    Ekran za pregled sacuvanih proizvoda i prodavnica.
    Tab "Proizvodi": svaki red su obicna Button dugmad (najpouzdanije u
    Kivy-ju za klik na malom ekranu) koja otvaraju formu za izmenu
    naziva/cene/jedinice ili trajno brisanje proizvoda iz baze.
    """

    def on_pre_enter(self, *args):
        self.show_proizvodi()

    def show_proizvodi(self):
        box = self.ids.database_box
        box.clear_widgets()
        proizvodi = db.get_proizvodi_sa_prodavnicom()

        header = BoxLayout(size_hint_y=None, height=dp(36))
        header.add_widget(Label(text="Proizvod", bold=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text="Jed.", bold=True, size_hint_x=0.3, color=(1, 1, 1, 1)))
        header.add_widget(Label(text="Cena", bold=True, size_hint_x=0.4, color=(1, 1, 1, 1)))
        box.add_widget(header)

        if not proizvodi:
            box.add_widget(
                Label(text="Nema unetih proizvoda.", size_hint_y=None,
                      height=dp(40), color=(1, 1, 1, 1))
            )
            return

        for pid, naziv, jedinica, cena, prodavnica in proizvodi:
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(2))

            def make_handler(pid=pid, naziv=naziv, jedinica=jedinica, cena=cena):
                def handler(instance):
                    self.open_edit_popup(pid, naziv, jedinica, cena)
                return handler

            handler = make_handler()

            btn_naziv = Button(
                text=naziv, halign="left", valign="middle",
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
            )
            btn_naziv.bind(size=lambda inst, val: setattr(inst, "text_size", val))

            btn_jed = Button(
                text=jedinica, size_hint_x=0.3,
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
            )
            btn_cena = Button(
                text=f"{cena:.2f}", size_hint_x=0.4,
                background_normal="", background_color=(0.16, 0.16, 0.18, 1),
            )

            btn_naziv.bind(on_release=handler)
            btn_jed.bind(on_release=handler)
            btn_cena.bind(on_release=handler)

            row.add_widget(btn_naziv)
            row.add_widget(btn_jed)
            row.add_widget(btn_cena)
            box.add_widget(row)

    def open_edit_popup(self, proizvod_id, naziv, jedinica, cena):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))

        row0 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        naziv_input = TextInput(text=naziv, multiline=False)
        row0.add_widget(Label(text="Naziv:", size_hint_x=0.4))
        row0.add_widget(naziv_input)
        content.add_widget(row0)

        row1 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        jedinica_input = TextInput(text=jedinica, multiline=False)
        row1.add_widget(Label(text="Jedinica:", size_hint_x=0.4))
        row1.add_widget(jedinica_input)
        content.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        cena_input = TextInput(text=f"{cena:.2f}", input_filter="float", multiline=False)
        row2.add_widget(Label(text="Cena:", size_hint_x=0.4))
        row2.add_widget(cena_input)
        content.add_widget(row2)

        error_label = Label(text="", size_hint_y=None, height=dp(24), color=(1, 0.4, 0.4, 1))
        content.add_widget(error_label)

        popup = Popup(title="Izmeni proizvod", content=content, size_hint=(0.9, 0.6))

        def save(*a):
            novi_naziv = naziv_input.text.strip()
            nova_jedinica = jedinica_input.text.strip() or "kom"
            if not novi_naziv:
                error_label.text = "Naziv ne moze biti prazan."
                return
            try:
                nova_cena = float(cena_input.text.replace(",", "."))
            except ValueError:
                error_label.text = "Neispravna cena."
                return
            if nova_cena < 0:
                error_label.text = "Cena ne moze biti negativna."
                return

            uspeh = db.update_proizvod(proizvod_id, novi_naziv, nova_jedinica, nova_cena)
            if not uspeh:
                error_label.text = "Vec postoji proizvod sa tim nazivom."
                return

            popup.dismiss()
            self.show_proizvodi()

        delete_state = {"confirm": False}

        def delete(instance):
            if not delete_state["confirm"]:
                delete_state["confirm"] = True
                instance.text = "Sigurno? Klikni jos jednom za brisanje"
                return
            uspeh = db.delete_proizvod(proizvod_id)
            if not uspeh:
                error_label.text = "Ne moze da se obrise - koriscen je u prethodnim kupovinama."
                delete_state["confirm"] = False
                instance.text = "Obrisi proizvod"
                return
            popup.dismiss()
            self.show_proizvodi()

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        save_btn = PrimaryButton(text="Sacuvaj")
        save_btn.bind(on_release=save)
        cancel_btn = SecondaryButton(text="Otkazi")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        delete_btn = DangerButton(text="Obrisi proizvod", size_hint_y=None, height=dp(44))
        delete_btn.bind(on_release=delete)
        content.add_widget(delete_btn)

        popup.open()

    def show_prodavnice(self):
        box = self.ids.database_box
        box.clear_widgets()
        prodavnice = db.get_prodavnice()

        if not prodavnice:
            box.add_widget(
                Label(
                    text="Nema unetih prodavnica jos.",
                    size_hint_y=None, height=dp(40), color=(1, 1, 1, 1),
                )
            )
            return

        for pid, naziv in prodavnice:
            row = BoxLayout(size_hint_y=None, height=dp(40))
            row.add_widget(Label(text=naziv, color=(1, 1, 1, 1)))
            box.add_widget(row)

    def go_back(self):
        self.manager.current = "home"
