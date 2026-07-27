<<<<<<< HEAD
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
=======
# ESP32 MQTT + MySQL SCADA Monitor

A Windows desktop SCADA/IoT monitoring application built with Python
Tkinter, Mosquitto MQTT over TLS, MySQL, and ESP32 devices.

The application can:

-   Start and stop the MQTT connection from the GUI.
-   Receive ESP32 messages from `factory/<board>/...` topics.
-   Store MQTT messages in a selected MySQL table.
-   Display ESP32 board name, MAC address, and IP address.
-   Show devices as Online or Offline.
-   Save device information in JSON files.
-   Publish commands to ESP32 devices from the GUI.
-   Create and select sensor-data tables.

## 1. Project files

Keep these files in the same project folder:

``` text
project-folder/
├── gui.py
├── main.py
├── .env
├── requirements.txt
├── runfile.bat
├── text2.conf
├── ca.crt
├── server.crt
├── server.key
├── devices1.json
└── devicesa_status.json
```

`ca.key`, `server.csr`, and `ca.srl` are certificate-generation files
and are not required by the Python GUI during normal operation. Keep
private keys secure and do not commit `.env`, `ca.key`, or `server.key`
to a public repository.

## 2. Requirements

Install:

-   Python 3.10 or newer
-   MySQL Server
-   Mosquitto MQTT Broker
-   ESP32 device firmware that publishes the expected MQTT topics

Check Python:

``` cmd
python --version
```

Check pip:

``` cmd
python -m pip --version
```

## 3. Create a virtual environment

Open Command Prompt in the project folder:

``` cmd
python -m venv venv
```

Activate it:

``` cmd
venv\Scripts\activate
```

## 4. Install Python packages

The application imports `mysql.connector`, so the recommended MySQL
package is `mysql-connector-python`.

Install the required packages with:

``` cmd
python -m pip install paho-mqtt mysql-connector-python python-dotenv
```

Alternatively, after correcting `requirements.txt` to use
`mysql-connector-python`, run:

``` cmd
python -m pip install -r requirements.txt
```

## 5. Create the MySQL database

Open MySQL:

``` cmd
mysql -u root -p
```

Create the database:

``` sql
CREATE DATABASE IF NOT EXISTS iotdb;
USE iotdb;
>>>>>>> bff10e62845c2bbf54c03578d85327a7f796ab11

CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100),
    value VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

<<<<<<< HEAD
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
=======
The MySQL password in `.env` must match the password configured for the
local MySQL `root` account.

## 6. Configure `.env`

Edit `.env` for the current computer. Example:

``` env
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=iotdb

CA_CERT=C:\path\to\project\ca.crt
BAT_FILE=C:\path\to\project\runfile.bat
```

Do not add spaces around `=`.

## 7. Configure Mosquitto TLS

Edit `text2.conf` so all certificate paths point to the actual project
folder:

``` conf
listener 8883
allow_anonymous true

