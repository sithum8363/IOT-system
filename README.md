# MQTT MySQL IoT Monitor

Python Tkinter desktop app for monitoring ESP32/IoT devices over MQTT, storing received MQTT messages in MySQL, and showing device MAC/IP/status data in a GUI.

## Features


- Starts a local Mosquitto MQTT broker with TLS on port `8883`
- Connects to MQTT with `paho-mqtt`
- Subscribes to `#` (all topics) and stores every message in a MySQL table
- Tracks ESP32 board name, MAC address, IP address, and online/offline status
- Auto-marks a board **Offline** if it hasn't published anything for a configurable timeout (heartbeat thread)
- Lets you create a new MySQL table from the GUI and switch which table incoming messages are written to
- Saves device state to local JSON files (`devices1.json`, `devicesa_status.json` by default)
- Provides a Tkinter GUI for start/stop, publishing messages, table selection, table creation, logs, and reset

## Main Files

| File | Purpose |
|---|---|
| `gui.py` | Tkinter UI and app entry point |
| `main.py` | MQTT client, MySQL access, device tracking, heartbeat, and file logic |
| `requirements.txt` | Python dependencies |
| `runfile.bat` | Starts Mosquitto using `text2.conf` |
| `text2.conf` | Mosquitto TLS listener configuration |
| `.env.example` | Environment variable template — copy to `.env` |
| `.gitignore` | Keeps secrets/runtime files out of Git |

---

## 1. Prerequisites

- Windows 10/11
- Python 3.10+
- MySQL Server 8.x (or compatible)
- Mosquitto MQTT broker (installed, or portable binary on `PATH`)
- ESP32 or other MQTT devices publishing to the expected topics

### Put the required tools on your `PATH`

The app shells out to `mosquitto` (via `runfile.bat`) and to `mysql` if you use the CLI for setup, so both need to be reachable from a terminal.

1. Press **Win**, search **"Edit the system environment variables"** → **Environment Variables**.
2. Under **System variables**, select `Path` → **Edit** → **New**, and add:
   - Mosquitto install folder, e.g. `C:\Program Files\mosquitto`
   - MySQL `bin` folder, e.g. `C:\Program Files\MySQL\MySQL Server 8.0\bin`
   - Your Python install / `Scripts` folder if `python`/`pip` aren't already recognized
