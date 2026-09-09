# import os
from flask import Flask, jsonify, request
from services.database import DatabasePSQL

app = Flask(__name__)
db_psql = DatabasePSQL()

@app.route('/')
def index():
    return jsonify({"status": "API Flusk is ONLINE!"})

@app.route('/db-status')
def db_status():
    try:
        conn = db_psql.get_db_conn()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({
            "status" : "Success connection with PostgreSQL!",
            "postgres_version": db_version[0]
        })
    except Exception as e:
        return jsonify({"error": str(e)}, 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
