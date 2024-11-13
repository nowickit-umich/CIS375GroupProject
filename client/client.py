
from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
from statistics_manager import Stats_Manager
from filter_manager import Filter_Manager

#UI Imports
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
import time
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
#from kivy.config import Config
from kivy.uix.textinput import TextInput


#Config.set('graphics', 'resizable', True)


#This sets background color, has no impact unless the background image is commented out or removed
#Window.clearcolor = (1,1,1)

#Change window size on startup, may have to change later.
Window.size = (1200,750)

class UserServer:
    def __init__(self, servname):
        self.servname = servname
        #let user change server name, could add more attributes to class to let user customize server more

#Background image
Builder.load_string('''
<BoxLayout>
    canvas.before:
        BorderImage:
            #BorderImage behaves like the CSS BorderImage
            border: 10, 10, 10, 10
            source: 'images/Earth2.png' #can change this image as we want, will need to change source when changing program location
            pos: self.pos
            size: self.size          
            ''')

class vpnScreen(Screen):
    def __init__(self, vpn_manager, **kwargs):
        super(vpnScreen, self).__init__(**kwargs)

        self.vpn_manager = vpn_manager


        #building clock feature
        self.timerunning = 0 #set timer to 0
        self.clockstatus = False #determine if clock is running, true means it is
        self.time_label = Label(text = "00:00:00", font_size = 25, pos = (160, -40), color = (0,0,0), bold = True)
        self.statuslabel = Label(text = "Disconnected" , font_size = 50, color = (20,0,0), pos = (0,10), bold = True)

        bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        layout = BoxLayout()

        #check color on kivy.org
        layout.add_widget(Button(text='Connect', background_color=(0, 0, 20), on_press = self.startclock)) #start clock



        layout.add_widget(Button(text='Disconnect', background_color=(20, 0, 0) , on_press = self.stopclock)) #stop clock



        Clock.schedule_interval(self.updateclock, 1)
        Clock.schedule_interval(self.updatestatus, .02)

        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)
        # self.add_widget(Label(text='This is the VPN Connection Screen'))

        # can add a font style in project folder to change display font
        self.add_widget(Label(text='Status: ', color=(0, 0, 0), font_size=50, pos=(0,60), bold=True))


        self.add_widget(self.statuslabel)


        self.add_widget(Label(text='Time Connected -', color=(0, 0, 0), font_size = 25, pos = (0,-40), bold = True))


        self.add_widget(self.time_label)

        self.add_widget(Label(text='IP Address - ', color=(0, 0, 0), font_size = 25, pos = (0,-80), bold = True)) #create function to read ip address

        self.add_widget(Label(text='Ping ms ', color=(0, 0, 0), font_size = 25, pos = (0,-120), bold = True)) #create function to read ping

    def startclock(self, instance):
        self.vpn_manager.connect() #call from vpn_manager instead of directly from windows_vpn
        #do this to make it easier to add functionality for other operating system
        #could create another file called mac_vpn.py
        self.timerunning = time.time()
        self.clockstatus = True

    def stopclock(self, instance):
        self.vpn_manager.disconnect()
        self.clockstatus = False
        self.time_label.text = "00:00:00"

    def updateclock(self, dt):
        if self.clockstatus:
            timespent = int(time.time() - self.timerunning) #might be time.time() - self.timer_start_time

            hours, remainder = divmod(timespent, 3600)
            mins, seconds = divmod(remainder, 60)
            self.time_label.text = f"{hours:02}:{mins:02}:{seconds:02}"

    def updatestatus(self, dt):
        if self.clockstatus:
            self.statuslabel.text = "Connected"
            self.statuslabel.color = (0,20,0)
        else:
            self.statuslabel.text = "Disconnected"
            self.statuslabel.color = (20, 0, 0)

class filterScreen(Screen):
    def __init__(self, **kwargs):
        super(filterScreen, self).__init__(**kwargs)
        self.add_widget(Label(text='This is the Filter configuration Screen', color=(0, 0, 0)))


class statScreen(Screen):
    def __init__(self, **kwargs):
        super(statScreen, self).__init__(**kwargs)
        self.add_widget(Label(text='This is the Statistics Screen', color=(0, 0, 0)))


