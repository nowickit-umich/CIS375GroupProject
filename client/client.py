from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
from filter_manager import Filter_Manager

import os
import asyncio

#UI Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner

from kivy.logger import Logger
Logger.setLevel('DEBUG')

class Login_Screen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        font_size = dp(16)

        # Define UI 
        self.cloud_types = ["AWS", "Google Cloud", "Azure"]
        self.input_access = TextInput(
            multiline=False, 
            padding=(font_size/2, font_size/2, font_size/2, 0), 
            write_tab=False, 
            font_size=font_size, 
            size_hint_y=None, 
            height=font_size + dp(20)
        )
        self.input_secret = TextInput(
            multiline=False, 
            padding=(font_size/2, font_size/2, font_size/2, 0), 
            write_tab=False, 
            font_size=font_size, 
            size_hint_y=None, 
            height=font_size + dp(20),
            password=True
        )
        self.message = Label(text="", size_hint=(1, 0.1))
        self.save_cred = CheckBox(size_hint=(None, None), size=(dp(20), dp(20)))
        login_button = Button(text='Login', size_hint=(1, 0.1), on_press=self.login)

        # Cloud selection drop down menu
        self.select_cloud = Spinner(
            text=self.cloud_types[0],
            values=self.cloud_types,
            size_hint=(1, None),
            height=dp(30)
        )

        label_width = dp(120)

        # Credential entry layout
        login_entry = GridLayout(cols=2, rows=4, spacing=10, size_hint=(0.9,0.8))
        login_entry.add_widget(Label(
                text="Cloud Platform:", size_hint=(None,None), height=dp(30),
                width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.select_cloud)
        login_entry.add_widget(Label(
            text="Access Token:", size_hint=(None,None), height=font_size + dp(20),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.input_access)
        login_entry.add_widget(Label(
            text="Secret Token:", size_hint=(None,None), height=font_size + dp(20),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.input_secret)
        login_entry.add_widget(Label(
            text="Save Credentials:", size_hint=(None,None), height=dp(20),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.save_cred)

        # Login box layout
        login_box = BoxLayout(orientation="vertical", size_hint=(1, 0.2), spacing=5)
        login_box.add_widget(self.message)
        login_box.add_widget(login_button)

        # Anchor widgets into place
        center = AnchorLayout(anchor_x="center", anchor_y="center")
        center.add_widget(login_entry)
        self.add_widget(center)
        bottom = AnchorLayout(anchor_x="center", anchor_y="bottom")
        bottom.add_widget(login_box)
        self.add_widget(bottom)

        # Check for saved credentials
        self.read_credentials()    
    
    def login(self, x):
        access = self.input_access.text
        secret = self.input_secret.text
        cloud_name = self.select_cloud.text
        if access == "" or secret == "":
            self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
            return
        credentials = [cloud_name, access, secret]
        
        # Check credentials
        self.message.color = (1,1,1,1)
        self.message.text = "Validating Credentials..."
        asyncio.create_task(self._check_credentials(credentials))
        return
    
    async def _check_credentials(self, credentials):
        app = App.get_running_app()
        is_valid = False
        try:
            await asyncio.to_thread(app.cloud_manager.setup, credentials) 
            is_valid = True
        except ValueError as e:
            pass
        except Exception as e:
            # TODO error handling            
            is_valid = False
        # update status
        Clock.schedule_once(lambda x: self.update_status(is_valid, credentials))
        return
        
    def update_status(self, is_valid, credentials):
        if is_valid:
            # Login Success
            self.message.color = (1,1,1,1)
            self.message.text = "Login Successful!"

            # Save credentials
            if self.save_cred:
                self.save_credentials(credentials)
            # Switch to main screen
            self.manager.current = 'main'
        else:
            self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
    
    def save_credentials(self, credentials):
        try:
            file = open("data/credentials.secret", "w")
        except Exception as e:
            print(e)
            print("Unable to save credentials")
            return
        file.write(credentials[0] + '\n')
        file.write(credentials[1] + '\n')
        file.write(credentials[2] + '\n')
        return
    
    def read_credentials(self):
        try:
            file = open("data/credentials.secret", "r")
        except:
            return
        cloud = file.readline().strip()
        access = file.readline().strip()
        secret = file.readline().strip()
        if not cloud or not access or not secret:
            os.remove("data/credentials.secret")
            return
        if cloud not in self.cloud_types:
            os.remove("data/credentials.secret")
            return
        self.input_access.text = access
        self.input_secret.text = secret
        self.save_cred.active = True
        return

class VPN_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # get references to necessary managers
        self.vpn_manager = App.get_running_app().vpn_manager
        self.cloud_manager = App.get_running_app().cloud_manager

        # Server Status Display test
        server_status = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.status_label = Label(text=f"Status: {self.cloud_manager.server_status}", font_size=20)
        server_status.add_widget(self.status_label)

        # Server Location Selector
        self.server_location_selector = Spinner(
            text=self.cloud_manager.locations[0],
            values=self.cloud_manager.locations,
            disabled=False,
            size_hint=(1, None),
            height=44
        )
        self.server_location_selector.bind(text=self.on_location_select)
        server_status.add_widget(self.server_location_selector)

        # Connect/Disconnect Button
        self.connect_button = Button(text="Initializing...", size_hint=(1, None), height=50)
        server_status.add_widget(self.connect_button)
        self.add_widget(server_status)
        return
    
    def on_location_select(self, instance, text=None):
        self.cloud_manager.server_location = self.server_location_selector.text

    # reads status to UI
    def update(self, dt):
        #TODO I think there is a better way to do this
        if self.cloud_manager.is_ready and not self.cloud_manager.is_monitored:
            asyncio.create_task(self.cloud_manager.monitor_server())

        # Update status
        self.status_label.text = f"Status: {self.cloud_manager.server_status}"
        # Update button text
        if self.cloud_manager.server_status == "Offline":
            self.connect_button.text = "Start Server"
            self.connect_button.on_press = lambda: asyncio.create_task(self.on_create_server())
        elif self.cloud_manager.server_status == "ok":
            if self.vpn_manager.is_connected:
                self.connect_button.text = "Disconnect VPN"
                self.connect_button.on_press = self.vpn_manager.disconnect
            else:
                self.connect_button.text = "Connect VPN"
                self.connect_button.on_press = self.vpn_manager.connect
        return
    
    async def on_create_server(self):
        try:
            await asyncio.to_thread(self.cloud_manager.create_server)
        except Exception as e:
            Logger.error("Create server error:", e)        

    def on_pre_enter(self, *args):
        # Update location selector
        self.server_location_selector.text = self.cloud_manager.locations[0]
        self.server_location_selector.values = self.cloud_manager.locations
        # Add update loop
        self.event_loop = Clock.schedule_interval(self.update, 1)
        # start monitoring status of vpn and cloud
           
    def on_leave(self, *args):
        Clock.unschedule(self.event_loop)
        self.cloud_manager.is_ready = False
        return
    
class Filter_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Label(text='This is the Filter configuration Screen'))

class Stats_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Label(text='This is the Statistics Screen'))

class Main_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create Screens
        self.sm = ScreenManager()
        self.vpn_screen = VPN_Screen(name='vpn')
        self.filter_screen = Filter_Screen(name='filter')
        self.stats_screen = Stats_Screen(name='stat')

        # Add screens to screen manager
        self.sm.add_widget(self.stats_screen)
        self.sm.add_widget(self.vpn_screen)
        self.sm.add_widget(self.filter_screen)

        # Create a layout for the menu bar
        menu_bar = BoxLayout(size_hint_y=None, height=50)
        menu_bar.add_widget(Button(text='VPN', on_press=lambda x:setattr(self.sm,'current','vpn')))
        menu_bar.add_widget(Button(text='Filter', on_press=lambda x:setattr(self.sm,'current','filter')))
        menu_bar.add_widget(Button(text='Statistics', on_press=lambda x:setattr(self.sm,'current','stat')))

        # Attach menu bar above screen manager
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(menu_bar)
        main_layout.add_widget(self.sm)
        
        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        # Trigger on_enter update for vpn screen when main screen is activaated
        self.sm.current = 'vpn'

class Client_App(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloud_manager = Cloud_Manager()
        self.vpn_manager = VPN_Manager()
        self.filter_manager = None
        self.stats_manager = None
        return

    def build(self):
        root_sm = ScreenManager(transition=NoTransition())
        login_screen = Login_Screen(name='login')
        main_screen = Main_Screen(name='main')
        # Add root screens
        root_sm.add_widget(login_screen)
        root_sm.add_widget(main_screen)
        return root_sm


if __name__ == '__main__':
    asyncio.run(Client_App().async_run(async_lib='asyncio'))

