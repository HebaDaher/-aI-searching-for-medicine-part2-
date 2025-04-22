from pyswip import Prolog
from flask import Flask, request, jsonify, render_template
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
prolog = Prolog()
prolog.consult("med_knowledge.pl")

# Mock function to simulate buying medicine
def buy_medicine_online(medicine):
    stores = ['Amazon', 'HealthKart', 'LocalPharma']
    return {
        'medicine': medicine,
        'price': f"${random.randint(5, 20)}",
        'store': random.choice(stores),
        'link': f"https://lifepharmacy.com/search?q={medicine}"
    }

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptoms TEXT,
            medicine TEXT,
            score INTEGER,
            price TEXT,
            store TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    symptoms = request.form.getlist('symptoms')
    symptoms = [s.lower() for s in symptoms if s.strip()]
    
    if not symptoms:
        return jsonify({'message': 'Please provide at least one symptom'}), 400

    results = list(prolog.query(f"recommend_medicines({symptoms}, Medicine, Score)"))
    if not results:
        return jsonify({'message': 'No medicine found'}), 404

    sorted_results = sorted(results, key=lambda x: x['Score'], reverse=True)[:7]
    recommendations = []

    # Open DB connection
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()

    for res in sorted_results:
        med = res["Medicine"]
        score = res["Score"]
        purchase = buy_medicine_online(med)
        purchase["score"] = score
        recommendations.append(purchase)

        # Save to database
        c.execute('''
            INSERT INTO logs (symptoms, medicine, score, price, store, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            ", ".join(symptoms),
            med,
            score,
            purchase["price"],
            purchase["store"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    conn.close()

    return jsonify(recommendations)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