cafile C:\path\to\project\ca.crt
certfile C:\path\to\project\server.crt
keyfile C:\path\to\project\server.key
```

Edit `runfile.bat` so the Mosquitto executable and configuration paths
are correct:

``` bat
@echo off
"C:\Program Files\mosquitto\mosquitto.exe" -c "C:\path\to\project\text2.conf" -v
pause
```

If Mosquitto is installed elsewhere, use its real installation path.

## 8. Check port 8883 before starting

Only one broker can listen on port 8883.

Check the port:

``` cmd
netstat -ano | findstr :8883
```

If a process is already listening, identify it:

``` cmd
tasklist | findstr PID_NUMBER
```

If an old Mosquitto process must be stopped, open Command Prompt as
Administrator and run:

``` cmd
taskkill /F /PID PID_NUMBER
```

Do not start a second Mosquitto instance while another broker is already
listening on port 8883.

## 9. Run the application

Activate the virtual environment if needed:

``` cmd
venv\Scripts\activate
```

Run:

``` cmd
python gui.py
```

Expected startup output includes:

``` text
Database connected
```

The GUI opens as **MQTT + MySQL IoT Monitor**.

Click **Start MQTT**. The application launches `runfile.bat`, loads the
CA certificate, connects to `localhost` on port `8883`, subscribes to
MQTT topics, and starts device status checking.

## 10. ESP32 MQTT topic format

The Python application expects topics similar to:

``` text
factory/esp32_1/mac
factory/esp32_1/status
factory/esp32_1/temperature
```

For MAC registration, the preferred JSON payload is:

``` json
{
  "board": "esp32_1",
  "mac": "00:70:07:2D:47:D8",
  "ip": "192.168.1.104",
>>>>>>> bff10e62845c2bbf54c03578d85327a7f796ab11
  "status": "Online"
}
```

<<<<<<< HEAD
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
=======
Publish it to:

``` text
factory/esp32_1/mac
```

For status:

``` text
Topic: factory/esp32_1/status
Payload: online
```

The current Python code uses an `OFFLINE_TIMEOUT` of 2 seconds.
Therefore, each ESP32 must publish a factory message more frequently
than every 2 seconds to remain Online. For normal Wi-Fi networks,
consider increasing the timeout to 10--30 seconds.

Example in `main.py`:

``` python
OFFLINE_TIMEOUT = 15
```

## 11. GUI controls

**Start MQTT** starts the broker command, connects the Python MQTT
client, and starts heartbeat checking.

**Stop MQTT** publishes `STOP`, disconnects the client, stops heartbeat
checking, and attempts to stop the Mosquitto Windows service.

**Send Message** publishes the entered payload to the entered MQTT
topic.

**Create the table** creates a MySQL sensor-data table using the entered
table name.

**Select DB** selects one of the listed MySQL tables as the destination
table for received MQTT messages.

**Reset Devices** clears both device JSON files and removes device rows
from the GUI.

## 12. Troubleshooting

### Port 8883 already in use

Error:

``` text
Only one usage of each socket address is normally permitted
```

Cause: another process is already listening on port 8883.

Run:

``` cmd
netstat -ano | findstr :8883
```

Then stop the duplicate process or avoid launching another broker.

### Certificate verification failed

Error:

``` text
CERTIFICATE_VERIFY_FAILED
```

Check that:

-   `CA_CERT` points to the correct `ca.crt`.
-   `server.crt` was signed by the CA represented by `ca.crt`.
-   The Mosquitto certificate paths are correct.
-   The hostname and certificate setup are suitable for the connection
    method.

The current application also calls `tls_insecure_set(True)`. This
disables hostname verification and is suitable only for controlled
development/testing. For production, use certificates with correct
hostname/IP identity and enable verification.

### MySQL access denied

Error:

``` text
Access denied for user 'root'@'localhost'
```

Check:

-   MySQL Server is running.
-   `DB_PASSWORD` in `.env` matches the MySQL account password.
-   `DB_NAME` exists.

### Unknown database

Create it:

``` sql
CREATE DATABASE iotdb;
```

### `ModuleNotFoundError: No module named 'mysql'`

Install:

``` cmd
python -m pip install mysql-connector-python
```

### Device immediately becomes Offline

The current timeout is only 2 seconds. Either publish heartbeat/status
messages more frequently or increase:

``` python
OFFLINE_TIMEOUT = 15
```

## 13. Recommended startup order

1.  Start MySQL Server.
2.  Check that port 8883 is free.
3.  Activate the Python virtual environment.
4.  Run `python gui.py`.
5.  Click **Start MQTT** once.
6.  Power on the ESP32 devices.
7.  Confirm incoming messages in the Log Window.
8.  Confirm devices appear in the device and status tables.

## 14. Security notes

This project currently allows anonymous MQTT clients and uses
development-oriented TLS settings. Before deployment:

-   Add MQTT username/password authentication or client certificates.
-   Disable anonymous MQTT access.
-   Use certificates with correct hostname/IP identity.
-   Do not commit `.env` or private key files to GitHub.
-   Use a dedicated MySQL application user instead of `root`.
-   Restrict broker and database network access with firewall rules.

## 15. Main command summary

``` cmd
python -m venv venv
venv\Scripts\activate
python -m pip install paho-mqtt mysql-connector-python python-dotenv
python gui.py
```
>>>>>>> bff10e62845c2bbf54c03578d85327a7f796ab11
