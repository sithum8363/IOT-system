import paho.mqtt.client as mqtt
import mysql.connector
import ssl
import time
import os
import subprocess
import json
import threading
from dotenv import load_dotenv
load_dotenv()
# ====================== Database ======================
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = db.cursor()
    print("Database connected")
    cursor.execute("SHOW TABLES")
    databases = [table[0] for table in cursor.fetchall()]
    print(databases)
except Exception as e:
    print(f"DB Error: {e}")
    cursor = None

# ====================== Globals ======================
client  = None
running = False
log_text      = None
topic_entry   = None
payload_entry = None
messagebox    = None
tk            = None
device_table  = None
status_table  = None
device_name   = None
dbenter       =None
create_db     =None
select_db     =None
topic_combo = None
table_name="sensor_data"

ca_cert_path  =  os.getenv("CA_CERT")
BAT_FILE = os.getenv("BAT_FILE")
DEVICE_FILE   = "devices1.json"
DEVICE_s_FILE = "devicesa_status.json"

# How many seconds of silence before a device is marked Offline
OFFLINE_TIMEOUT = 2

# Tracks the last time each board sent ANY message  { board: epoch_float }
_last_seen: dict = {}

# Background timer handle
_heartbeat_timer = None





# ─────────────────────────── JSON helpers ────────────────────────────────────

