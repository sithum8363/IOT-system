# MQTT MySQL IoT Monitor

Python Tkinter desktop app for monitoring ESP32/IoT devices over MQTT, storing received MQTT messages in MySQL, and showing device MAC/IP/status data in a GUI.

## Features

- Starts a local Mosquitto MQTT broker with TLS on port `8883`
- Connects to MQTT with `paho-mqtt`
- Subscribes to MQTT topics and stores messages in MySQL
- Tracks ESP32 board name, MAC address, IP address, and online/offline status
- Saves device state to local JSON files
- Provides a Tkinter GUI for start/stop, publishing messages, table selection, table creation, logs, and reset

## Main Files

- `gui.py` - Tkinter user interface and app entry point
- `main.py` - MQTT, MySQL, device tracking, and file logic
- `requirements.txt` - Python dependencies
- `runfile.bat` - starts Mosquitto with `text2.conf`
- `text2.conf` - Mosquitto TLS listener configuration
- `.env.example` - environment variable template
- `.gitignore` - prevents local secrets/runtime files from being uploaded

## What To Change On Another Machine

Copy `.env.example` to `.env`, then edit these values:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name

MQTT_HOST=localhost
MQTT_PORT=8883
MOSQUITTO_SERVICE=mosquitto

CA_CERT=ca.crt
BAT_FILE=runfile.bat
```

Also check these machine-specific items:

- Mosquitto install path: `runfile.bat` uses `mosquitto` from PATH first, then tries `C:\Program Files\mosquitto\mosquitto.exe`. If Mosquitto is installed somewhere else, edit `runfile.bat`.
- TLS files: place `ca.crt`, `server.crt`, and `server.key` in the project folder, or update `text2.conf` and `CA_CERT`.
- Database: create the MySQL database named in `DB_NAME` before running the app.
- Broker host: if the MQTT broker runs on another PC, set `MQTT_HOST` to that PC's IP address or hostname.
- ESP32 firmware: make sure devices publish to the same broker host/port and use compatible TLS certificates.

Do not upload `.env`, `*.key`, `*.crt`, `mysql-init.txt`, or the generated `devices*.json` files to GitHub.

## Requirements

- Windows
- Python 3.10 or newer
- MySQL Server
- Mosquitto MQTT broker
- ESP32 or other MQTT devices publishing to the expected topics

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create your local `.env` file:

```powershell
copy .env.example .env
notepad .env
```

Create the MySQL database and default table:

```sql
CREATE DATABASE your_database_name;
USE your_database_name;

CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100),
    value VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Run the app:

```powershell
python gui.py
```

Click `Start MQTT` in the GUI to start the broker and connect the MQTT client.

## MQTT Topics

The code listens to all topics, with special handling for:

- `factory/<board>/mac` - registers or updates a device
- `factory/<board>/status` - updates online/offline status
- other `factory/<board>/...` messages - refresh the board's last-seen time

Example MAC payload:

```json
{
  "board": "esp32_1",
  "mac": "AA:BB:CC:DD:EE:FF",
  "ip": "192.168.1.50",
  "status": "Online"
}
```

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

The `.gitignore` file is set up to exclude local passwords, private keys, certificates, runtime JSON files, Python cache files, and virtual environments.

## Security Notes

`text2.conf` currently has `allow_anonymous true`, which is convenient for local testing but not recommended for production. For a real deployment, add Mosquitto username/password authentication, firewall rules, and device-specific certificates.
