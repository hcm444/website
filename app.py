from flask import Flask, render_template
import sqlite3
import datetime
app = Flask(__name__)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address,app=app)


def get_latest_data(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute("""
        SELECT f1.* FROM flights f1
        LEFT JOIN flights f2
        ON f1.icao24 = f2.icao24 AND f1.timestamp < f2.timestamp
        WHERE f2.timestamp IS NULL AND f1.timestamp = (
            SELECT MAX(timestamp) FROM flights
        )
    """)
    latest_data = c.fetchall()
    conn.close()
    return latest_data

@app.route('/belarus')
@limiter.limit("5 per minute")
def belarus_index():
    latest_data = get_latest_data('databases/db1.sqlite3')
    if len(latest_data) == 0:
        latest_time = "No data available"
    else:
        latest_time = datetime.datetime.fromtimestamp(latest_data[0][-1]).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('BLR.html', latest_data=latest_data, latest_time=latest_time)

@app.route('/ukraine')
@limiter.limit("5 per minute")
def ukraine_index():
    latest_data = get_latest_data('databases/db2.sqlite3')
    if len(latest_data) == 0:
        latest_time = "No data available"
    else:
        latest_time = datetime.datetime.fromtimestamp(latest_data[0][-1]).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('UKR.html', latest_data=latest_data, latest_time=latest_time)

@app.route('/crow')
@limiter.limit("5 per minute")
def crow_index():
    latest_data = get_latest_data('databases/db.sqlite3')
    if len(latest_data) == 0:
        latest_time = "No data available"
    else:
        latest_time = datetime.datetime.fromtimestamp(latest_data[0][-1]).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('CROW.html', latest_data=latest_data, latest_time=latest_time)

@app.route('/blog')
@limiter.limit("5 per minute")
def new_page():
    # Add any necessary logic here
    return render_template('blog.html')

if __name__ == '__main__':
    app.run(debug=True)