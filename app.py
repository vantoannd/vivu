from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from geopy.distance import geodesic
import config
import bcrypt
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Thư mục để lưu trữ tệp tải lên
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def get_db_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASS,
        port=config.DB_PORT
    )
    return conn

def load_locations():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, latitude, longitude, rating, category, image_data FROM locations')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    locations = []
    for row in rows:
        location = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'rating': row[5],
            'category': row[6],
            'image_data': row[7]
        }
        locations.append(location)
    return locations

@app.route('/')
def index():
    keyword = request.args.get('keyword', '')
    return render_template('index.html', keyword=keyword)

@app.route('/api/locations', methods=['GET'])
def get_locations():
    locations = load_locations()
    category = request.args.get('category')
    if category:
        locations = [loc for loc in locations if loc['category'] == category]
    return jsonify(locations)

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        rating = request.form['rating']
        category = request.form['category']
        
        # Xử lý dữ liệu hình ảnh
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        image = request.files['image']
        
        if image.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Đọc dữ liệu ảnh và lưu vào cơ sở dữ liệu
        image_data = image.read()
        
        new_location = Location(
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
            rating=rating,
            category=category,
            image_data=image_data
        )
        
        db.session.add(new_location)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('add_location.html')

@app.route('/route_suggestions')
def route_suggestions():
    locations = load_locations()
    return render_template('route_suggestions.html', locations=locations)

@app.route('/api/location/<int:location_id>', methods=['GET'])
def get_location(location_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, latitude, longitude, rating, category, image_data FROM locations WHERE id = %s', (location_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return jsonify({'error': 'Location not found'}), 404
    location = {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'latitude': row[3],
        'longitude': row[4],
        'rating': row[5],
        'category': row[6],
        'image_data': row[7]
    }
    return jsonify(location)

@app.route('/api/route_suggestions', methods=['GET'])
def get_route_suggestions():
    start_lat = request.args.get('start_lat')
    start_lng = request.args.get('start_lng')
    end_lat = request.args.get('end_lat')
    end_lng = request.args.get('end_lng')
    
    if not start_lat or not start_lng or not end_lat or not end_lng:
        return jsonify({'error': 'Start and end coordinates are required'}), 400
    
    start_location = {
        'latitude': float(start_lat),
        'longitude': float(start_lng)
    }
    
    end_location = {
        'latitude': float(end_lat),
        'longitude': float(end_lng)
    }
    
    route = [start_location, end_location]
    
    return jsonify(route)

@app.route('/api/location/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM locations WHERE id = %s', (location_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Đã xóa địa điểm thành công!'})

@app.route('/search_locations', methods=['GET'])
def search_locations():
    keyword = request.args.get('keyword')
    # Thực hiện tìm kiếm các địa điểm dựa trên từ khóa
    # Ví dụ: Tìm kiếm trong cơ sở dữ liệu hoặc danh sách các địa điểm đã có
    results = []
    if keyword:
        for location in load_locations():
            if keyword.lower() in location['name'].lower() or keyword.lower() in location['description'].lower():
                results.append(location)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
