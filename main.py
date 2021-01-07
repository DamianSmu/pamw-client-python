import requests
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import Screen
from kivymd.uix.textfield import MDTextField
from functools import partial
import jwt
from dotenv import load_dotenv
import os

URL = "https://pamw-damian-smugorzewski-api.herokuapp.com/"
#URL = "http://localhost:8080/"

ACCESSTOKEN = ""


class App(MDApp):
    def __init__(self, **kw):
        super(App, self).__init__(**kw)
        self.title = "Aplikacja kuriera"
        self.screen_manager = ScreenManager()
        self.parcel_screen = ParcelScreen(name="Parcels")
        self.login_screen = LoginScreen(name="Login")

    def build(self):
        self.screen_manager.add_widget(self.login_screen)
        self.screen_manager.add_widget(self.parcel_screen)
        return self.screen_manager

    def change_screen(self, screen_name):
        self.screen_manager.current = screen_name


class LoginScreen(Screen):
    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)

        label_title = MDLabel(text="Aplikacja kuriera",
                              font_style='H4',
                              pos_hint={'center_x': 0.5, 'center_y': 0.8},
                              size_hint_x=None, size=("300dp", "90dp"),
                              halign="center")
        label_login = MDLabel(text="Zaloguj się",
                              font_style='H5',
                              pos_hint={'center_x': 0.5, 'center_y': 0.7},
                              size_hint_x=None, size=("200dp", "90dp"),
                              halign="center")
        self.username_text_field = MDTextField(
            helper_text_mode="on_focus",
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            size_hint_x=None,
            width=300)
        button = MDRectangleFlatButton(text='Zaloguj',
                                       pos_hint={'center_x': 0.5, 'center_y': 0.35},
                                       on_release=self.button_clicked)
        button_auth = MDRectangleFlatButton(text='Zaloguj (Auth0.com)',
                                            pos_hint={'center_x': 0.5, 'center_y': 0.25},
                                            on_release=self.button_auth_clicked)
        self.username_text_field.hint_text = "Nazwa użytkownika"
        self.username_text_field.helper_text = "Wpisz nazwę użytkownika (tylko kurier)"
        self.password_text_field = MDTextField(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                               password=True,
                                               size_hint_x=None,
                                               width=300)
        self.password_text_field.hint_text = "Hasło"
        self.failure_message = MDLabel(text="Niepoprawna nazwa użytkownika lub hasło",
                                       halign="center",
                                       theme_text_color="Error",
                                       pos_hint={'center_x': 0.5, 'center_y': 0.2}, )
        self.add_widget(label_title)
        self.add_widget(label_login)
        self.add_widget(self.username_text_field)
        self.add_widget(self.password_text_field)
        self.add_widget(button)
        self.add_widget(button_auth)

    def button_clicked(self, obj):
        username = self.username_text_field.text
        password = self.password_text_field.text
        try:
            response = requests.post(URL + "api/auth/signin",
                                     json={'username': username, 'password': password},
                                     headers={"Content-type": "application/json"})
            if not response:
                self.failure_message.text = "Niepoprawna nazwa użytkownika lub hasło"
                self.remove_widget(self.failure_message)
                self.add_widget(self.failure_message)
            if response:
                self.remove_widget(self.failure_message)
                if "COURIER" in response.json()['roles']:
                    global ACCESSTOKEN
                    ACCESSTOKEN = "MyBearer " + response.json()['accessToken']
                    MDApp.get_running_app().change_screen("Parcels")
                else:
                    self.failure_message.text = "Użytkownik nie jest kurierem."
                    self.remove_widget(self.failure_message)
                    self.add_widget(self.failure_message)
        except:
            self.failure_message.text = "Brak połączenia z serwerem."
            self.remove_widget(self.failure_message)
            self.add_widget(self.failure_message)

    def button_auth_clicked(self, obj):
        username = self.username_text_field.text
        password = self.password_text_field.text
        SECRET_KEY = os.getenv("SECRET_KEY")
        load_dotenv()
        payload = {"client_id": "Lm7u6t7L1ocqf7MBX30GDaBKinqWw55S",
                   "client_secret": SECRET_KEY,
                   "audience": "https://pamw-damian-smugorzewski-api.herokuapp.com",
                   "grant_type": "password",
                   "username": username,
                   "password": password,
                   "scope": "openid app_metadata"}

        response = requests.post("https://dev-5ieroany.eu.auth0.com/oauth/token",
                                 json=payload,
                                 headers={"Content-type": "application/json"})

        if not response:
            self.failure_message.text = "Niepoprawna nazwa użytkownika lub hasło"
            self.remove_widget(self.failure_message)
            self.add_widget(self.failure_message)
        if response:
            self.remove_widget(self.failure_message)
            if "kurier" == jwt.decode(response.json()['id_token'], options={"verify_signature": False})['nickname']:
                global ACCESSTOKEN
                ACCESSTOKEN = "Bearer " + response.json()['access_token']
                MDApp.get_running_app().change_screen("Parcels")
            else:
                self.failure_message.text = "Użytkownik nie jest kurierem."
                self.remove_widget(self.failure_message)
                self.add_widget(self.failure_message)


