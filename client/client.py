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

from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
from filter_manager import Filter_Manager

import os
import asyncio
import logging
from threading import Thread

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    
    def login(self, b):
        '''
        Description: Function called from the login button. Performs basic input validation,
        updates the login screen message, and then passes the input to the 
        _check_credentials function to asyncronously validate.

        param b: instance of the button
        return: None
        '''
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
        '''
        Description: Async function which calls the cloud_manager setup function to validate 
        the given credentials. Calls update_status with the result of the credential validation.

        param credentials: list containing [cloud_name, access_key, secret_key]
        return: None 
        '''
        app = App.get_running_app()
        is_valid = False
        try:
            logger.debug("Checking Credentials")
            is_valid = await asyncio.to_thread(app.cloud_manager.setup, credentials) 
        except Exception as e:
            # TODO error handling            
            is_valid = False
            logger.error(f"Error checking credentials: {e}")
        # schedule update status to execute
        Clock.schedule_once(lambda x: self.update_status(is_valid, credentials))
        return
        
    def update_status(self, is_valid, credentials):
        '''
        Description: Updates the login screen message with the result of the login attempt. Switches to the
        main screen if the login was successful.

        param is_valid: boolean value. True if the credentials were valid.
        param credentials: list containing [cloud_name, access_key, secret_key]
        return: None
        '''
        if is_valid:
            # Login Success
            self.message.color = (1,1,1,1)
            self.message.text = "Login Successful!"

            # Save credentials
            if self.save_cred:
                self.save_credentials(credentials)
            # Switch to main screen
            logger.info("Login Successful")
            self.manager.current = 'main'
        else:
            self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
            logger.info("Login Failed")
    
    def save_credentials(self, credentials):
        '''
        Description: Saves the given credentials to the credential file.

        param credentials: list containing [cloud_name, access_key, secret_key]
        return: None
        '''
        try:
            file = open("data/credentials.secret", "w")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return
        file.write(credentials[0] + '\n')
        file.write(credentials[1] + '\n')
        file.write(credentials[2] + '\n')
        logger.info("Credentials Saved Successfully")
        return
    
    def read_credentials(self):
        '''
        Description: Reads credentials from the credential file.

        return: None
        '''
        try:
            file = open("data/credentials.secret", "r")
        except Exception as e:
            logger.error(f"Error reading credentials: {e}")
            return
        cloud = file.readline().strip()
        access = file.readline().strip()
        secret = file.readline().strip()
        if (not cloud) or (not access) or (not secret) or (cloud not in self.cloud_types):
            os.remove("data/credentials.secret")
            logger.debug("Removing invalid credential file")
            return
        self.input_access.text = access
        self.input_secret.text = secret
        self.save_cred.active = True
        logger.info("Successfully read credentials from file")
        return

