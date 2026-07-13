import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import main

# ==========================
# LINK TO MAIN
# ==========================
main.tk = tk
main.messagebox = messagebox

root = tk.Tk()
root.title("MQTT + MySQL IoT Monitor")
root.geometry("1200x700")

# ==========================
# TOP CONTROL BUTTONS
# ==========================
control_frame = tk.Frame(root)
control_frame.pack(pady=15)

tk.Button(
    control_frame,
    text="▶ Start MQTT",
    bg="green",
    fg="white",
    font=("Arial", 10, "bold"),
    command=main.start_mqtt
).pack(side=tk.LEFT, padx=10)

tk.Button(
    control_frame,
    text="⏹ Stop MQTT",
    bg="red",
    fg="white",
    font=("Arial", 10, "bold"),
    command=main.stop_mqtt
).pack(side=tk.LEFT, padx=10)

# ==========================
# PUBLISH SECTION
# ==========================
publish_frame = tk.LabelFrame(
    root,
    text="Send Data (Publish) and get MAC adders ",
    padx=10,
    pady=10
)
publish_frame.pack(pady=10, fill="x", padx=10)

tk.Label(publish_frame, text="Topic:").grid(row=0, column=0)

main.topic_entry = tk.Entry(publish_frame, width=50)
main.topic_entry.grid(row=0, column=1, padx=5)
main.topic_entry.insert(0, "all ")

tk.Label(publish_frame, text="Payload:").grid(row=1, column=0)

main.payload_entry = tk.Entry(publish_frame, width=50)
main.payload_entry.grid(row=1, column=1, padx=5)
main.payload_entry.insert(0, "GETMAC")

tk.Label(publish_frame, text="new table name").grid(row=0, column=2)

main.dbenter= tk.Entry(publish_frame, width=50)
main.dbenter.grid(row=0, column=3, padx=5)
main.dbenter.insert(0, "---")

tk.Label(publish_frame, text="select table ").grid(
    row=0,
    column=4,
    padx=3,
    pady=3
)
topic_var = tk.StringVar()

main.topic_combo = ttk.Combobox(
    publish_frame,
    values=main.databases,
    state="readonly",
    width=30)

main.topic_combo.grid(row=0,column=5,padx=2, pady=2)
main.topic_combo.current(0)

tk.Button(
    publish_frame,
    text="select_db",
    bg="yellow",
    fg="black",
    command=main.select_db
).grid(row=2, column=5, pady=10)
tk.Button(
    publish_frame,
    text="create the table",
    bg="yellow",
    fg="black",
    command=main.create_db
).grid(row=2, column=3, pady=10)

tk.Button(
    publish_frame,
    text="Send Message",
    bg="blue",
    fg="white",
    command=main.send_message
).grid(row=2, column=1, pady=10)

# ==========================
# MAIN AREA
# ==========================
content_frame = tk.Frame(root)
content_frame.pack(fill="both", expand=True, padx=10, pady=5)

# ==========================
# DEVICE TABLE
# ==========================
device_frame = tk.LabelFrame(
    content_frame,
    text="Connected ESP32 Devices"
)
device_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)

device_columns = (
    "Board Name",
    "MAC Address",
    "IP"
)

main.device_table = ttk.Treeview(
    device_frame,
    columns=device_columns,
    show="headings",
    height=20
)

main.device_table.heading(
    "Board Name",
    text="Board Name"
)

main.device_table.heading(
    "MAC Address",
    text="MAC Address"
)

main.device_table.heading(
    "IP",
    text="IP Address"
)

main.device_table.column(
    "Board Name",
    width=120
)

main.device_table.column(
    "MAC Address",
    width=150
)

main.device_table.column(
    "IP",
    width=120
)

device_scroll = ttk.Scrollbar(
    device_frame,
    orient="vertical",
    command=main.device_table.yview
)

main.device_table.configure(
    yscrollcommand=device_scroll.set
)

main.device_table.pack(
    side=tk.LEFT,
    fill="both",
    expand=True
)

device_scroll.pack(
    side=tk.RIGHT,
    fill="y"
)

# ==========================
# STATUS TABLE
# ==========================
status_frame = tk.LabelFrame(
    content_frame,
    text="Device Status"
)
status_frame.pack(side=tk.LEFT, fill="y", padx=5)

status_columns = (
    "Board",
    "Status"
)

main.status_table = ttk.Treeview(
    status_frame,
    columns=status_columns,
    show="headings",
    height=20
)

main.status_table.heading(
    "Board",
    text="Board"
)

main.status_table.heading(
    "Status",
    text="Status"
)

main.status_table.column(
    "Board",
    width=100
)

main.status_table.column(
    "Status",
    width=80
)

main.status_table.pack(
    fill="both",
    expand=True
)
main.status_table.tag_configure(
    "online",
    foreground="green"
)

main.status_table.tag_configure(
    "offline",
    foreground="red"
)

# ==========================
# LOG WINDOW
# ==========================
log_frame = tk.LabelFrame(
    content_frame,
    text="Log Window"
)
log_frame.pack(
    side=tk.LEFT,
    fill="both",
    expand=True,
    padx=5
)

main.log_text = scrolledtext.ScrolledText(
    log_frame,
    width=40,
    height=25,
    state=tk.DISABLED,
    font=("Consolas", 10)
)

main.log_text.pack(
    fill="both",
    expand=True
)

# ==========================
# RESET BUTTON
# ==========================
tk.Button(
    root,
    text="Reset Devices",
    bg="red",
    fg="white",
    command=main.reset_devices
).pack(pady=10)

# ==========================
# STARTUP LOGS
# ==========================
main.log("=== MQTT + MySQL UI Ready ===")
main.log("Place 'ca.crt' in the same folder")
main.log("Click 'Start MQTT' to begin")

main.load_devices()

# ==========================
# CLOSE WINDOW
# ==========================
root.protocol(
    "WM_DELETE_WINDOW",
    lambda: (
        main.stop_mqtt(),
        root.destroy()
    )
)

root.mainloop()