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
from kivy.core.window import Window

from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
from filter_manager import Filter_Manager
from observer import Observer

import os
import asyncio
import logging
from threading import Thread

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Loading_Overlay(ModalView):
    '''
    Description: Displays an animated loading icon and blocks the screen. 
    NOTE: must be called with Clock.schedule_once to ensure it is placed on top of the screen
    '''
    def __init__(self, message="", **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0.6)
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        layout = FloatLayout()
        layout.add_widget(
            Image(
                source="data/images/load.zip", 
                anim_delay = 1/60,
                anim_loop = 0,
                size_hint = (0.15, 0.15),
                pos_hint = {"center_x": 0.5, "center_y": 0.5}
            )
        )
        layout.add_widget(
            Label(
                text=message,
                pos_hint = {"center_x": 0.5, "center_y": 0.3}
            )
        )
        self.add_widget(layout)

    def on_touch_down(self, touch):
        '''
        Description: Ensures that the overlay intercepts all touch events 
        '''
        return True

class Login_Screen(Screen):
    '''
    Description: Displays a login screen which allows the user to select the cloud type and enter their API credentials
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        font_size = dp(16)

        self.loading = Loading_Overlay("Validating Credentials...")

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

        param b: instance of the calling button; unused
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
        Clock.schedule_once(self.loading.open, 0)
        try:
            logger.debug("Checking Credentials")
            is_valid = await asyncio.to_thread(app.cloud_manager.setup, credentials) 
        except Exception as e:
            # TODO error handling            
            is_valid = False
            logger.error(f"Error checking credentials: {e}")
        # schedule update status to execute
        Clock.schedule_once(lambda x: self.update_status(is_valid, credentials))
        Clock.schedule_once(self.loading.dismiss, 0)
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

class Status_Widget(GridLayout, Observer):
    '''
    Description: Widget which contains all status information about the server and VPN connection.
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
        self.is_updated = True

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

    def update(self, cloud_manager, vpn_manager):
        '''
        Description: Updates the contents of the status widget
        param cloud_manager: Cloud_Manager to get status from
        param vpn_manager: VPN_Manager to get status from
        '''
        if cloud_manager is not None:
            self.server_status.text = cloud_manager.server_status
            #if cloud_manager.server_ip != None:
            self.server_ip.text = cloud_manager.server_ip
            self.is_updated = True
        if vpn_manager is not None:
            if vpn_manager.is_connected:
                self.vpn_status.text = "Connected"
            else:
                self.vpn_status.text = "Disconnected"
            self.is_updated = True

