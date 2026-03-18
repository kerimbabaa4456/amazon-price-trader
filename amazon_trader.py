import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import time
import threading
import winsound

DATA_FILE = "data.json"
CHECK_INTERVAL = 10800  # 3 saat

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -------- DATA -------- #
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------- PRICE -------- #
def get_price(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        price = soup.find("span", {"class": "a-offscreen"})
        return price.text.strip() if price else None
    except:
        return None

# -------- NOTIFY -------- #
def notify(msg):
    def popup():
        messagebox.showinfo("Price Alert", msg)
    root.after(0, popup)
    winsound.Beep(1000, 500)

# -------- LOG -------- #
def log(msg):
    output_text.insert(tk.END, msg + "\n")
    output_text.see(tk.END)

# -------- UI FUNCTIONS -------- #
def add_url():
    url = entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Enter a link")
        return
    data = load_data()
    if url not in data:
        target_price = simpledialog.askstring("Target Price", "Enter target price for this product:")
        data[url] = {"last_price": "", "target_price": target_price}
        save_data(data)
    listbox.insert(tk.END, url)
    entry.delete(0, tk.END)

def remove_url():
    selected = listbox.curselection()
    if not selected:
        return
    url = listbox.get(selected)
    listbox.delete(selected)
    data = load_data()
    if url in data:
        del data[url]
        save_data(data)

def load_urls():
    data = load_data()
    for url in data.keys():
        listbox.insert(tk.END, url)

# -------- TRACK -------- #
def start_tracking():
    urls = listbox.get(0, tk.END)
    if not urls:
        messagebox.showerror("Error", "Add at least 1 link")
        return
    def run():
        status_label.config(text="Running...")
        while True:
            data = load_data()
            for url in urls:
                price_text = get_price(url)
                if price_text:
                    log(f"{url} -> {price_text}")
                    # convert price to float
                    price = float(price_text.replace("$","").replace(",",""))
                    old_price = data[url]["last_price"]
                    target_price = float(data[url]["target_price"].replace("$","").replace(",",""))
                    if old_price and old_price != price:
                        log("Price changed!")
                    if price <= target_price:
                        notify(f"Target reached!\n{price}")
                    data[url]["last_price"] = price
                    save_data(data)
                else:
                    log(f"{url} -> failed")
            log("---- Waiting 3 hours ----\n")
            time.sleep(CHECK_INTERVAL)
    threading.Thread(target=run, daemon=True).start()

# -------- GUI -------- #
root = tk.Tk()
root.title("Amazon Trader PRO")
root.geometry("750x600")
root.configure(bg="#1e1e1e")

tk.Label(root, text="Amazon Trader PRO", fg="white", bg="#1e1e1e", font=("Arial",16)).pack(pady=10)

entry = tk.Entry(root, width=90)
entry.pack(pady=5)

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="Add", width=10, command=add_url).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Remove", width=10, command=remove_url).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Start", width=10, command=start_tracking).grid(row=0, column=2, padx=5)

listbox = tk.Listbox(root, width=95, height=8)
listbox.pack(pady=10)

status_label = tk.Label(root, text="Waiting...", fg="white", bg="#1e1e1e")
status_label.pack()

output_text = tk.Text(root, height=20)
output_text.pack(pady=10)

load_urls()
root.mainloop()