class Status_Widget(GridLayout):
    '''
    Description: 
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols=2
        self.rows=5
        self.spacing=10
        label_width = dp(120)
        label_height = dp(30)
        self.server_status = Label(text="Offline", size_hint=(None,None), height=label_height)
        self.server_ip = Label(text="", size_hint=(None,None), height=label_height)
        self.server_latency = Label(text="", size_hint=(None,None), height=label_height)
        self.vpn_status = Label(text="Disconnected", size_hint=(None,None), height=label_height)
        self.vpn_speed = Label(text="", size_hint=(None,None), height=label_height)

        self.add_widget(Label(text="Server Status:", size_hint=(None,None), height=label_height,
                width=label_width, halign="right", valign='middle', text_size=(label_width, None)))
        self.add_widget(self.server_status)
        self.add_widget(Label(text="Server IP:", size_hint=(None,None), height=label_height,
                width=label_width, halign="right", valign='middle', text_size=(label_width, None)))
        self.add_widget(self.server_ip)
        self.add_widget(Label(text="Latency:", size_hint=(None,None), height=label_height,
                width=label_width, halign="right", valign='middle', text_size=(label_width, None)))
        self.add_widget(self.server_latency)
        self.add_widget(Label(text="VPN Status:", size_hint=(None,None), height=label_height,
                width=label_width, halign="right", valign='middle', text_size=(label_width, None)))
        self.add_widget(self.vpn_status)
        self.add_widget(Label(text="VPN Speed:", size_hint=(None,None), height=label_height,
                width=label_width, halign="right", valign='middle', text_size=(label_width, None)))
        self.add_widget(self.vpn_speed)

class VPN_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # get references to necessary managers
        self.vpn_manager = App.get_running_app().vpn_manager
        self.cloud_manager = App.get_running_app().cloud_manager

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Server Status Display
        self.status = Status_Widget()
        layout.add_widget(self.status)

        # Server Location Selector
        self.server_location_selector = Spinner(
            text=self.cloud_manager.locations[0],
            values=self.cloud_manager.locations,
            disabled=False,
            size_hint=(1, None),
            height=44
        )
        self.server_location_selector.bind(text=self.on_location_select)
        layout.add_widget(self.server_location_selector)

        # Connect/Disconnect Button
        self.connect_button = Button(text="Initializing...", size_hint=(1, None), height=50)
        layout.add_widget(self.connect_button)
        self.add_widget(layout)
        return

    def on_location_select(self, instance, text=None):
        self.cloud_manager.server_location = self.server_location_selector.text

    # reads status to UI
    def update(self, dt=0):
        # Update status
        prev_status = self.status.server_status.text
        self.status.server_status.text = self.cloud_manager.server_status
        if self.cloud_manager.server_ip != None:
            self.status.server_ip.text = self.cloud_manager.server_ip
        if self.vpn_manager.is_connected:
            self.status.vpn_status.text = "Connected"
        else:
            self.status.vpn_status.text = "Disconnected"

        # Update button text
        if self.cloud_manager.server_status == "Offline":
            logger.debug("VPN Screen Update: Offline")
            App.get_running_app().root_sm.get_screen('main').filter_button.disabled = True
            App.get_running_app().root_sm.get_screen('main').stats_button.disabled = True
            self.connect_button.text = "Start Server"
            self.connect_button.background_color = (0,0,1)
            self.connect_button.on_press = lambda: asyncio.create_task(self.on_create_server())
        elif self.cloud_manager.server_status == 'Starting...':
            logger.debug("VPN Screen Update: Starting")
            self.connect_button.disabled = True
        elif self.cloud_manager.server_status == "Running":
            if(prev_status != self.status.server_status.text):
                self.connect_button.disabled = False
            if self.vpn_manager.is_connected:
                logger.debug("VPN Screen Update: Connected")
                self.connect_button.text = "Disconnect VPN"
                self.connect_button.on_press = lambda: asyncio.create_task(self.on_disconnect())
                App.get_running_app().root_sm.get_screen('main').filter_button.disabled = False
                App.get_running_app().root_sm.get_screen('main').stats_button.disabled = False
            else:
                logger.debug("VPN Screen Update: Disconnected")
                self.connect_button.text = "Connect VPN"
                self.connect_button.on_press = lambda: asyncio.create_task(self.on_connect())
                App.get_running_app().root_sm.get_screen('main').filter_button.disabled = True
                App.get_running_app().root_sm.get_screen('main').stats_button.disabled = True
        return
    
    async def on_connect(self):
        Clock.schedule_once(lambda x: setattr(self.connect_button, 'disabled', True))
        try:
            await asyncio.to_thread(self.vpn_manager.connect, self.cloud_manager.server_ip)
        except Exception as e:
            logger.error(f"VPN Connect error: {str(e)}")
        Clock.schedule_once(lambda x:setattr(self.status.vpn_status, 'text', "Connected"))
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'text', "Disconnect VPN"))
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'background_color', (0,1,0)))
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'disabled', False))
    
    async def on_disconnect(self):
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'disabled', True))
        try:
            await asyncio.to_thread(self.vpn_manager.disconnect)
        except Exception as e:
            logger.error(f"VPN Disconnect error: {str(e)}")
        Clock.schedule_once(lambda x:setattr(self.status.vpn_status, 'text', "Disconnected"))
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'text', "Connect VPN"))
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'background_color', (1,0,0)))
        Clock.schedule_once(lambda x: setattr(self.connect_button, 'disabled', False))

    async def on_create_server(self):
        Clock.schedule_once(lambda x: setattr(self.cloud_manager, 'server_status', "Starting"))
        Clock.schedule_once(lambda x: setattr(self.connect_button, 'disabled', True))
        Clock.schedule_once(lambda x: setattr(self.server_location_selector, 'disabled', True))
        try:
            await asyncio.to_thread(self.cloud_manager.create_server)
        except Exception as e:
            logger.error(f"Create server error: {str(e)}")

    def on_pre_enter(self, *args):
        # Update location selector
        if(self.server_location_selector.text == "None"):
            self.server_location_selector.text = self.cloud_manager.locations[0]
            self.server_location_selector.values = self.cloud_manager.locations
        # Add update loop
        self.update()
        self.update_loop = Clock.schedule_interval(self.update, 1)

    def on_leave(self, *args):
        Clock.unschedule(self.update_loop)
        return
    
class Filter_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()
        #self.add_widget(CheckBox(color = (0,0,0), size_hint=(None, None), size=(dp(20), dp(20))))

        #read from a file to create a few filters and checkboxes

        # get list of file from server, file contain list of names

        background_image = Image(source="images/Earth2.png", allow_stretch=True, keep_ratio=False,
                                 size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        layout.add_widget(background_image)

        # read text names from file

        filter_layout = BoxLayout(orientation = "vertical", size_hint = (.8, .8), pos_hint = {"x":.01, "y":.5}, spacing = 10)

        self.addfilter(filter_layout)

        layout.add_widget(filter_layout)

        self.add_widget(layout)

        # read number of lines in file, add that many labels and checkboxes, each checkbox will either connect or disconnect filter
    def addfilter(self,filter_layout):
        try:
            file = open("data/blocklist", "r")
            lines = file.readlines()
        except Exception as e:
            print(e)
            print("Unable to load blocklist\n")
            return


        for line in lines[:20]:
            # Display up to 20 filters
            row = BoxLayout(orientation = "horizontal", size_hint_y = None, height = 40)
            label = Label(text=line.strip(),  halign = "left", valign = "middle", color = (0,0,0))
            label.bind(size=label.setter("text_size"))
            checkbox = CheckBox(size_hint_x=None, width = 40, color = (0,0,0))

            checkbox.bind(
                active=lambda instance, value, line=line.strip(): self.on_checkbox_active(instance, value, line))

            row.add_widget(label)
            row.add_widget(checkbox)
            filter_layout.add_widget(row)

        #close file?



        #self.add_widget(Label(color = (0,0,0), text='This is the Filter configuration Screen'))

    def on_checkbox_active(self, checkbox, value, line):
        if value:
            print(f"Checkbox selected for line: {line}")
            #self.filter_manager.add_block_list(line)
            #not sure what function to call here
        else:
            print(f"Checkbox deselected for line: {line}")

            #self.filter_manager.delete_block_list

class Stats_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats_manager = App.get_running_app().stats_manager

        self.add_widget(Label(text='This is the Statistics Screen'))

        # Display VPN status
        self.vpn_label = Label(text=f"VPN Status: {self.stats_manager.get_vpn_status()}")
        self.add_widget(self.vpn_label)

        # Display Server status
        self.server_label = Label(text=f"Server Status: {self.stats_manager.get_server_status()}")
        self.add_widget(self.server_label)

        # Display Filter status
        self.filter_label = Label(text=f"Filter Status: {self.stats_manager.get_filter_status()}")
        self.add_widget(self.filter_label)

    def update_stats(self):
        # Update the labels with current statistics
        self.vpn_label.text = f"VPN Status: {self.stats_manager.get_vpn_status()}"
        self.server_label.text = f"Server Status: {self.stats_manager.get_server_status()}"
        self.filter_label.text = f"Filter Status: {self.stats_manager.get_filter_status()}"

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
        self.vpn_button = Button(text='VPN', on_press=lambda x:setattr(self.sm,'current','vpn'))
        self.filter_button = Button(text='Filter', on_press=lambda x:setattr(self.sm,'current','filter'))
        self.stats_button = Button(text='Statistics', on_press=lambda x:setattr(self.sm,'current','stat'))
        menu_bar.add_widget(self.vpn_button)
        menu_bar.add_widget(self.filter_button)
        menu_bar.add_widget(self.stats_button)

        # Attach menu bar above screen manager
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(menu_bar)
        main_layout.add_widget(self.sm)
        
        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        # Trigger on_enter update for vpn screen when main screen is activated
        self.sm.current = 'vpn'

class Client_App(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloud_manager = Cloud_Manager()
        self.vpn_manager = VPN_Manager()
        self.filter_manager = None
        self.stats_manager = Stats_Manager()
        self.server_monitor = Thread(target=self.cloud_manager.monitor_server, daemon=True)
        self.server_monitor.start()
        self.vpn_monitor = Thread(target=self.vpn_manager.monitor_connection, daemon=True)
        self.vpn_monitor.start()
        return

    def build(self):
        self.root_sm = ScreenManager(transition=NoTransition())
        login_screen = Login_Screen(name='login')
        main_screen = Main_Screen(name='main')
     
        # Add root screens
        self.root_sm.add_widget(login_screen)
        self.root_sm.add_widget(main_screen)
        return self.root_sm
    
    def on_stop(self):
        # disconnect VPN
        while(self.vpn_manager.disconnect() == 0):
            continue
        # delete cloud resources TODO
        pass

if __name__ == '__main__':
    asyncio.run(Client_App().async_run(async_lib='asyncio'))
