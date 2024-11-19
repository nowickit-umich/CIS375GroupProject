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
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner

def call_async(function):
    # returns a synchronous wrapper function for use with kivy buttons
    def wrapper(x):
        asyncio.create_task(function(x))
    return wrapper

class Login_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        font_size = dp(16)

        # primary elements
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
        login_button = Button(text='Login', size_hint=(1, 0.1), on_press=call_async(self.login))

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
    
    async def login(self, x):
        # DEBUG LOGIN BYPASS
        #self.manager.current = 'main'
        #return

        access = self.input_access.text
        secret = self.input_secret.text
        cloud_name = self.select_cloud.text
        if access == "" or secret == "":
            self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
            return
        
        self.message.color = (1,1,1,1)
        self.message.text = "Validating Credentials..."

        # Update UI
        await asyncio.sleep(0)

        app = App.get_running_app()
        try:
            await app.cloud_manager.setup(cloud_name, [access, secret])
        except Exception as e:
            # TODO error handling
            print(e)
            self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
            return
        
        # DEBUG test credentials
        print("login")
        print(x)
        print(self.input_access.text)
        print(self.select_cloud.text)
        print(self.save_cred.active)

        # Login Success
        app.login = True
        self.message.color = (1,1,1,1)
        self.message.text = "Login Successful!"

        # Save credentials
        if self.save_cred:
            self.save_credentials(cloud_name, access, secret)

        self.manager.current = 'main'
        return
    
    def save_credentials(self, cloud_name, access, secret):
        try:
            file = open("credentials.secret", "w")
        except Exception as e:
            print(e)
            print("Unable to save credentials")
            return
        file.write(cloud_name + '\n')
        file.write(access + '\n')
        file.write(secret + '\n')
        return
        
    def read_credentials(self):
        try:
            file = open("credentials.secret", "r")
        except:
            return
        cloud = file.readline().strip()
        access = file.readline().strip()
        secret = file.readline().strip()
        if not cloud or not access or not secret:
            os.remove("credentials.secret")
            return
        if cloud not in self.cloud_types:
            os.remove("credentials.secret")
            return
        self.input_access.text = access
        self.input_secret.text = secret
        self.save_cred.active = True
        return

class VPN_Screen(Screen):
    def update(self, dt):
        if self.status.text == "DISCONNECTED":
            self.status.text = "CONNECTED"
        else:
            self.status.text = "DISCONNECTED"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # get references to necessary managers
        self.vpn_manager = App.get_running_app().vpn_manager
        self.cloud_manager = App.get_running_app().cloud_manager

        #connection status test
        status1 = AnchorLayout(anchor_y='center', anchor_x='right', height=50)
        self.status = Button(text='DISCONNECTED', size_hint=(None, None))
        status1.add_widget(self.status)
        Clock.schedule_interval(self.update, 2)
        self.add_widget(status1)

        server_status = BoxLayout(orientation="vertical", padding=20, spacing=10)
        # Server Status Display test
        status_label = Label(text=f"Status: sttttt", font_size=20)
        server_status.add_widget(status_label)

        # Server Location Selector
        server_spinner = Spinner(
            text="location",
            values=("US-East", "US-West", "Europe", "Asia"),
            size_hint=(1, None),
            height=44
        )
        server_status.add_widget(server_spinner)

        # Connect/Disconnect Button
        connect_button = Button(text="Connect", size_hint=(1, None), height=50)
        server_status.add_widget(connect_button)
        self.add_widget(server_status)

        # connect/disconnect button
        # label_width = dp(120)
        # main_widget = BoxLayout(orientation="vertical", size_hint=(0.7, 0.7))
        # location_widget = BoxLayout(orientation="horizontal")
        # location_widget.add_widget(Label(text="Sever Location:", size_hint=(None, 1), width=label_width))
        # location_widget.add_widget(Button(text="sel loc"))
        # main_widget.add_widget(location_widget)
        # main_widget.add_widget(Button(text="Connect"))
        # status_widget = BoxLayout(orientation="horizontal")
        # status_widget.add_widget(Label(text="Sever Status:", size_hint=(None, 1), width=label_width))
        # main_widget.add_widget(status_widget)
        # center = AnchorLayout(anchor_x="center", anchor_y="center")
        # center.add_widget(main_widget)
        # self.add_widget(center)

        # bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        # layout = BoxLayout()
        # layout.add_widget(Button(text='Connect', on_press=lambda x:self.vpn_manager.connect()))
        # layout.add_widget(Button(text='Disconnect', on_press=lambda x:self.vpn_manager.disconnect()))
        # bottom_bar.add_widget(layout)
        # self.add_widget(bottom_bar)

    
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

        sm = ScreenManager()
        sm.add_widget(VPN_Screen(name='vpn'))
        sm.add_widget(Filter_Screen(name='filter'))
        sm.add_widget(Stats_Screen(name='stat'))

        # Create a layout for the menu bar
        menu_bar = BoxLayout(size_hint_y=None, height=50)
        menu_bar.add_widget(Button(text='VPN', on_press=lambda x:setattr(sm,'current','vpn')))
        menu_bar.add_widget(Button(text='Filter', on_press=lambda x:setattr(sm,'current','filter')))
        menu_bar.add_widget(Button(text='Statistics', on_press=lambda x:setattr(sm,'current','stat')))

        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(menu_bar)
        main_layout.add_widget(sm)
        
        self.add_widget(main_layout)

class UI_DEMOApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloud_manager = Cloud_Manager()
        self.vpn_manager = VPN_Manager()
        self.filter_manager = None
        self.stats_manager = None
        self.login = False
        return

    def build(self):
        root_sm = ScreenManager()
        # Add screens
        root_sm.add_widget(Login_Screen(name='login'))
        root_sm.add_widget(Main_Screen(name='main'))
        return root_sm

if __name__ == '__main__':
    asyncio.run(UI_DEMOApp().async_run(async_lib='asyncio'))

