import tkinter as tkr
from PIL import ImageGrab
import keyboard
import random
import time
import winsound

# ------------------------
# HUD
# ------------------------
root = tkr.Tk()
root.geometry("+0+0")
root.overrideredirect(True)
root.config(bg="black")
root.attributes("-transparentcolor", "black")
root.wm_attributes("-topmost", True)
root.resizable(0, 0)

# Timer Label
timer_display = tkr.Label(root, font=('Trebuchet MS', 30, 'bold'), bg='black')
timer_display.pack(anchor='w')

# Site Label
site_label = tkr.Label(root, font=('Trebuchet MS', 16), fg='white', bg='black', text="Site: -")
site_label.pack(anchor='w')

# ------------------------
# GLOBAL
# ------------------------
seconds = 41
running = False
last_spike_time = 0  # cooldown timestamp

# ------------------------
# SESLER
# ------------------------
def spike_sound():
    winsound.Beep(800,120)
    winsound.Beep(1000,120)

def explode_sound():
    winsound.Beep(400,300)
    winsound.Beep(300,400)

# ------------------------
# PATLAMA EFEKTİ
# ------------------------
def explosion_flash():
    flash = tkr.Toplevel()
    flash.attributes("-fullscreen", True)
    flash.attributes("-topmost", True)
    flash.config(bg="red")
    flash.attributes("-alpha", 0.7)
    flash.after(200, flash.destroy)

def shake():
    x = root.winfo_x()
    y = root.winfo_y()
    for _ in range(20):
        dx = random.randint(-15,15)
        dy = random.randint(-10,10)
        root.geometry(f"+{x+dx}+{y+dy}")
        root.update()
        time.sleep(0.02)
    root.geometry(f"+{x}+{y}")

# ------------------------
# HUD TEMİZLEME
# ------------------------
def hide_hud():
    timer_display.config(text="")
    site_label.config(text="Site: -")

# ------------------------
# TIMER
# ------------------------
def start_timer(site_name):
    global running
    running = True
    site_label.config(text=f"Site: {site_name}")
    spike_sound()
    # 3 saniye "Spike Algılandı!" mesajı
    timer_display.config(text="SPIKE ALGILANDI!", fg="orange")
    root.after(3000, lambda: countdown(seconds))

def countdown(time_left):
    global running
    if running and time_left > 0:
        mins, secs = divmod(time_left, 60)
        # Renk değişimi
        if time_left > 10:
            color = 'green'
        elif 8 <= time_left <= 10:
            color = 'yellow'
        else:
            color = 'red'
        timer_display.config(text="{:02d}:{:02d}".format(mins, secs), fg=color)
        root.after(1000, countdown, time_left-1)
    else:
        if running:
            timer_display.config(text="SPIKE PATLADI", fg="red")
            explode_sound()
            explosion_flash()
            shake()
            running = False
            hide_hud()

# ------------------------
# SPIKE DETECTION + SITE ALGILAMA
# ------------------------
def search_color():
    global running, last_spike_time
    current_time = time.time()
    # Spike cooldown 2 saniye
    cooldown = 2

    if running:
        root.after(10, search_color)
        return

    if current_time - last_spike_time < cooldown:
        root.after(10, search_color)
        return

    # Spike detection bölgesi
    area = (931, 26, 973, 66)
    screenshot = ImageGrab.grab(bbox=area)
    detected = False
    for x in range(screenshot.width):
        for y in range(screenshot.height):
            pixel = screenshot.getpixel((x, y))
            if pixel == (230, 0, 0) or pixel == (170, 0, 0):
                detected = True
                # Site tespiti: Sol=A, Ort=B, Sağ=C
                if x < screenshot.width // 3:
                    site = "A"
                elif x < 2 * screenshot.width // 3:
                    site = "B"
                else:
                    site = "C"
                print(f"Detected bomb plant at site {site}!")
                last_spike_time = current_time
                start_timer(site)
                break
        if detected:
            break

    root.after(10, search_color)

# ------------------------
# HOTKEYLER
# ------------------------
keyboard.add_hotkey("F8", hide_hud)

# ------------------------
# BAŞLAT
# ------------------------
root.after(10, search_color)
root.mainloop()