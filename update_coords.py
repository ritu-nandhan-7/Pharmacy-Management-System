import sqlite3
import requests
import time

# Connect to DB
conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()

# Fetch pharmacies with no lat/lon
cursor.execute("SELECT pharmacy_id, location FROM pharmacy WHERE latitude IS NULL OR longitude IS NULL")
pharmacies = cursor.fetchall()

headers = {
    'User-Agent': 'PharmacyLocatorApp/1.0 (contact@example.com)'
}

for pharmacy_id, location in pharmacies:
    try:
        print(f"📍 Geocoding: {location}")
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
        response = requests.get(url, headers=headers).json()

        if response:
            lat = float(response[0]["lat"])
            lon = float(response[0]["lon"])
            cursor.execute("""
                UPDATE pharmacy
                SET latitude = ?, longitude = ?
                WHERE pharmacy_id = ?
            """, (lat, lon, pharmacy_id))
            print(f"✅ Updated → {lat}, {lon}")
        else:
            print(f"⚠ No result for: {location}")

        # Respect OpenStreetMap's rate limit
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error with '{location}': {e}")

conn.commit()
conn.close()
print("🎉 Done updating all coordinates!")
