import app
import wifi
import json
import os

from requests import get
from system.eventbus import eventbus
from app_components import clear_background

from events.input import Buttons, BUTTON_TYPES

IPIFY_URL = "https://api.ipify.org"


class DanApp(app.App):

    state = "init"
    ip = ""
    ip_displayed = False

    def __init__(self):
        self.button_states = Buttons(self)
        
    def check_wifi(self):
        self.update_state("checking_wifi")
        #connect_wifi()
        ssid = wifi.get_ssid()
        if not ssid:
            print("No WIFI config!")
            return

        if not wifi.status():
            wifi.connect()
            while True:
                print("Connecting to")
                print(f"{ssid}...")


        if self.state != "checking_wifi":
            self.update_state("checking_wifi")
        connected = wifi.status()
        if not connected:
            self.update_state("no_wifi")
        return connected
    
    def get_ip(self):
        if not self.check_wifi():
            self.update_state("no_wifi")
        self.update_state("getting_ip")

    def background_update(self, delta):
        if self.state == "getting_ip":
            try:
                self.response = get(IPIFY_URL)
            except Exception:
                try:
                    self.response = get(IPIFY_URL)
                except Exception:
                    self.update_state("no_ip")
                    return
            self.update_state("ip_received")
            
    def update_state(self, state):
        print(f"State Transition: '{self.state}' -> '{state}'")
        self.state = state
        
    def handle_ip(self):
        if not self.response:
            return
        self.ip = self.response.text
        self.update_state("ip_ready")

    
        

    def update(self, delta):
        if self.state == "init":
            print("calling get ip")
            self.get_ip()
        elif self.state == "ip_received":
            self.handle_ip()
        elif self.state == "ip_ready" and not self.ip_displayed:
            self.ip_displayed = True
        elif self.state == "no_ip":
            self.ip = "Error :("
            
        
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()

    def draw(self, ctx):
        ctx.save()
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        clear_background(ctx)
        if self.state == 'init':
            ctx.rgb(0.2,0,0).rectangle(-120,-120,240,240).fill()
            ctx.rgb(1,0,0).move_to(-80,0).text("Calling get_ip")
        elif self.state == 'ip_received':
            ctx.rgb(0.2,0,0).rectangle(-120,-120,240,240).fill()
            ctx.rgb(1,0,0).move_to(-80,0).text("IP Received")
        elif self.state == 'ip_ready':
            ctx.rgb(0,0.2,0).rectangle(-120,-120,240,240).fill()
            ctx.rgb(0,1,0).move_to(-10,0).text(self.ip)
        elif self.state == 'no_ip':
            ctx.rgb(0.2,0,0).rectangle(-120,-120,240,240).fill()
            ctx.rgb(1,0,0).move_to(-10,0).text(self.ip)
            
        
        
        ctx.restore()
        
    def connect_wifi():
        ssid = wifi.get_ssid()
        if not ssid:
            print("No WIFI config!")
            return

        if not wifi.status():
            wifi.connect()
            while True:
                print("Connecting to")
                print(f"{ssid}...")

                # if wifi.wait():
                #    break

__app_export__ = DanApp
