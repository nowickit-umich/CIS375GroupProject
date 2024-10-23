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


#This sets background color, has no impact unless the background image is commented out or removed
#Window.clearcolor = (1,1,1)

#Change window size on startup, may have to change later.
Window.size = (1200,750)


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
    def __init__(self, **kwargs):
        super(vpnScreen, self).__init__(**kwargs)

        bottom_bar = AnchorLayout(anchor_y='bottom', size_hint_y=None, height=50)
        layout = BoxLayout()

        #check color on kivy.org
        layout.add_widget(Button(text='Connect', background_color=(0, 0, 20)))

        #call connect function

        layout.add_widget(Button(text='Disconnect', background_color=(20, 0, 0)))
        #call disconnect function

        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)
        # self.add_widget(Label(text='This is the VPN Connection Screen'))

        # can add a font style in project folder to change display font
        self.add_widget(Label(text='Status: ', color=(0, 0, 0), font_size=50, pos=(0,40), bold=True))
        self.add_widget(Label(text='Time Connected - ', color=(0, 0, 0), font_size = 25, pos = (0,-40), bold = True)) #add stopwatch here, starts when vpn connect
        self.add_widget(Label(text='IP Address - ', color=(0, 0, 0), font_size = 25, pos = (0,-80), bold = True)) #create function to read ip address
        self.add_widget(Label(text='Ping ms ', color=(0, 0, 0), font_size = 25, pos = (0,-120), bold = True)) #create function to read ping




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
        layout.add_widget(Button(text='Create Server'))
        layout.add_widget(Button(text='Delete Server'))
        bottom_bar.add_widget(layout)
        self.add_widget(bottom_bar)


class UI_DEMOApp(App):
    def build(self):
        sm = ScreenManager()

        # Add screens
        sm.add_widget(vpnScreen(name='vpn'))
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
        #could do %c, which displays Sun Sep 8 07:06:05 2013
        #idea behind including time zone name is if we change the server to a different location, the time zone could change
        #even if we don't let user change region it makes the software easier to improve in the future

if __name__ == '__main__':
    UI_DEMOApp().run()
