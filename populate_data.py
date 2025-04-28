import sqlite3
import random

# Connect to the database
conn = sqlite3.connect("pharmacy.db")
c = conn.cursor()

# ---------- Step 1: Clear old data ----------
c.execute("DELETE FROM availability")
c.execute("DELETE FROM medicine")
c.execute("DELETE FROM pharmacy")
conn.commit()

# ---------- Step 2: Insert Pharmacies ----------
pharmacies = [
    ("HealthFirst", "Spencer Plaza, Anna Salai, Chennai 600002", "healthfirst@example.com", "9876543210", "Spencer Plaza, Anna Salai"),
    ("WellCare Pharmacy", "Phoenix Marketcity, Velachery Road, Chennai 600042", "wellcare@example.com", "8765432109", "Phoenix Marketcity, Velachery"),
    ("CityMed", "Express Avenue Mall, Whites Road, Royapettah, Chennai 600014", "citymed@example.com", "7654321098", "Express Avenue, Royapettah"),
    ("MediQuick", "Vijaya Forum Mall, Arcot Road, Vadapalani, Chennai 600026", "mediquick@example.com", "6543210987", "nexus vijaya forum mall"),
    ("PharmaHub", "Apollo Hospital, Greams Road, Thousand Lights, Chennai 600006", "pharmahub@example.com", "5432109876", "apollo hospital thousand lights"),
    ("TrustCare", "Adyar Ananda Bhavan, LB Road, Adyar, Chennai 600020", "trustcare@example.com", "4321098765", "a2b lb road adyar"),
    ("GreenLeaf Pharmacy", "Saravana Stores, Ranganathan Street, T Nagar, Chennai 600017", "greenleaf@example.com", "3210987654", "Saravana Stores, T Nagar"),
    ("Apollo Express", "VR Chennai Mall, Jawaharlal Nehru Road, Anna Nagar, Chennai 600040", "apolloexpress@example.com", "2109876543", "VR Mall, Anna Nagar"),
    ("LifeLine", "Marina Mall,Old Mahabalipuram Road, Egattur, Tamil Nadu 603103", "lifeline@example.com", "1098765432", "marina mall egattur"),
    ("MediPoint", "VIT Chennai,Kelambakkam - Vandalur Rd, Rajan Nagar, Chennai, Tamil Nadu 600127", "medipoint@example.com", "9988776655", "VIT Chennai")
]

c.executemany("INSERT INTO pharmacy (name, address, email, mobile, location) VALUES (?, ?, ?, ?, ?)", pharmacies)
conn.commit()

# ---------- Step 3: Insert Medicines ----------
medicines = [
    ("Paracetamol 500mg", 12.0, "2026-01-01", 300),
    ("Azithromycin 250mg", 25.0, "2025-11-15", 200),
    ("Cetirizine 10mg", 10.0, "2026-04-20", 250),
    ("Multivitamin Syrup", 30.0, "2026-02-10", 150),
    ("Ibuprofen 400mg", 20.0, "2025-10-10", 180),
    ("ORS Sachet", 5.0, "2025-09-01", 500),
    ("Amoxicillin 500mg", 18.0, "2026-03-30", 220),
    ("Antacid Tablet", 15.0, "2026-05-15", 275),
    ("Cough Syrup", 22.0, "2025-12-25", 130),
    ("Vitamin D3 Capsule", 35.0, "2026-06-10", 160)
]

c.executemany("INSERT INTO medicine (name, price, expiry_date, quantity) VALUES (?, ?, ?, ?)", medicines)
conn.commit()

# ---------- Step 4: Insert Availability ----------
# Get all pharmacy IDs and medicine IDs
c.execute("SELECT pharmacy_id FROM pharmacy")
pharmacy_ids = [row[0] for row in c.fetchall()]

c.execute("SELECT medicine_id FROM medicine")
medicine_ids = [row[0] for row in c.fetchall()]

# Randomly assign medicines to pharmacies (many-to-many)
availability_data = []
for pharmacy_id in pharmacy_ids:
    available_meds = random.sample(medicine_ids, k=random.randint(3, 6))  # 3 to 6 meds per pharmacy
    for med_id in available_meds:
        availability_data.append((pharmacy_id, med_id))

c.executemany("INSERT INTO availability (pharmacy_id, medicine_id) VALUES (?, ?)", availability_data)
conn.commit()

print("✅ Data populated successfully.")
conn.close()
