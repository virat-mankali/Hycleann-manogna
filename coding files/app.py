from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['hyclone']
users_collection = db['users']
bins_collection = db['bins']

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            if '@driver.com' in email:
                return redirect(url_for('driver_dashboard'))
            elif '@supervisor.com' in email:
                return redirect(url_for('supervisor_dashboard'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']

        # Append role-specific email domain
        if role == 'driver':
            email = f"{name}@driver.com"
        elif role == 'supervisor':
            email = f"{name}@supervisor.com"
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into MongoDB
        users_collection.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': role
        })

        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/driver_dashboard')
def driver_dashboard():
    return render_template('driver.html')

@app.route('/supervisor_dashboard')
def supervisor_dashboard():
    return render_template('supervisor.html')

# API to get bin data for maps
@app.route('/bins', methods=['GET'])
def get_bins():
    bins = list(bins_collection.find({}, {'_id': 0, 'bin_name': 1, 'percentage': 1, 'lat': 1, 'lng': 1}))
    return jsonify(bins)

if __name__ == '__main__':
    app.run(debug=True)