3. Open a **new** terminal (PATH changes don't apply to already-open windows) and confirm:
   ```powershell
   mosquitto -h
   mysql --version
   python --version
   ```
   If any command isn't found, the folder isn't on `PATH` yet or the app was installed elsewhere — fix the path and repeat.

If you don't want to touch the system `PATH`, you can instead set the full binary paths directly in `.env` (see `BAT_FILE` / `MOSQUITTO_SERVICE` below) and skip step 2.

---

## 2. MySQL setup

### Create the database, user, and table

Open a terminal and log in as root (or an admin account):

```powershell
mysql -u root -p
```

Then run:

```sql
-- 1. Create the database
CREATE DATABASE IF NOT EXISTS your_database_name;

-- 2. (Recommended) create a dedicated app user instead of using root
CREATE USER IF NOT EXISTS 'iot_app'@'localhost' IDENTIFIED BY 'a_strong_password';
GRANT ALL PRIVILEGES ON your_database_name.* TO 'iot_app'@'localhost';
FLUSH PRIVILEGES;

-- 3. Switch to the database
USE your_database_name;

-- 4. Create the default table the app writes to on first run
CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100),
    value VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Additional tables (matching the schema above) can also be created later directly from the GUI using the **"new table name"** field + **"create the table"** button — no need to go back to the MySQL CLI for that part.

### Point the app at MySQL

Whatever host/user/password/database you used above must match `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` in `.env` (see next section). If the app prints `DB Error: ...` on startup, it's almost always one of these four values, or the MySQL service not running (`services.msc` → `MySQL80` should be **Running**).

---

## 3. Environment variables — full `.env.example`

Copy the template and fill in your machine-specific values:

```powershell
copy .env.example .env
notepad .env
```

Updated `.env.example` (includes every variable `main.py` actually reads, including the JSON device-file paths and offline timeout, which the old template omitted):

```env
# ---- MySQL ----
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name

# ---- MQTT ----
MQTT_HOST=localhost
MQTT_PORT=8883
MOSQUITTO_SERVICE=mosquitto

# ---- TLS / Mosquitto startup ----
CA_CERT=ca.crt
BAT_FILE=runfile.bat

# ---- Device tracking files (relative to project folder, or use absolute paths) ----
DEVICE_FILE=devices1.json
DEVICE_STATUS_FILE=devicesa_status.json
```

Notes:
- All paths (`CA_CERT`, `BAT_FILE`, `DEVICE_FILE`, `DEVICE_STATUS_FILE`) can be relative (resolved against the project folder) or absolute — see `_project_path()` in `main.py`.
- `OFFLINE_TIMEOUT` (how many seconds of silence before a board is marked Offline) is currently hardcoded to `2` seconds in `main.py`. If you want it configurable per machine, add `OFFLINE_TIMEOUT=2` to `.env` and read it with `int(os.getenv("OFFLINE_TIMEOUT", "2"))` instead of the hardcoded value.
- Never commit the real `.env` — only `.env.example` should go into Git.

---

## 4. Mosquitto TLS configuration (`text2.conf`)

The broker is started by `runfile.bat`, which launches Mosquitto with `text2.conf`. On a new machine you'll typically need to:

1. **Generate/obtain TLS certificates** and place `ca.crt`, `server.crt`, `server.key` in the project folder (or wherever `text2.conf` points).
2. **Update the cert paths** in `text2.conf` to match where you placed them, e.g.:
   ```conf
   listener 8883
   cafile ca.crt
   certfile server.crt
   keyfile server.key
   require_certificate false

   allow_anonymous true
   ```
3. **Match the port** in `text2.conf` (`listener 8883`) with `MQTT_PORT` in `.env`.
4. **Confirm the Mosquitto service name** matches `MOSQUITTO_SERVICE` in `.env` — this is the name `main.py` uses when it runs `net stop <service>` on shutdown. Check the actual service name with:
   ```powershell
   sc query state= all | findstr mosquitto
   ```
5. **`runfile.bat` binary lookup** — it tries `mosquitto` on `PATH` first, then falls back to `C:\Program Files\mosquitto\mosquitto.exe`. If installed elsewhere, either add it to `PATH` (see section 1) or edit that fallback path directly in `runfile.bat`.

### Production hardening (optional but recommended)

`allow_anonymous true` is fine for local testing but should be turned off for anything beyond your desk:

```conf
allow_anonymous false
password_file passwd.txt
```

Generate the password file with:
```powershell
mosquitto_passwd -c passwd.txt your_mqtt_username
```

Then update your ESP32 firmware and any GUI publish calls to authenticate with that username/password, and restrict the listener with firewall rules so port `8883` isn't open to the internet.

---

## 5. Full setup order (new machine, from scratch)

```powershell
# 1. Clone / copy the project, then:
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt

# 2. Environment
copy .env.example .env
notepad .env        # fill in DB + MQTT + file paths

# 3. MySQL (see section 2 for full SQL)
mysql -u root -p
#   CREATE DATABASE ...; CREATE TABLE sensor_data ...;

# 4. TLS certs + text2.conf (see section 4)
#    place ca.crt / server.crt / server.key, update text2.conf paths

# 5. Run
python gui.py
```

Click **Start MQTT** in the GUI to launch the broker (via `runfile.bat`) and connect the MQTT client. Click **Stop MQTT** to disconnect and stop the Mosquitto service.

---

## MQTT Topics

The client subscribes to `#` (every topic), with special handling for:

- `factory/<board>/mac` — registers or updates a device (board, MAC, IP, status)
- `factory/<board>/status` — updates online/offline status
- other `factory/<board>/...` messages — refresh the board's last-seen time (used by the offline heartbeat)
- every message, regardless of topic, is also inserted into whichever MySQL table is currently selected in the GUI

Example MAC payload:

```json
{
  "board": "esp32_1",
  "mac": "AA:BB:CC:DD:EE:FF",
  "ip": "192.168.1.50",
  "status": "Online"
}
```

---

## GitHub Upload Checklist

Before uploading, check what Git will include:

```powershell
git status --short
```

Recommended first commit:

```powershell
git init
git add README.md .gitignore .env.example requirements.txt main.py gui.py runfile.bat text2.conf
git commit -m "Initial commit"
```

`.gitignore` should exclude: `.env`, `*.key`, `*.crt`, `passwd.txt`, `mysql-init.txt`, generated `devices*.json` files, `__pycache__/`, and your virtual environment folder (`.venv/`).

---

## Security Notes

- `text2.conf` ships with `allow_anonymous true` for local testing — switch to a password file + `allow_anonymous false` before any real deployment (section 4).
- Never commit `.env`, certificates, or the MySQL password.
- If you created a dedicated MySQL user (recommended, section 2), avoid using `root` in `.env` for day-to-day running.
- Restrict port `8883` at the firewall/router level if the broker doesn't need to be reachable outside your local network.
#   I O T - s y s t e m _ u o p 
 
 
