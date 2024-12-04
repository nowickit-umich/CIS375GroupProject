#messed around with this branch a bit so some of the other features might not work correctly in other screens

#there are a lot of print functions that dont need to be here, they are just there for testing purposes

#there are two different ways that are implemented for the enable and disable filter functions
#one is in the checkbox active method and another is in the sendupdate function in filterscreen
#cant get the filter manager functions to work since the class in the file needs a server address and i can't get it to compile
#the selected filters don't print or send in a specific order, for some reason it is random
#not sure if it matters what order the blocklist is being sent as long as correct lists are sent

from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
from filter_manager import FilterManager

import os
import asyncio

# UI Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView


from kivy.logger import Logger
Logger.setLevel('DEBUG')

#removed the background image to prevent issues of multiple images loading at one time,
#will implement background image on each different tab,
"""
Builder.load_string('''
<BoxLayout>  
    canvas.before:
        BorderImage:
            source: 'images/Earth2.png'
            pos: self.pos
            size: self.size
''')
"""

#add this to match the image color, so the screen tabs dont have a black background
Window.clearcolor = (1,1,1)

Window.size = (1300,750)

#Window.fullscreen = True



def call_async(function):
    # returns a synchronous wrapper function for use with kivy
    def wrapper(x):
        asyncio.create_task(function(x))

    return wrapper