def _read_devices(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []


def _write_devices(filepath, devices):
    try:
        with open(filepath, "w") as f:
            json.dump(devices, f, indent=4)
    except Exception as e:
        log(f"File write error ({filepath}): {e}")


def save_device(board, mac, IP, status):
    """Add a new device entry. Skips if MAC already exists."""
    devices = _read_devices(DEVICE_FILE)
    for d in devices:
        if d["mac"] == mac:
            return          # already registered – update path handles changes
    devices.append({
        "board":     board,
        "mac":       mac,
        "IP":        IP,
        "status":    status,
        "last_seen": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    _write_devices(DEVICE_FILE,   devices)
    _write_devices(DEVICE_s_FILE, devices)
    log(f"Device saved: {mac}")


def update_device_info_in_file(board, mac, IP, status):
    """Update IP, MAC and status for an existing board entry in both files."""
    for filepath in [DEVICE_FILE, DEVICE_s_FILE]:
        devices = _read_devices(filepath)
        for d in devices:
            if d["board"] == board:
                d["mac"]       = mac
                d["IP"]        = IP
                d["status"]    = status
                d["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
                break
        _write_devices(filepath, devices)


def update_device_status_in_file(board, status):
    """Persist a status-only change for an existing board entry."""
    for filepath in [DEVICE_FILE, DEVICE_s_FILE]:
        devices = _read_devices(filepath)
        for d in devices:
            if d["board"] == board:
                d["status"]    = status
                d["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
                break
        _write_devices(filepath, devices)


# ─────────────────────────── UI table helpers ────────────────────────────────
def load_databases():
    global databases

    cursor.execute("SHOW TABLES")
    databases = [table[0] for table in cursor.fetchall()]

    if topic_combo:
        topic_combo["values"] = databases

    return databases

def create_db():
    global dbenter
    db_name = dbenter.get()

    if db_name:
        cursor.execute( f"""
        CREATE TABLE IF NOT EXISTS `{db_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            topic VARCHAR(100),
            value VARCHAR(100),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.commit()
        load_databases()
        databases = [table[0] for table in cursor.fetchall()]
        print(databases)


def _status_label(raw: str) -> str:
    """Convert 'online'/'offline' to a display label with emoji."""
    mapping = {
        "online":  "🟢 Online",
        "offline": "🔴 Offline",
    }
    return mapping.get(raw.lower(), raw)
def _status_tag(label: str) -> str:
    """Return the tk tag name from a status label."""
    return "online" if "Online" in label else "offline"

def update_status(board, status):
    """Update the status_table row for *board*. Persists to disk."""
    if status_table is None:
        return
    label = _status_label(status)
    tag = "online" if "Online" in label else "offline"
    for item in status_table.get_children():
        if status_table.item(item)["values"][0] == board:
            status_table.item(item, values=(board, label), tags=(tag,))
            update_device_status_in_file(board, label)
            return
    status_table.insert("", "end", values=(board, label), tags=(tag,))
    update_device_status_in_file(board, label)


def _update_device_row(board, mac, IP, status):
    """
    Refresh a device_table row (board / mac / IP).
    Inserts a new row if the board is not yet listed.
    Also refreshes the status_table.
    """
    if device_table is None:
        return

    label = _status_label(status)
    tag = "online" if "Online" in label else "offline"
    # Update or insert in device_table
    found = False
    for item in device_table.get_children():
        values = device_table.item(item)["values"]
        if values[0] == board:                      # match by board name
            device_table.item(item, values=(board, mac, IP))
            found = True
            break
    if not found:
        device_table.insert("", "end", values=(board, mac, IP))

    # Update or insert in status_table
    if status_table is not None:
        status_found = False
        for item in status_table.get_children():
            if status_table.item(item)["values"][0] == board:
                status_table.item(item, values=(board, label), tags=(tag,))
                status_found = True
                break
        if not status_found:
            status_table.insert("", "end", values=(board, label), tags=(tag,))

    # Persist both info and status to files
    update_device_info_in_file(board, mac, IP, label)


def add_device(board, mac, IP, status):
    """Register or fully refresh a device (info + status)."""
    if not board or not mac:
        return
    save_device(board, mac, IP, status)   # no-op if already exists
    _update_device_row(board, mac, IP, status)


def load_devices():
    """Populate both tables from JSON files on startup. All start Offline."""
    global device_table
    if device_table is None:
        return
    devices = _read_devices(DEVICE_FILE)
    for device in devices:
        device_table.insert(
            "", "end",
            values=(device["board"], device["mac"], device["IP"])
        )
        if status_table:
            status_table.insert(
                "", "end",
                values=(device["board"], "🔴 Offline"),tags=("offline",)

            )

def select_db():
    global table_name,topic_combo
    table_name=topic_combo.get()
    print("Selected:", table_name)
    messagebox.showinfo("Selected Table", table_name)

# ─────────────────────────── Manual refresh ──────────────────────────────────

def refresh_devices():
    """
    Manual refresh button handler.
    Re-reads the JSON files and updates every row in both tables.
    Devices not heard from within OFFLINE_TIMEOUT seconds are marked Offline.
    """
    if device_table is None:
        log("⚠ Table not ready")
        return

    devices = _read_devices(DEVICE_FILE)
    now = time.time()

    for device in devices:
        board = device["board"]
        mac   = device["mac"]
        IP    = device["IP"]

        # Determine live status from last-seen tracker
        last = _last_seen.get(board, 0)
        status = "Online" if (now - last) < OFFLINE_TIMEOUT else "Offline"

        _update_device_row(board, mac, IP, status)

    log("🔄 Device list refreshed")


# ─────────────────────────── Heartbeat timer ─────────────────────────────────

def _heartbeat():
    """
    Runs every OFFLINE_TIMEOUT seconds in a background thread.
    Any board that has not published within OFFLINE_TIMEOUT seconds
    is automatically marked Offline in the UI and the JSON files.
    """
    global _heartbeat_timer
    if not running:
        return

    now = time.time()
    devices = _read_devices(DEVICE_FILE)

    for device in devices:
        board = device["board"]
        last  = _last_seen.get(board, 0)
        if (now - last) >= OFFLINE_TIMEOUT:
            current_label = ""
            if status_table:
                for item in status_table.get_children():
                    if status_table.item(item)["values"][0] == board:
                        current_label = str(status_table.item(item)["values"][1])
                        break
            if "Offline" not in current_label:
                update_status(board, "Offline")
                log(f"⏱ {board} timed out → 🔴 Offline")

    # Re-schedule
    _heartbeat_timer = threading.Timer(OFFLINE_TIMEOUT, _heartbeat)
    _heartbeat_timer.daemon = True
    _heartbeat_timer.start()


def _start_heartbeat():
    global _heartbeat_timer
    _heartbeat_timer = threading.Timer(OFFLINE_TIMEOUT, _heartbeat)
    _heartbeat_timer.daemon = True
    _heartbeat_timer.start()


def _stop_heartbeat():
    global _heartbeat_timer
    if _heartbeat_timer:
        _heartbeat_timer.cancel()
        _heartbeat_timer = None


# ─────────────────────────── MQTT callbacks ──────────────────────────────────

def on_message(client, userdata, msg):
    global table_name
    log(f"table_ name:{table_name}")
    try:
        value = msg.payload.decode()
        log(f"Received: {msg.topic} = {value}")

        # Save every message to DB
        if cursor:
            sql = f"INSERT INTO `{table_name}` (topic, value) VALUES (%s, %s)"
            cursor.execute(sql, (msg.topic, value))
            db.commit()
            log(f"💾 Saved to :{table_name} db")

        # ── factory/<board>/mac  →  full device registration / info update ──
        if "factory" in msg.topic and msg.topic.endswith("/mac"):
            board = mac = IP = status = None
            try:
                data   = json.loads(value)
                board  = data.get("board")
                mac    = data.get("mac")
                IP     = data.get("ip", "N/A")
                status = data.get("status", "Online")
            except json.JSONDecodeError:
                parts  = msg.topic.split("/")
                board  = parts[1] if len(parts) > 1 else "Unknown"
                mac    = value.strip()
                IP     = "N/A"
                status = "Online"

            if board and mac:
                _last_seen[board] = time.time()
                add_device(board, mac, IP, status)
                log(f"Device updated: {board} | {mac} | {IP} | {status}")

        # ── factory/<board>/status  →  Online / Offline update ──────────────
        elif "factory" in msg.topic and msg.topic.endswith("/status"):
            parts = msg.topic.split("/")
            board = parts[1] if len(parts) >= 3 else None
            if board:
                try:
                    data       = json.loads(value)
                    raw_status = str(data.get("status", value)).strip()
                except (json.JSONDecodeError, AttributeError):
                    raw_status = value.strip()

                if raw_status.lower() == "online":
                    _last_seen[board] = time.time()

                update_status(board, raw_status)
                log(f"Status update: {board} → {raw_status}")

        # ── Any other factory message keeps the board's last-seen fresh ──────
        elif msg.topic.startswith("factory/"):
            parts = msg.topic.split("/")
            if len(parts) >= 2:
                board = parts[1]
                _last_seen[board] = time.time()
                # If the board was Offline, flip it back Online automatically
                if status_table:
                    for item in status_table.get_children():
                        vals = status_table.item(item)["values"]
                        if vals[0] == board and "Offline" in str(vals[1]):
                            update_status(board, "Online")
                            log(f"↩ {board} is back → 🟢 Online")
                            break

    except Exception as e:
        log(f"on_message error: {e}")


def on_connect(client, userdata, flags, rc, properties=None):
    log(f"✅ Connected to MQTT! Code: {rc}")
    client.subscribe("#")
    client.subscribe("factory/#")


# ─────────────────────────── MQTT lifecycle ──────────────────────────────────

def configfile():
    subprocess.Popen(BAT_FILE)
    print("working conf")


def stop():
    subprocess.run(["net", "stop", "mosquitto"])
    print("stop")


def set_ca_cert_path(path):
    global ca_cert_path
    ca_cert_path = path
    log(f"CA Certificate set: {path}")


def get_ca_cert_path():
    return ca_cert_path


def start_mqtt():
    global client, running
    if running:
        return
    try:
        configfile()
        client = mqtt.Client()
        cert   = get_ca_cert_path()
        log(f"Loading CA cert: {cert}")
        client.tls_set(ca_certs=cert, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.tls_insecure_set(True)
        client.on_connect = on_connect
        client.on_message = on_message
        log("Connecting to broker...")
        client.connect("localhost", 8883, 60)
        running = True
        client.loop_start()
        _start_heartbeat()
        time.sleep(10)
        client.publish("all", "START")
        log("🚀 MQTT Started Successfully")
    except Exception as e:
        log(f"❌ Failed to start MQTT: {e}")
        if messagebox:
            messagebox.showerror("Connection Error", str(e))


def stop_mqtt():
    global client, running
    if client and running:
        try:
            client.publish("all", "STOP")
            client.loop_stop()
            client.disconnect()
            _stop_heartbeat()
            log("⏹ MQTT Stopped")
            stop()
        except Exception:
            pass
        running = False


# ─────────────────────────── Utilities ───────────────────────────────────────

def send_message():
    if not topic_entry or not payload_entry:
        return
    topic   = topic_entry.get().strip()
    payload = payload_entry.get().strip()
    if not topic or not payload:
        if messagebox:
            messagebox.showwarning("Warning", "Topic and Payload required!")
        return
    if client and running:
        try:
            client.publish(topic, payload)
            log(f"📤 Sent → {topic} = {payload}")
        except Exception as e:
            log(f"Send failed: {e}")
    else:
        if messagebox:
            messagebox.showwarning("Warning", "MQTT not running!")


def reset_devices():
    try:
        _write_devices(DEVICE_FILE,   [])
        _write_devices(DEVICE_s_FILE, [])
        if device_table:
            for item in device_table.get_children():
                device_table.delete(item)
        if status_table:
            for item in status_table.get_children():
                status_table.delete(item)
        _last_seen.clear()
        log("Devices list reset successfully")
    except Exception as e:
        log(f"Reset error: {e}")


def log(message):
    if log_text is None or tk is None:
        print(message)
        return

    def _write():
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)

    log_text.after(0, _write)