class serverScreen(Screen):
    def __init__(self, **kwargs):


        super(serverScreen, self).__init__(**kwargs)
        self.add_widget(Label(text='This is the Server Management Screen', color=(0, 0, 0)))

        bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        layout = BoxLayout()
        layout.add_widget(Button(text='Start Server'))
        layout.add_widget(Button(text='Stop Server'))

        create_popup = (Button(text='Create Server'))
        create_popup.bind(on_release=self.createserver_popup)
        layout.add_widget(create_popup)

        layout.add_widget(Button(text='Delete Server'))

        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)

    def createserver_popup(self, instance):
        layout = BoxLayout(orientation = 'vertical')

        layout.add_widget(Label(text = 'Enter Name for Server:', pos = (0,-40)))
        #change position

        #layout.add_widget(Label(text = 'Create Server Here, allow user to enter name to create server'))

        #popup = Popup(title = 'test', auto_dismiss = True)

        servername = TextInput(multiline=False, size_hint = (1,None), height = 100)
        layout.add_widget(servername)

        UserServer(servername)

        close_button = Button(text = 'Create Server', size_hint_y= None, height = 40)
        close_button.bind(on_release = lambda x: self.createserverobject(servername.text, popup))


        #user has a popup that asks them to enter a server name to create a server
        #user can only have 1 server at a time
        #delete function clears the name of the server

        layout.add_widget(close_button)

        #popup = Popup(title = 'test', content = layout, size_hint = (.75, .75), auto_dismiss = True, background = None)

        popup = Popup(title = 'Create A Server',
                      content = layout,
                      size_hint = (.75, .75),
                      auto_dismiss = True,
                      background_color = (1,1,1,1)
                      )
        #could remove title or make it empty to not have a title in pop up

        #figure out how to get rid of blue tint in background

        popup.open()


    def createserverobject(self, servername, popup):
        #doesn't check if name is empty or any test cases
        new_server = UserServer(servername)
        print(f"Server created: {new_server.servname}")  # Confirm server creation in the console
        popup.dismiss()


class UI_DEMOApp(App):
    def build(self):
        sm = ScreenManager()

        # Add screens
        vpn_manager = VPN_Manager()
        cloud_manager = Cloud_Manager()
        filter_manager = Filter_Manager()
        stats_manager = Stats_Manager()

        sm.add_widget(vpnScreen(vpn_manager, name='vpn'))
        sm.add_widget(filterScreen(name='filters'))
        sm.add_widget(statScreen(name='stat'))
        sm.add_widget(serverScreen(name='server'))

        # Create a layout for the menu bar

        menu_bar = BoxLayout(size_hint_y=None, height=50)
        menu_bar.add_widget(Button(text='VPN', on_press=lambda x: setattr(sm, 'current', 'vpn')))
        menu_bar.add_widget(Button(text='Filter', on_press=lambda x: setattr(sm, 'current', 'filters')))
        menu_bar.add_widget(Button(text='Statistics', on_press=lambda x: setattr(sm, 'current', 'stat')))
        menu_bar.add_widget(Button(text='Server', on_press=lambda x: setattr(sm, 'current', 'server')))

        self.TimeClock = Label(font_size = 30, size_hint_y= None, height = 50, color = (0,0,0), bold = True)
        #self.TimeClock.pos_hint = {'right': 1} not too sure how this works, maybe push it to right side of screen
        Clock.schedule_interval(self.update_ClockTime, 1)

        # Create the main layout
        main_layout = BoxLayout(orientation='vertical')

        main_layout.add_widget(menu_bar)
        main_layout.add_widget(self.TimeClock)
        main_layout.add_widget(sm)


        return main_layout

    def update_ClockTime(self, dt):
        self.TimeClock.text = time.strftime(("%A, %B %d %Y %I:%M:%S %p %Z"))
        #self.TimeClock.text = time.strftime(("%c"))
        #could do %c, which displays Sun Sep 8 07:06:05 2013
        #idea behind including time zone name is if we change the server to a different location, the time zone could change
        #even if we don't let user change region it makes the software easier to improve in the future

if __name__ == '__main__':
    UI_DEMOApp().run()
