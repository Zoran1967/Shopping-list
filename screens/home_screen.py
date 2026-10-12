from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    """
    Početni ekran: dugmad za Novu listu, Istoriju, Bazu proizvoda/prodavnica
    i Podešavanja.
    """

    def go_to_new_list(self):
        self.manager.get_screen("shopping_list").reset_for_new_list()
        self.manager.current = "shopping_list"

    def go_to_history(self):
        self.manager.current = "history"

    def go_to_database(self):
        self.manager.current = "database"

    def go_to_settings(self):
        self.manager.current = "settings"
