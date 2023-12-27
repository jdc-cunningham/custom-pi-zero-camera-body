'''
- boots
  - ask if charged (battery)
  - idle
    (click center button or shutter) show camera pass through, wait for buttons, maybe overlay telemetry/horizon,
    sample imu in separate thread
  - shutter (photo)
  - non-center d-pad button (show/navigate menu)
  - CRON sqlite db counter for battery consumption
'''

import time

from buttons.buttons import Buttons
# from battery.battery import BattDb
from camera.camera import Camera
from menu.menu import Menu
from display.display import Display
from utils.utils import Utils
from imu.imu import Imu # 6050 or GY-91

class Main:
  def __init__(self):
    self.on = True
    self.display = None
    self.controls = None
    self.utils = None
    self.menu = None
    self.camera = None
    self.live_preview_active = False
    self.zoom_active = False
    self.processing = False # debouncer for button action
    self.active_menu = "Home"

    self.startup()

    # keep main running
    while (self.on):
      print('on') # replace with battery check
      time.sleep(60)

  def startup(self):
    self.utils = Utils()
    self.display = Display(self.utils.pi_ver, self.utils, self)
    self.camera = Camera(self.display, self)
    self.menu = Menu(self.display, self.camera, self)
    self.display.show_boot_scene()
    self.display.start_menu()
    self.controls = Buttons(self.button_pressed)
    self.imu = Imu()

    self.imu.start()
    self.camera.start()
    self.controls.start()

  def button_pressed(self, button):
    # debouncer
    if (self.processing):
      return

    self.processing = True

    if (button == "SHUTTER"):
      if (self.active_menu == "Video"):
        self.menu.update_state(button)
      else:
        self.camera.handle_shutter()
    else:
      if (self.live_preview_active and button == "BACK"):
        if (self.zoom_active):
          self.camera.zoom_out()
        else:
          self.camera.toggle_live_preview(False)
          self.live_preview_active = False
          time.sleep(0.15)
          self.display.start_menu()
        self.processing = False
      elif (self.live_preview_active and (button == "CENTER" or button == "BACK")):
        self.camera.handle_zoom(button)
      elif (self.zoom_active and (button != "CENTER")):
        self.camera.handle_pan(button)
      elif (self.live_preview_active):
        self.processing = False
        return
      else:
        self.menu.update_state(button)

    # debounce
    time.sleep(0.3)

Main()