class VPN_Screen(Screen):
    '''
    Description: Displays the server status and VPN connection status. Contains buttons to allow
    control of server and VPN connection.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # get references to necessary managers
        self.vpn_manager = App.get_running_app().vpn_manager
        self.cloud_manager = App.get_running_app().cloud_manager

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Server Status Display
        self.status = Status_Widget()
        # register observers
        self.cloud_manager.add_observer(self.status)
        self.vpn_manager.add_observer(self.status)

        layout.add_widget(self.status)
        self.connect_button_lock = False
        self.connect_button = Button(text="Connect", size_hint=(1, None), height=50)
        #self.connect_button.disabled = True
        layout.add_widget(self.connect_button)

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
        self.server_button_lock = False
        self.server_button = Button(text="Start Server", size_hint=(1, None), height=50)
        layout.add_widget(self.server_button)
        self.add_widget(layout)
        return

    def on_location_select(self, instance, text=None):
        '''
        Description: Updates the cloud_manager location based on user input 
        '''
        self.cloud_manager.server_location = self.server_location_selector.text

    def update(self, dt=0):
        '''
        Description: Updates the status display and update the UI elements based
        on the current status.
        '''
        if not self.status.is_updated:
            return

        # Update server button
        if self.status.server_status.text == "Offline":
            App.get_running_app().root_sm.get_screen('main').filter_button.disabled = True
            App.get_running_app().root_sm.get_screen('main').stats_button.disabled = True
            self.connect_button.disabled = True
            self.server_button.text = "Start Server"
            self.server_button.background_color = (0,1,0)
            self.server_button.on_press = lambda: asyncio.create_task(self.on_create_server())
            if not self.server_button_lock:
                self.server_location_selector.disabled = False
        elif self.status.server_status.text == "Starting":
            App.get_running_app().root_sm.get_screen('main').filter_button.disabled = True
            App.get_running_app().root_sm.get_screen('main').stats_button.disabled = True
            self.connect_button.disabled = True
            self.server_button.disabled = True
            self.server_location_selector.disabled = True
            self.server_button.text = "Server Starting"
        elif self.status.server_status.text == "Running":
            if not self.connect_button_lock:
                self.connect_button.disabled = False
            self.server_button.text = "Stop Server"
            self.server_button.background_color = (1,0,0)
            self.server_button.on_press = lambda: asyncio.create_task(self.on_delete_server())
            if not self.server_button_lock:
                self.server_button.disabled = False
        self.status.is_updated = False
        
        # Update vpn button
        if self.status.vpn_status.text == "Connected":
            App.get_running_app().root_sm.get_screen('main').filter_button.disabled = False
            App.get_running_app().root_sm.get_screen('main').stats_button.disabled = False
            self.connect_button.text = "Disconnect VPN"
            self.connect_button.background_color = (1,0,0)
            self.connect_button.on_press = lambda: asyncio.create_task(self.on_disconnect())
        else:
            App.get_running_app().root_sm.get_screen('main').filter_button.disabled = True
            App.get_running_app().root_sm.get_screen('main').stats_button.disabled = True
            self.connect_button.text = "Connect VPN"
            self.connect_button.background_color = (0,1,0)
            self.connect_button.on_press = lambda: asyncio.create_task(self.on_connect())

        return
    
    async def on_connect(self):
        '''
        Description: Asynchronously attempts to establish a VPN connection.
        '''
        Clock.schedule_once(lambda x: setattr(self, "connect_button_lock", True))
        Clock.schedule_once(lambda x: setattr(self.connect_button, 'disabled', True))
        try:
            await asyncio.to_thread(self.vpn_manager.connect, self.cloud_manager.server_ip)
            await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"VPN Connect error: {str(e)}")
        Clock.schedule_once(lambda x: setattr(self, "connect_button_lock", False))
    
    async def on_disconnect(self):
        '''
        Description: Asynchronously attempts to disconnect the VPN
        '''
        Clock.schedule_once(lambda x: setattr(self, "connect_button_lock", True))
        Clock.schedule_once(lambda x:setattr(self.connect_button, 'disabled', True))
        try:
            await asyncio.to_thread(self.vpn_manager.disconnect)
        except Exception as e:
            logger.error(f"VPN Disconnect error: {str(e)}")
        Clock.schedule_once(lambda x: setattr(self, "connect_button_lock", False))

    async def on_create_server(self):
        '''
        Description: Asynchronously attempts to create a new server in the currently 
        selected location. 
        '''
        Clock.schedule_once(lambda x: setattr(self, "server_button_lock", True))
        #Clock.schedule_once(lambda x: setattr(self.cloud_manager, 'server_status', "Starting"))
        Clock.schedule_once(lambda x: setattr(self.server_button, 'disabled', True))
        Clock.schedule_once(lambda x: setattr(self.server_location_selector, 'disabled', True))
        try:
            await asyncio.to_thread(self.cloud_manager.create_server)
        except Exception as e:
            logger.error(f"Create server error: {str(e)}")
        Clock.schedule_once(lambda x: setattr(self, "server_button_lock", False))

    async def on_delete_server(self):
        '''
        Description: Asynchronously attempts to delete the running server. 
        '''
        Clock.schedule_once(lambda x: setattr(self, "server_button_lock", True))
        Clock.schedule_once(lambda x: setattr(self.server_button, 'disabled', True))
        load = Loading_Overlay("Stopping Server...")
        Clock.schedule_once(load.open)
        try:
            if self.status.vpn_status.text == "Connected":
                await asyncio.to_thread(self.vpn_manager.disconnect)
            await asyncio.to_thread(self.cloud_manager.delete_server)
            # wait for status to update
            await asyncio.sleep(4)
        except Exception as e:
            logger.error(f"Delete server error: {str(e)}")
            Clock.schedule_once(lambda x: setattr(self.server_button, 'disabled', False))
        Clock.schedule_once(lambda x: setattr(self, "server_button_lock", False))
        Clock.schedule_once(load.dismiss)

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

        '''
        Description: Allows user to activate/deactivate filters as they choose
        User activates/deactivates checkboxes to change status of filters
        Filters are .block files with multiple domains that can be blocked
        '''
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filter_manager = Filter_Manager()
        self.selected_filters = set()  # Store the selected filters

        # main layout
        layout = FloatLayout()

        # layout for filter checkbox
        self.filter_layout = BoxLayout(orientation = "vertical", size_hint = (.8, .8), pos_hint = {"x":.5, "y":.5}, spacing = 10)
        # Title
        layout.add_widget(Label(text="[b]Configure Block Lists[/b]", markup=True, font_size=dp(18), halign='left', size_hint=(0.5, 0.1), pos_hint={"x":0.25, "y":0.85}))
        layout.add_widget(self.filter_layout)

        # update filter lists button
        send_update_button = Button(text="Update Blocklists", size_hint=(.4, .1), pos_hint={"x": .3, "y": .05})
        send_update_button.bind(on_press=lambda x:asyncio.create_task(self.on_send_update()))
        layout.add_widget(send_update_button)
        # add main layout
        self.add_widget(layout)

    def add_checkboxes(self, filter_layout):
        '''
        Description: adds a checkbox widget for each block list in the filter_manager. 
        '''
        filter_layout.clear_widgets()
        for list in self.filter_manager.block_list:
            name = list['name'].removesuffix(".block")
            row = BoxLayout(orientation = "horizontal", size_hint = (None,None), height = 40)
            label = Label(text=name,  halign = "right", valign = "middle", color = (1,1,1))
            label.bind(size=label.setter("text_size"))
            
            checkbox = CheckBox(size_hint_x=None, width = 40, color = (1,1,1), active=list['enabled'])

            checkbox.bind(
                active=lambda instance, value, name=name: self.on_checkbox_active(instance, value, name)
            )
            row.add_widget(label)
            row.add_widget(checkbox)

            filter_layout.add_widget(row)

    def on_checkbox_active(self, checkbox, value, name):
        if value:
            self.filter_manager.enable_list(name)
        else:
            self.filter_manager.disable_list(name)

    async def on_send_update(self):
        # move to thread because send_update blocks
        try:
            await asyncio.to_thread(self.filter_manager.send_update)
        except Exception as e:
            logger.error(f"Send filter update error: {str(e)}")
        return
    
    async def sync_list(self):
        try:
            await asyncio.to_thread(self.filter_manager.get_server_lists)
            # Add the checkbox widgets
            self.add_checkboxes(self.filter_layout)
            self.load.dismiss()
        except:
            logger.error("Unable to get server filter lists")

    def on_pre_enter(self, *args):
        self.load = Loading_Overlay("Getting Active Filters...")
        self.load.open()
        # get server address
        addr = App.get_running_app().cloud_manager.server_private_ip
        # set address of filter manager
        if self.filter_manager.server_host != addr:
            self.filter_manager.is_updated = False
            self.filter_manager.server_host = addr
        asyncio.create_task(self.sync_list())
        logger.debug("Filter Screen Initialized")
        
class Stats_Screen(Screen):
    '''
    Description: Displays various statistics related to VPN, server status, and DNS data. 
    Includes buttons to toggle between views such as blocked domains, top visited domains, 
    top blocked domains, data blocked for domains, and DNS data.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats_manager = App.get_running_app().stats_manager
        
        # Create the main layout for the screen
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Create a layout to hold the statistics in the center
        self.stats_layout = FloatLayout(size_hint=(.75, .75), height=dp(400), pos_hint={"center_x": 0.5, "center_y": 0.5})  # Set a fixed height for the scrollable area

        # Buttons for toggling each section
        self.top_visited_button = Button(text="View Top 10 Visited Domains", size_hint_y=None, height=dp(40))
        self.top_blocked_button = Button(text="View Top 10 Blocked Domains", size_hint_y=None, height=dp(40))
        self.data_blocked_button = Button(text="View Data Blocked for Domains", size_hint_y=None, height=dp(40))

        # Create labels to hold the data
        self.top_visited_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        self.top_blocked_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        self.data_blocked_label = Label(size_hint=(None, None), height=dp(40), width=dp(300), markup=True)
        
        # Initially set all labels to be hidden
        self.top_visited_label.text = ""
        self.top_blocked_label.text = ""
        self.data_blocked_label.text = ""

        # Add widgets to the layout
        main_layout.add_widget(self.stats_layout)

        # Add buttons at the bottom
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(60), orientation='horizontal')
        buttons_layout.add_widget(self.top_visited_button)
        buttons_layout.add_widget(self.top_blocked_button)
        buttons_layout.add_widget(self.data_blocked_button)

        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)

        # Bind buttons to their functions
        self.top_visited_button.bind(on_press=self.show_top_visited)
        self.top_blocked_button.bind(on_press=self.show_top_blocked)
        self.data_blocked_button.bind(on_press=self.show_data_blocked)

    # Display the top 10 visited domains
    def show_top_visited(self, instance=None):
        self.stats_layout.clear_widgets()
        self.top_visited_label.text = "[b][u]Top 10 Visited Domains:[/u][/b]\n"
        top_visited_list = self.stats_manager.get_top_visited()
        for domain in top_visited_list:
            self.top_visited_label.text += f"\n{domain['domain']} - Traffic: {domain['traffic']}"
        self.top_visited_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.top_visited_label)

     # Display the top 10 blocked domains
    def show_top_blocked(self, instance=None):
        self.stats_layout.clear_widgets()
        self.top_blocked_label.text = "[b][u]Top 10 Blocked Domains:[/u][/b]\n"
        top_blocked_list = self.stats_manager.get_top_blocked_domains()
        for domain in top_blocked_list:
            self.top_blocked_label.text += f"\n{domain['domain']} - Times Blocked: {domain['denied']}"
        self.top_blocked_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.top_blocked_label)

    # Display the data blocked for each domain
    def show_data_blocked(self, instance=None):
        self.stats_layout.clear_widgets()
        self.data_blocked_label.text = "[b][u]Data Blocked for Each Domain:[/u][/b]\n"
        total_data = self.stats_manager.get_total_data()
        for domain in total_data:
            self.data_blocked_label.text += f"\n {domain['domain']} - Total Data Blocked: {domain['total_data']} MB"
        self.data_blocked_label.center = self.stats_layout.center
        self.stats_layout.add_widget(self.data_blocked_label)

    async def sync_log(self, server_address):
        try:
            await asyncio.to_thread(self.stats_manager.update_log, server_address)
        except Exception as e:
            logger.error(f"Error Fetching DNS Log: {e}")
        self.show_top_blocked()
        self.load.dismiss()
        return

    def on_pre_enter(self):
        self.load = Loading_Overlay("Fetching DNS Logs...")
        self.load.open()
        addr = App.get_running_app().cloud_manager.server_private_ip
        asyncio.create_task(self.sync_log(addr))
        return

class Main_Screen(Screen):
    '''
    Description: This screen is just a container for the menu bar. All other screens (except login) are within
    this screens screen manager.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create Screens
        self.sm = ScreenManager()
        self.vpn_screen = VPN_Screen(name='vpn')
        self.filter_screen = Filter_Screen(name='filter')
        self.stats_screen = Stats_Screen(name='stat')

        # Add screens to screen manager
        self.sm.add_widget(Screen(name='int'))
        self.sm.add_widget(self.vpn_screen)
        self.sm.add_widget(self.stats_screen)
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
    '''
    Description: Main client application
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloud_manager = Cloud_Manager()
        self.vpn_manager = VPN_Manager()
        self.stats_manager = Stats_Manager()
        self.server_monitor = Thread(target=self.cloud_manager.monitor_server, daemon=True)
        self.server_monitor.start()
        self.vpn_monitor = Thread(target=self.vpn_manager.monitor_connection, daemon=True)
        self.vpn_monitor.start()
        return

    def build(self):
        Window.title = "VPN Client"

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
    # Run the client app within asyncio
    asyncio.run(Client_App().async_run(async_lib='asyncio'))