class Login_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.add_widget(self.layout)



        font_size = dp(16)

        # Define UI
        self.cloud_types = ["AWS", "Google Cloud", "Azure"]
        self.input_access = TextInput(
            multiline=False,
            padding=(font_size / 2, font_size / 2, font_size / 2, 0),
            write_tab=False,
            font_size=font_size,
            size_hint_y=None,
            height=font_size + dp(20)
        )
        self.input_secret = TextInput(
            multiline=False,
            padding=(font_size / 2, font_size / 2, font_size / 2, 0),
            write_tab=False,
            font_size=font_size,
            size_hint_y=None,
            height=font_size + dp(20),
            password=True
        )
        self.message = Label(text="", size_hint=(1, 0.1))
        self.save_cred = CheckBox(color = (0,0,0), size_hint=(None, None), size=(dp(20), dp(20)))
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
        login_entry = GridLayout(cols=2, rows=4, spacing=10, size_hint=(0.9, 0.8))
        login_entry.add_widget(Label(
            text="Cloud Platform:", size_hint=(None, None), height=dp(30), color = (0,0,0),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.select_cloud)
        login_entry.add_widget(Label(
            text="Access Token:", size_hint=(None, None), height=font_size + dp(20), color = (0,0,0),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.input_access)
        login_entry.add_widget(Label(
            text="Secret Token:", size_hint=(None, None), height=font_size + dp(20), color = (0,0,0),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.input_secret)
        login_entry.add_widget(Label(
            text="Save Credentials:", size_hint=(None, None), height=dp(20), color = (0,0,0),
            width=label_width, halign="right", valign='middle', text_size=(label_width, None)
        ))
        login_entry.add_widget(self.save_cred)

        # Login box layout
        login_box = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(120), spacing=dp(5))
        login_box.add_widget(self.message)
        login_box.add_widget(login_button)

        # Anchor widgets into place
        center = AnchorLayout(anchor_x="center", anchor_y="center")
        center.add_widget(login_entry)
        self.add_widget(center)

        self.layout.add_widget(login_box)

        """
        bottom = AnchorLayout(anchor_x="center", anchor_y="bottom")
        bottom.add_widget(login_box)
        self.add_widget(bottom)"""

        # Check for saved credentials
        self.read_credentials()

    async def login(self, x):
        # DEBUG LOGIN BYPASS
        # self.manager.current = 'main'
        # return

        access = self.input_access.text
        secret = self.input_secret.text
        cloud_name = self.select_cloud.text
        if access == "" or secret == "":
            #self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
            return

        #self.message.color = (1, 1, 1, 1)
        self.message.color = (0,0,0)
        self.message.text = "Validating Credentials..."
        await asyncio.sleep(0)  # Update UI

        app = App.get_running_app()
        try:
            await app.cloud_manager.setup(cloud_name, [access, secret])
        except Exception as e:
            # TODO error handling
            print(e)
            self.message.color = (1, 0.2, 0.2, 1)
            self.message.text = "Error: Invalid Credentials"
            return

        # Login Success
        app.login = True
        self.message.color = (1, 1, 1, 1)
        self.message.text = "Login Successful!"
        await asyncio.sleep(0)

        # Save credentials
        if self.save_cred:
            self.save_credentials(cloud_name, access, secret)
        # Switch to main screen
        self.manager.current = 'main'
        return

    def save_credentials(self, cloud_name, access, secret):
        try:
            file = open("data/credentials.secret", "w")
        except Exception as e:
            print(e)
            print("Unable to save credentials")
            return
        file.write(cloud_name + '\n')
        file.write(access + '\n')
        file.write(secret + '\n')
        return

    # FORMAT: put each value on its own line
    # CLOUD_NAME
    # ACCESS KEY
    # SECRET KEY
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

        layout = FloatLayout()

        background_image = Image(source="images/Earth2.png", allow_stretch=True, keep_ratio=False,
                                 size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        layout.add_widget(background_image)

        # get references to necessary managers
        self.vpn_manager = App.get_running_app().vpn_manager
        self.cloud_manager = App.get_running_app().cloud_manager

        # Server Status Display test
        server_status = BoxLayout(orientation="vertical", padding=20, spacing=10,
                                  size_hint=(0.8, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})



        self.time_connected_label = Label(
            text='Time Connected -',
            color=(0, 0, 0),
            font_size=25,
            bold=True
        )

        server_status.add_widget(self.time_connected_label)  # Add above server location selector



        self.status_label = Label(text=f"Status: {self.cloud_manager.server_status}", font_size=20, color = (0,0,0), bold = True)
        server_status.add_widget(self.status_label)

        # Server Location Selector
        self.server_location_selector = Spinner(
            text=self.cloud_manager.locations[0],
            values=self.cloud_manager.locations,
            size_hint=(1, None),
            height=44
        )
        server_status.add_widget(self.server_location_selector)





        # Connect/Disconnect Button

        self.server_active = False #When true, server is active, when false server is inactive
        #when inactive the bottom button on vpn tab will say start server
        #when true the button will display connect/disconnect
        self.is_connected = False #when false, display connect button, when true display disconnect button


        self.connect_button = Button(text="Start Server", size_hint=(1, None), height=50, color = (0,0,0), on_press = self.changestatus)
        server_status.add_widget(self.connect_button)

        #self.add_widget(server_status)

        #return

        layout.add_widget(server_status)

        self.add_widget(layout)

    def update(self, dt):
        # Update status
        self.status_label.text = f"Status: {self.cloud_manager.server_status}"
        # Update button text
        if self.cloud_manager.server_status == "Offline":
            self.connect_button.text = "Start Server"

            #self.cloud_manager.start_server()
        elif self.cloud_manager.server_status == "Online":
            if self.vpn_manager.is_connected:
                self.connect_button.text = "Disconnect VPN"
            else:
                self.connect_button.text = "Connect VPN"
        return

    def changestatus(self, dt):
        #self.status_label.text = f"Status: {self.cloud_manager.server_status}"
        if not self.server_active: #if server is not active
            # First press action: Start server
            #self.cloud_manager.server_status == "Online"
            #need to make the above line work so the update function will work correctly to change text from start server to connect vpn
            #right now it will detect the server is activated and change the text to connect vpn but the text quickly returns to start server

            #self.cloud_manager.create_server()

            self.cloud_manager.start_server()
            self.server_active = True
            self.connect_button.text = "Connect VPN"
            #print(self.cloud_manager.server_status) #prints offline
        elif not self.is_connected: #if server is active and vpn is not connected
            # Second press action: Connect VPN
            self.vpn_manager.connect()
            self.is_connected = True
        else: #if server is active and vpn is connected
            # Third press action: Disconnect VPN
            self.vpn_manager.disconnect()
            self.is_connected = False


    def on_pre_enter(self, *args):
        # Update location selector
        self.server_location_selector.text = self.cloud_manager.locations[0]
        self.server_location_selector.values = self.cloud_manager.locations
        # Add update loop
        self.event_loop = Clock.schedule_interval(self.update, 1)

    def on_leave(self, *args):
        Clock.unschedule(self.event_loop)
        return


class Filter_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_filters = set()  # Store the selected filters

        #self.filter_manager = App.get_running_app().filter_manager
        #not sure above line is needed

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

        sendupdatebutton = Button(text="Send Updated Blocklist", size_hint=(.4, .1), pos_hint={"x": .3, "y": .05})
        sendupdatebutton.bind(on_press=self.sendfilterupdate)
        layout.add_widget(sendupdatebutton)

        self.add_widget(layout)

        #add blocklist name instead of file contents
        #remove file header just display name

    def addfilter(self,filter_layout):
        """ #this was for reading the data in the blocklist file, don't need this comment section anymore
        try:

            file = open("data/blocklist", "r")

            lines = file.readlines()
        except Exception as e:
            print(e)
            print("Unable to load blocklist\n")
            return
        """

        #reading from "data" directory
        try:
            lines = os.listdir("data")

        except Exception as e:
            print(e)
            print("Unable to load blocklist\n")
            return

        for line in lines[:20]:
            #only displays files with .block in their name
            #
            if line.endswith(".block"):
                textline = os.path.splitext(line)[0]
                # Display up to 20 filters
                row = BoxLayout(orientation = "horizontal", size_hint_y = None, height = 40)
                label = Label(text=textline.strip(),  halign = "left", valign = "middle", color = (0,0,0))
                label.bind(size=label.setter("text_size"))
                checkbox = CheckBox(size_hint_x=None, width = 40, color = (0,0,0))

                checkbox.bind(
                    active=lambda instance, value, line=line.strip(): self.on_checkbox_active(instance, value, line))
                    #might need to be line.strip() instead of textline, since the filter manager will need the .block extension
                row.add_widget(label)
                row.add_widget(checkbox)
                filter_layout.add_widget(row)

        #close file?

    def on_checkbox_active(self, checkbox, value, line):
        if value:
            print(f"Checkbox selected for line: {line}")

            self.selected_filters.add(line)  # Add to selected filters

            #self.filter_manager.enable_list(line)

            #right now this method sends the .block extension as well as the name,
            #if that needs to change, change checkbox.bind line to line=textline

        else:
            print(f"Checkbox deselected for line: {line}")

            self.selected_filters.discard(line)  # Remove from selected filters

            #self.filter_manager.disable_list(line)


    def sendfilterupdate(self, instance):

        #if checkbox of blocklist or blocklist 2 is enabled, send it to the enable_list

        print("list sent")
        print("Selected filters:", list(self.selected_filters))

        try:
            lines = os.listdir("data")

        except Exception as e:
            print(e)
            print("Unable to load blocklist\n")
            return

        for line in lines[:20]:
            line = line.strip() #this will have .block extension
            #self.filter_manager.disable_list(line) #uncomment

            #disabling every blocklist so blocklists not selected arent enabled
            #definetly a better way to do this instead of just reading the file again
            #maybe create another list with full name of .block files and call each line with the disable_list(line)


        #should only send selected filters to enable_list
        for filters in list(self.selected_filters):
            #self.filter_manager.enable_list(line)
            print(filters)

        #self.filter_manager.send_update() #uncomment

    def on_pre_enter(self, *args):

        #self.filter_manager.get_list() #uncomment

        print("on_pre_enter FilterScreen Test") #just to show it is called


class Stats_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Label(color = (0,0,0), text='This is the Statistics Screen'))


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
        menu_bar.add_widget(Button(text='VPN', on_press=lambda x: setattr(self.sm, 'current', 'vpn')))
        menu_bar.add_widget(Button(text='Filter', on_press=lambda x: setattr(self.sm, 'current', 'filter')))
        menu_bar.add_widget(Button(text='Statistics', on_press=lambda x: setattr(self.sm, 'current', 'stat')))

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

        self.filter_manager = None #FilterManager()
        #not sure how to initialize this since there needs to be a server address in FilterManager class

        self.stats_manager = None
        # Add manager update loops
        Clock.schedule_interval(call_async(self.cloud_manager.update), 1)
        Clock.schedule_interval(call_async(self.vpn_manager.update), 1)
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
