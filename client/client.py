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

class vpnScreen(Screen):
    def __init__(self, vpn_manager, **kwargs):
        super().__init__(**kwargs)

        bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        layout = BoxLayout()
        layout.add_widget(Button(text='Connect', on_press=lambda x:asyncio.run(vpn_manager.connect())))
        layout.add_widget(Button(text='Disconnect', on_press=lambda x:vpn_manager.disconnect()))
        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)
        self.add_widget(Label(text='This is the VPN Connection Screen'))

class filterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='This is the Filter configuration Screen'))

class statScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='This is the Statistics Screen'))

class serverScreen(Screen):
    def __init__(self, cloud_manager, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='This is the Server Management Screen'))

        bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        layout = BoxLayout()
        layout.add_widget(Button(text='Start Server', on_press=lambda x:cloud_manager.start_server()))
        layout.add_widget(Button(text='Stop Server', on_press=lambda x:cloud_manager.stop_server()))
        layout.add_widget(Button(text='Create Server', on_press=lambda x:cloud_manager.create_server()))
        layout.add_widget(Button(text='Delete Server', on_press=lambda x:cloud_manager.delete_server()))
        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)

class UI_DEMOApp(App):


    def build(self):
        sm = ScreenManager()

        # Managers
        vpn_manager = VPN_Manager()
        cloud_manager = Cloud_Manager()
        filter_manager = Filter_Manager()
        stats_manager = Stats_Manager()

        # Add screens
        sm.add_widget(vpnScreen(vpn_manager, name='vpn'))
        sm.add_widget(filterScreen(name='filters'))
        sm.add_widget(statScreen(name='stat'))
        sm.add_widget(serverScreen(cloud_manager, name='server'))

        # Create a layout for the menu bar
        menu_bar = BoxLayout(size_hint_y=None, height=50)
        menu_bar.add_widget(Button(text='VPN', on_press=lambda x:setattr(sm,'current','vpn')))
        menu_bar.add_widget(Button(text='Filter', on_press=lambda x:setattr(sm,'current','filters')))
        menu_bar.add_widget(Button(text='Statistics', on_press=lambda x:setattr(sm,'current','stat')))
        menu_bar.add_widget(Button(text='Server', on_press=lambda x:setattr(sm,'current','server')))

        # Create the main layout
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(menu_bar)
        main_layout.add_widget(sm)

        return main_layout

if __name__ == '__main__':
    UI_DEMOApp().run()

