from constants import UPDATE, WARNING                   # Local file
from pypresence import Presence
from pydexcom import Dexcom
from tkinter.font import *
from tkinter import *
import credentials                                      # Local file
import PIL.ImageTk
import screeninfo
import integrity                                        # Local file
import PIL.Image
import threading
import datetime
import ctypes


class Overlay():
    def __init__(self, root):
        self.window = root
        self.visible = False 

        # Window attributes 
        self.window.config(bg="#8a899e")

        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-transparent", "#8a899e")

        self.windowChanged()

        self.window.bind("<KeyPress-F2>", self.hideWindow)
        self.window.bind("<KeyRelease-F2>", self.showWindow)
        self.window.bind("<FocusOut>", self.showWindow)

        self.window.bind("<F3>", self.closeWindow)
        
        # Application
        # TODO: Make `ous` configurable from a `settings.ini` file
        self.dexcom = Dexcom(
            credentials.get("Dexcom", "username"), 
            credentials.get("Dexcom", "password"),
            ous=True                                                    # Set `ous` to `True` if you're outside the US, eg. in Europe
        )

        # Discord Rich Presence
        # TODO: Make `Enable RPC` configurable from a `settings.ini` file, and skip any errors related to RPC if disabled
        self.RPC = Presence(client_id=credentials.get("Discord", "client_id"))
        self.RPC.connect()

        # Generate gui
        self.guiMap = {
            "text": lambda: self.canvas.itemconfig(self.glucoseLabel, text=str(self.data["mmol/L"])),
            "textColor": lambda: self.canvas.itemconfig(self.glucoseLabel, fill=("#3b3b3b" if self.data["mmol/L"] > 3.9 else "#ffffff")),
            "base": lambda: self.canvas.itemconfig(self.base, image=self.baseImages[self.data["state"]]),  # // image=self.baseImages[min(int(((self.data["mmol/L"] - 4.0) / 8.8) + 1), 2)]
            "arrow": lambda: self.canvas.itemconfig(self.arrow, image=self.arrowImages[self.data["trendNumber"] - 1]),
            "frame": lambda: self.canvas.itemconfig(self.frame, image=self.frameImages[min(max((x:=self.data["trendNumber"]) - 2, 0), 4) + (1 ^ min(x % 8, 1))]),            
        }

        self.generateGUI()


    def generateGUI(self):
        loadFont("assets/fonts/MPLUSRounded1c-ExtraBold.ttf")

        fontConfig = {
            'family': 'Rounded Mplus 1c ExtraBold', 
            'weight': 'normal',
            'slant': 'roman', 
            'underline': False, 
            'overstrike': False
        }

        self.font = lambda size: Font(family=fontConfig["family"], size=size, weight=fontConfig["weight"], slant=fontConfig["slant"], underline=fontConfig["underline"], overstrike=fontConfig["overstrike"])

        self.canvas = Canvas(master=self.window, width=128, height=128, highlightthickness=0, bg="#8a899e")

        self.frameImages = tuple([PIL.ImageTk.PhotoImage(PIL.Image.open(f"assets/images/frame/{image}.png").resize((128, 128), 3)) for image in ["up", "diagonal-up", "forward", "diagonal-down", "down", "not-determinable"]])
        self.frame = self.canvas.create_image(0, 0, image="", anchor=NW)

        self.baseImages = tuple([PIL.ImageTk.PhotoImage(PIL.Image.open(f"assets/images/base/{image}.png").resize((128, 128), 3)) for image in ["low", "normal", "high"]])
        self.base = self.canvas.create_image(0, 0, image="", anchor=NW)

        self.arrowImages = tuple([PIL.ImageTk.PhotoImage(PIL.Image.open(f"assets/images/arrow/{image}.png").resize((128, 128), 3)) for image in ["straight-up", "up", "diagonal-up", "forward", "diagonal-down", "down", "straight-down", "not-determinable"]])
        self.arrow = self.canvas.create_image(0, 0, image="", anchor=NW)

        self.glucoseLabel = self.canvas.create_text(64, 62, font=self.font(20))
        self.updateGlucose()

        self.showWindow()

    def windowChanged(self):
        screens = screeninfo.get_monitors()
        screens.sort()

        PRIMARY = "primary"

        screenDict = {}
        for index, monitor in enumerate(screens):
            exec(f'{"screenDict[PRIMARY]" if monitor.is_primary else "screenDict[str(index)]"} = monitor')

        if len(screenDict.keys()) == 1:
            displayScreen = screenDict["primary"]
        elif tuple(screenDict.keys())[0] == "primary":
            displayScreen = screenDict["1"]
        elif tuple(screenDict.keys())[-1] == "primary":
            displayScreen = screenDict[str(len(screenDict)-1)]
        else:
            displayScreen = screenDict[str(tuple(screenDict.keys()).index("primary")+1)]

        self.window.wm_geometry("+%i+%i" % (displayScreen.x + 80, displayScreen.y + 80))  # + (80/1080)*displayScreen.height, + (80/1080)*displayScreen.height

    def hideWindow(self, event=None):
        if self.visible:
            self.visible = False
            self.canvas.pack_forget()
            
    def showWindow(self, event=None):
        self.visible = True
        self.canvas.pack()
        
    def updateGui(self, *elements):
        for element in elements:
            self.guiMap[element]()

    def updateGlucose(self):
        glucose = self.dexcom.get_current_glucose_reading()
        updateMessage = "Time updated"
        scheduleDialog = "Next update"
        updateTag = UPDATE

        try:
            self.data = {
                "mmol/L": glucose.mmol_l, 
                "trendNumber": glucose.trend, 
                "trendDescription": glucose.trend_description, 
                "trendArrow": glucose.trend_arrow,
                "state": min(int(((glucose.mmol_l - 4.0) / 8.8) + 1), 2),
                "lastUpdated": glucose.time
            }
        except:
            self.data["lastUpdated"] += datetime.timedelta(minutes=1)
            updateMessage = "Data recieved \"NoneType\""
            scheduleDialog = "Retrying"
            updateTag = WARNING

        if (nextUpdate:=(((self.data["lastUpdated"] + datetime.timedelta(minutes=5)) - datetime.datetime.now()).seconds + 1)) < 300:
            self.updateGui("base", "frame", "arrow", "textColor", "text")

            try:
                self.RPC.update(state=(stateStr:=("Low", "Normal", "High")[self.data["state"]]), details=f"{self.data['mmol/L']} {(self.data['trendArrow'])} mmol/L", start=(timeNow:=int(datetime.datetime.now().timestamp())), end=(nextUpdate + timeNow), large_text="CGD", large_image="logocgd", small_text=stateStr, small_image=stateStr.lower())
            except:
                pass

            self.window.after(nextUpdate*1000, self.updateGlucose)
            print(f"{updateTag} {updateMessage}! {scheduleDialog} in: {nextUpdate}s ({nextUpdate*1000}ms)")
        else:
            self.window.after(5000, self.updateGlucose)
            print("[!] Time not updated yet! Retrying in 5s")

    def closeWindow(self, event):
        self.window.destroy()


def loadFont(fontPath):
    file = ctypes.byref(ctypes.create_unicode_buffer(fontPath))

    flags = (FR_PRIVATE:=0x10)

    ctypes.windll.gdi32.AddFontResourceExW(file, flags, 0)


def main():
    global applicationObject

    root = Tk()

    applicationObject = Overlay(root)

    root.mainloop()


if __name__ == "__main__":
    # Ensure all necessary files are present
    integrity.verify_project()

    # Load credentials
    credentials.read()
    credentials.control_defaults()

    # Start application
    main()
