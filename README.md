# 🌡️ Temperature & Humidity Monitor

A simple IoT monitoring system that reads temperature and humidity from a DHT22 sensor, sends the data over WiFi to a Flask backend, and stores it in a Supabase database for tracking and alerting.

---

## Architecture

```
DHT22 Sensor
     ↓
ESP8266 (Arduino)
     ↓ HTTP POST (JSON)
Flask Server (deployed / local)
     ↓
Supabase (PostgreSQL cloud database)
```

---

## Files

| File | Purpose |
|---|---|
| `temp_humidity_monitor.ino` | Upload to ESP8266 via Arduino IDE |
| `server.py` | Python Flask server |
| `.env` | Supabase credentials (never commit this!) |
| `requirements.txt` | Python dependencies |

---

## Supabase Setup

1. Go to [https://supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to **SQL Editor** and run this to create the table:

```sql
CREATE TABLE readings (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  temperature FLOAT        NOT NULL,
  humidity    FLOAT        NOT NULL,
  alert       BOOLEAN      NOT NULL DEFAULT FALSE,
  timestamp   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

4. Go to **Project Settings → API**
5. Copy your **Project URL** and **anon public key**
6. Paste them into `.env`:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

## Server Setup

```bash
pip install -r requirements.txt
python server.py
```

---

## Deploy Server (optional)

To make it accessible from anywhere, deploy `server.py` to:

- **Railway** — [https://railway.app](https://railway.app)
- **Render** — [https://render.com](https://render.com)
- **Fly.io** — [https://fly.io](https://fly.io)

Add your `.env` values as environment variables in the platform dashboard. Never upload your `.env` file to GitHub.

After deploying, update the Arduino code:
```cpp
const char* SERVER_URL = "https://your-deployed-server.railway.app/log";
```

---

## Arduino Setup

### Required Libraries
Install via Arduino IDE → Library Manager:
- `DHT sensor library` by Adafruit
- `Adafruit Unified Sensor` by Adafruit

ESP8266WiFi and ESP8266HTTPClient come with the ESP8266 board package.

### Board Manager URL
Add under Arduino IDE → Preferences → Additional Board URLs:
```
http://arduino.esp8266.com/stable/package_esp8266com_index.json
```

### Configure the Code
```cpp
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://YOUR_SERVER_URL/log";
```

---

## Wiring

```
DHT22
  VCC  → 3.3V
  GND  → GND
  DATA → D2

Green LED (+) → 220Ω → D5
Red LED   (+) → 220Ω → D6
Buzzer    (+) → D7
All       (-) → GND
```

---

## Alert Behavior

| Condition | Green LED | Red LED | Buzzer |
|---|---|---|---|
| Normal | ON | OFF | Silent |
| Temp > 35°C or Humidity > 80% | OFF | ON | Beep |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/log` | Save sensor reading |
| GET | `/readings` | Last 50 readings |
| GET | `/readings/latest` | Most recent reading |
| GET | `/readings/alerts` | Alert readings only |
| GET | `/readings/stats` | Avg / Max / Min stats |
| DELETE | `/readings/delete` | Clear all records |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Supabase connection error | Check `.env` values are correct |
| ESP8266 won't connect | Double-check WiFi credentials |
| Server response -1 | Check SERVER_URL in `.ino` |
| Sensor reads NaN | Check DHT22 wiring, use 3.3V not 5V |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