class ParcelScreen(Screen):
    def __init__(self, **kw):
        super(ParcelScreen, self).__init__(**kw)
        self.box_layout = BoxLayout(orientation='vertical',
                                    spacing=10,
                                    padding=10,
                                    size_hint_y=None)
        self.box_layout.bind(minimum_height=self.box_layout.setter('height'))
        self.scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scrollview.bar_width = 5
        self.scrollview.add_widget(self.box_layout)
        self.add_widget(self.scrollview)

    def button_clicked(self, obj, uri, status, label):
        txt = requests.patch(uri,
                             headers=auth_header(),
                             json={'status': status}).json()
        label.text = "Status: " + self.status_for_name(status)

    def on_pre_enter(self):
        txt = requests.get(URL + "api/parcel/",
                           headers=auth_header()).json()

        title = MDLabel(text="Wszystkie przesyłki:",
                        font_style="H4",
                        pos_hint={"center_x": .5, "center_y": .5},
                        size_hint=(None, None),
                        size=("400dp", "90dp"))
        self.box_layout.add_widget(title)
        for parcel in txt['_embedded']['parcelList']:
            card = MDCard(orientation="vertical",
                          padding="8dp",
                          size_hint=(None, None),
                          size=("400dp", "180dp"),
                          pos_hint={"center_x": .5, "center_y": .5})
            label_id = MDLabel(text="Id: " + str(parcel['id']))
            label_reciever = MDLabel(text="Odbiorca: " + str(parcel['receiver']), font_style='Caption')
            label_postoffice = MDLabel(text="Skrytka pocztowa: " + str(parcel['postOffice']), font_style='Caption')
            label_size = MDLabel(text="Rozmiar: " + str(parcel['size']), font_style='Caption')
            label_status = MDLabel(text="Status: " + self.status_for_name(str(parcel['status'])), font_style='Caption')
            card.add_widget(label_id)
            card.add_widget(MDSeparator())
            card.add_widget(label_reciever)
            card.add_widget(label_postoffice)
            card.add_widget(label_size)
            card.add_widget(label_status)
            card.add_widget(MDSeparator())
            box_layout = MDBoxLayout(adaptive_height=True, padding=5, spacing=5)
            wd_button = MDRectangleFlatButton(text='W drodze', size_hint=(.333, None),
                                              on_release=partial(self.button_clicked,
                                                                 uri=str(parcel["_links"]["self"]["href"]),
                                                                 status="IN_TRANSPORT", label=label_status))
            d_button = MDRectangleFlatButton(text='Dostarczono', size_hint=(.333, None),
                                             on_release=partial(self.button_clicked,
                                                                uri=str(parcel["_links"]["self"]["href"]),
                                                                status="DELIVERED", label=label_status))
            o_button = MDRectangleFlatButton(text='Odebrano', size_hint=(.333, None),
                                             on_release=partial(self.button_clicked,
                                                                uri=str(parcel["_links"]["self"]["href"]),
                                                                status="PICKED_UP", label=label_status))
            box_layout.add_widget(wd_button)
            box_layout.add_widget(d_button)
            box_layout.add_widget(o_button)
            card.add_widget(box_layout)
            self.box_layout.add_widget(card)

    def status_for_name(self, status):
        return {
            'IN_TRANSPORT': "W drodze",
            'DELIVERED': "Dostarczona",
            'PICKED_UP': "Odebrana",
            'CREATED': "Utworzona"
        }[status]


def auth_header():
    return {"Content-type": "application/json",
            "Authorization": ACCESSTOKEN}


if __name__ == '__main__':
    App().run()
