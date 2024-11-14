from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
from filter_manager import Filter_Manager

import asyncio

#UI Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

class loginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Button(text='login', on_press=lambda x:setattr(self.manager, 'current', 'vpn')))

class vpnScreen(Screen):
    async def update(self, dt):
        if self.status.text == "DISCONNECTED":
            self.status.text = "CONNECTED"
        else:
            self.status.text = "DISCONNECTED"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a layout for the menu bar
        menu_bar = AnchorLayout(anchor_y='top', height=50)
        menu_bar.add_widget(BoxLayout(size_hint_y=None, height=50))
        menu_bar.add_widget(Button(text='VPN', on_press=lambda x:setattr(self.sm,'current','vpn')))
        menu_bar.add_widget(Button(text='Filter', on_press=lambda x:setattr(self.sm,'current','filters')))
        menu_bar.add_widget(Button(text='Statistics', on_press=lambda x:setattr(self.sm,'current','stat')))
        self.add_widget(menu_bar)
        #key_file = open("api")
        #api = key_file.readline().split()
        #if(api == []):
            # prompt for API key
            # maybe make a login screen that handles this???
        #    login = Popup()
        # test api key

        # 
        self.vpn_manager = VPN_Manager()

        # init cloud connection
        self.cloud_manager = Cloud_Manager([])

        #connection status test
        status1 = AnchorLayout(anchor_y='center', anchor_x='right', height=50)
        self.status = Button(text='DISCONNECTED', size_hint=(None, None))
        status1.add_widget(self.status)
        Clock.schedule_interval(self.update, 2)
        self.add_widget(status1)

        # location select test
        dropdown = DropDown()
        locations = self.cloud_manager.available_locations()
        for loc in locations:
            btn = Button(text=loc, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        mainbutton = Button(text='Location', size_hint=(None, None))
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        test = AnchorLayout(anchor_y='center', anchor_x='left')
        test.add_widget(mainbutton)
        self.add_widget(test)

        bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        layout = BoxLayout()
        layout.add_widget(Button(text='Connect', on_press=lambda x:self.vpn_manager.connect()))
        layout.add_widget(Button(text='Disconnect', on_press=lambda x:self.vpn_manager.disconnect()))
        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)
        self.add_widget(Label(text='This is the VPN Connection Screen'))

        

class filterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filter_manager = Filter_Manager()
        self.add_widget(Label(text='This is the Filter configuration Screen'))

class statScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stats_manager = Stats_Manager()
        self.add_widget(Label(text='This is the Statistics Screen'))

class UI_DEMOApp(App):

    def __init__(self):
        super().__init__()
        # not sure if this works
        self.sm = ScreenManager()
        return

    def build(self):
        # Add screens
        self.sm.add_widget(loginScreen(name='login'))
        self.sm.add_widget(vpnScreen(name='vpn'))
        self.sm.add_widget(filterScreen(name='filters'))
        self.sm.add_widget(statScreen(name='stat'))

        

        # Create the main layout
        main_layout = BoxLayout(orientation='vertical')
        #main_layout.add_widget(menu_bar)
        main_layout.add_widget(self.sm)

        return main_layout

if __name__ == '__main__':
    UI_DEMOApp().run()

