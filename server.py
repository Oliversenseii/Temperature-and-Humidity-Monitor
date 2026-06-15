from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

app = Flask(__name__)

SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/log", methods=["POST"])
def log_reading():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    temp = data.get("temperature")
    humid = data.get("humidity")
    alert = data.get("alert", False)

    if temp is None or humid is None:
        return jsonify({"error": "Missing fields"}), 400

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    supabase.table("readings").insert({
        "temperature": temp,
        "humidity": humid,
        "alert": alert,
        "timestamp": ts
    }).execute()

    print(f"[{ts}] Temp: {temp}C  Humidity: {humid}%  Alert: {alert}")
    return jsonify({"status": "saved", "timestamp": ts}), 200


@app.route("/readings", methods=["GET"])
def get_readings():
    limit = int(request.args.get("limit", 50))
    result = supabase.table("readings").select("*").order("id", desc=True).limit(limit).execute()
    return jsonify(result.data), 200


@app.route("/readings/latest", methods=["GET"])
def get_latest():
    result = supabase.table("readings").select("*").order("id", desc=True).limit(1).execute()
    if result.data:
        return jsonify(result.data[0]), 200
    return jsonify({"error": "No data yet"}), 404


@app.route("/readings/alerts", methods=["GET"])
def get_alerts():
    result = supabase.table("readings").select("*").eq("alert", True).order("id", desc=True).execute()
    return jsonify(result.data), 200


@app.route("/readings/stats", methods=["GET"])
def get_stats():
    result = supabase.table("readings").select("temperature, humidity, alert").execute()
    rows = result.data

    if not rows:
        return jsonify({"error": "No data yet"}), 404

    temps = [r["temperature"] for r in rows]
    humids = [r["humidity"] for r in rows]
    alerts = [r["alert"] for r in rows]

    return jsonify({
        "total_readings": len(rows),
        "avg_temp": round(sum(temps) / len(temps), 2),
        "max_temp": round(max(temps), 2),
        "min_temp": round(min(temps), 2),
        "avg_humidity": round(sum(humids) / len(humids), 2),
        "total_alerts": sum(1 for a in alerts if a)
    }), 200


@app.route("/readings/delete", methods=["DELETE"])
def delete_all():
    supabase.table("readings").delete().neq("id", 0).execute()
    return jsonify({"status": "all records deleted"}), 200


if __name__ == "__main__":
    print("Server running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
