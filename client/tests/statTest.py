#UI Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

#from cloud_manager import Cloud_Manager
#from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
#from filter_manager import Filter_Manager
#from observer import Observer

import os
import asyncio
import logging
from threading import Thread

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Stats_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats_manager = App.get_running_app().stats_manager
        
        # Create the main layout for the screen
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Create a layout to hold the statistics in the center
        self.stats_layout = FloatLayout(size_hint=(.75, .75), height=dp(400), pos_hint={"center_x": 0.5, "center_y": 0.5})  # Set a fixed height for the scrollable area

        # Buttons for toggling each section
        self.blocked_button = Button(text="View Blocked Domains", size_hint_y=None, height=dp(40))
        self.top_visited_button = Button(text="View Top 10 Visited Domains", size_hint_y=None, height=dp(40))
        self.top_blocked_button = Button(text="View Top 10 Blocked Domains", size_hint_y=None, height=dp(40))
        self.data_blocked_button = Button(text="View Data Blocked for Domains", size_hint_y=None, height=dp(40))
        self.dns_data_button = Button(text="View DNS Data", size_hint_y=None, height=dp(40))  # New button for DNS data

        # Create labels to hold the data
        self.blocked_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        self.top_visited_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        self.top_blocked_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        self.data_blocked_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        self.dns_data_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)  # New label for DNS data

        # Initially set all labels to be hidden
        self.blocked_label.text = ""
        self.top_visited_label.text = ""
        self.top_blocked_label.text = ""
        self.data_blocked_label.text = ""
        self.dns_data_label.text = ""  # Set DNS label initially to be empty

        # Add widgets to the layout
        main_layout.add_widget(self.stats_layout)

        # Add buttons at the bottom
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(60), orientation='horizontal')
        buttons_layout.add_widget(self.blocked_button)
        buttons_layout.add_widget(self.top_visited_button)
        buttons_layout.add_widget(self.top_blocked_button)
        buttons_layout.add_widget(self.data_blocked_button)
        buttons_layout.add_widget(self.dns_data_button)  # Add the new DNS data button

        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)

        # Bind buttons to their functions
        self.blocked_button.bind(on_press=self.show_blocked_domains)
        self.top_visited_button.bind(on_press=self.show_top_visited)
        self.top_blocked_button.bind(on_press=self.show_top_blocked)
        self.data_blocked_button.bind(on_press=self.show_data_blocked)
        self.dns_data_button.bind(on_press=self.show_dns_data)  # Bind the DNS data button

        # Call the dns_data function to load the DNS data when the screen is initialized
        self.stats_manager.dns_data()

    def show_blocked_domains(self, instance):
        self.stats_layout.clear_widgets()
        self.blocked_label.text = "[b][u]Blocked Domains for Current Session:[/u][/b]\n"
        blocked_domains_list = self.stats_manager.get_blocked_domains()
        for domain in blocked_domains_list:
            self.blocked_label.text += f"\n{domain['domain']}"
        self.blocked_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.blocked_label)

    def show_top_visited(self, instance):
        self.stats_layout.clear_widgets()
        self.top_visited_label.text = "[b][u]Top 10 Visited Domains:[/u][/b]\n"
        top_visited_list = self.stats_manager.get_top_visited()
        for domain in top_visited_list:
            self.top_visited_label.text += f"\n{domain['domain']} - Traffic: {domain['traffic']}"
        self.top_visited_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.top_visited_label)

    def show_top_blocked(self, instance):
        self.stats_layout.clear_widgets()
        self.top_blocked_label.text = "[b][u]Top 10 Blocked Domains:[/u][/b]\n"
        top_blocked_list = self.stats_manager.get_top_blocked_domains()
        for domain in top_blocked_list:
            self.top_blocked_label.text += f"\n{domain['domain']} - Times Blocked: {domain['denied']}"
        self.top_blocked_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.top_blocked_label)

    def show_data_blocked(self, instance):
        self.stats_layout.clear_widgets()
        self.data_blocked_label.text = "[b][u]Data Blocked for Each Domain:[/u][/b]\n"
        total_data = self.stats_manager.get_total_data()
        for domain in total_data:
            self.data_blocked_label.text += f"\n {domain['domain']} - Total Data Blocked: {domain['total_data']} MB"
        self.data_blocked_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.data_blocked_label)

    def show_dns_data(self, instance):
        self.stats_layout.clear_widgets()
        self.dns_data_label.text = "[b][u]DNS Data - Allowed and Denied Queries:[/u][/b]\n"
        dns_data = self.stats_manager.get_dns_data()
        for domain, data in dns_data.items():
            self.dns_data_label.text += f"\n{domain} - Allowed: {data['allowed']} | Denied: {data['denied']}"
        self.dns_data_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.dns_data_label) 


class Client_App(App):
    '''
    Description: Main client application
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.cloud_manager = Cloud_Manager()
        #self.vpn_manager = VPN_Manager()
        self.stats_manager = Stats_Manager()
        #self.server_monitor = Thread(target=self.cloud_manager.monitor_server, daemon=True)
        #self.server_monitor.start()
        #self.vpn_monitor = Thread(target=self.vpn_manager.monitor_connection, daemon=True)
        #self.vpn_monitor.start()
        return

    def build(self):
        self.root_sm = ScreenManager(transition=NoTransition())
        #login_screen = Login_Screen(name='login')
        main_screen = Stats_Screen(name='main')
     
        # Add root screens
        #self.root_sm.add_widget(login_screen)
        self.root_sm.add_widget(main_screen)

        return self.root_sm
    
    def on_stop(self):
        # disconnect VPN
        #while(self.vpn_manager.disconnect() == 0):
        #    continue
        # delete cloud resources TODO
        pass

if __name__ == '__main__':
    # Run the client app within asyncio
    asyncio.run(Client_App().async_run(async_lib='asyncio'))
