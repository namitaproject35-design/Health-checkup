from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

def init_db():
    conn = sqlite3.connect('database.db')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        symptoms TEXT,
        disease TEXT,
        precautions TEXT,
        advice TEXT
    )
    ''')

    conn.commit()
    conn.close()
app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

def validate_registration(fullname, email, phone, username, password, confirm_password):
    """Validate registration form data"""
    errors = []
    
    # Validate fullname
    if not fullname or len(fullname.strip()) < 2:
        errors.append('Full name must be at least 2 characters long.')
    
    # Validate email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        errors.append('Please enter a valid email address.')
    
    # Validate phone
    phone_digits = re.sub(r'\D', '', phone)
    if len(phone_digits) < 10:
        errors.append('Please enter a valid phone number (at least 10 digits).')
    
    # Validate username
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters long.')
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append('Username can only contain letters, numbers, and underscores.')
    
    # Validate password
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters long.')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain at least one number.')
    
    # Check password confirmation
    if password != confirm_password:
        errors.append('Passwords do not match.')
    
    return errors

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate input
        validation_errors = validate_registration(fullname, email, phone, username, password, confirm_password)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('register.html', 
                                   fullname=fullname, 
                                   email=email, 
                                   phone=phone, 
                                   username=username)

        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (fullname, email, phone, username, password) VALUES (?, ?, ?, ?, ?)',
                         (fullname, email, phone, username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                flash('This username is already taken. Please choose another.', 'error')
            elif 'email' in str(e):
                flash('This email is already registered. Please log in or use another email.', 'error')
            else:
                flash('Registration failed. Please try again.', 'error')
            return render_template('register.html',
                                   fullname=fullname, 
                                   email=email, 
                                   phone=phone, 
                                   username=username)
    
    return render_template('register.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # You can store or print
        print(name, email, message)

        flash("Message sent successfully!", "success")

    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

DISEASES = {
    'Common Cold': ['runny nose', 'stuffy nose', 'sneezing', 'sore throat', 'mild fever', 'cough'],
    'Flu (Influenza)': ['high fever', 'body aches', 'chills', 'fatigue', 'dry cough'],
    'Diabetes': ['frequent urination', 'increased thirst', 'fatigue', 'blurred vision', 'slow healing wounds'],
    'Hypertension (High Blood Pressure)': ['headache', 'dizziness', 'chest pain', 'shortness of breath'],
    'Asthma': ['shortness of breath', 'wheezing', 'chest tightness', 'coughing'],
    'COVID-19': ['fever', 'dry cough', 'loss of taste', 'loss of smell', 'breathing difficulty', 'fatigue'],
    'Dengue': ['high fever', 'severe headache', 'joint pain', 'muscle pain', 'skin rash', 'nausea'],
    'Malaria': ['fever with chills', 'sweating', 'headache', 'nausea', 'vomiting'],
    'Typhoid': ['prolonged fever', 'weakness', 'abdominal pain', 'loss of appetite', 'constipation', 'diarrhea'],
    'Tuberculosis (TB)': ['persistent cough', 'blood in sputum', 'chest pain', 'weight loss', 'night sweats'],
    'Migraine': ['severe headache', 'sensitivity to light', 'nausea', 'vomiting'],
    'Food Poisoning': ['nausea', 'vomiting', 'diarrhea', 'stomach cramps', 'fever'],
}

DESCRIPTIONS = {
    'Common Cold': 'A viral infection affecting the upper respiratory tract, usually mild and short-term.',
    'Flu (Influenza)': 'A more severe viral infection than cold, spreads quickly and may require rest and medication.',
    'Diabetes': 'A chronic condition where blood sugar levels are abnormally high.',
    'Hypertension (High Blood Pressure)': 'Often called a “silent killer” because symptoms may not appear early.',
    'Asthma': 'A respiratory condition causing airway inflammation and breathing difficulty.',
    'COVID-19': 'A contagious viral infection affecting the respiratory system.',
    'Dengue': 'A mosquito-borne viral disease common in tropical regions.',
    'Malaria': 'A serious mosquito-borne disease caused by parasites.',
    'Typhoid': 'A bacterial infection spread through contaminated food and water.',
    'Tuberculosis (TB)': 'A bacterial infection mainly affecting the lungs.',
    'Migraine': 'A neurological condition causing intense recurring headaches.',
    'Food Poisoning': 'Caused by consuming contaminated food or water.',
    'Unknown': 'Based on the symptoms provided, we could not determine a specific condition.'
}

PRECAUTIONS = {
    'Common Cold': 'Rest, drink fluids, and use over-the-counter cold remedies.',
    'Flu (Influenza)': 'Get plenty of rest, stay hydrated, and take antiviral medication if prescribed.',
    'Diabetes': 'Monitor blood sugar levels, follow a balanced diet, and take prescribed medications.',
    'Hypertension (High Blood Pressure)': 'Adopt a low-salt diet, exercise regularly, and take blood pressure medication.',
    'Asthma': 'Avoid triggers, use inhalers as prescribed, and have an action plan.',
    'COVID-19': 'Isolate yourself, rest, stay hydrated, and monitor your oxygen levels.',
    'Dengue': 'Rest, drink plenty of fluids, and avoid mosquito bites.',
    'Malaria': 'Take antimalarial drugs as prescribed and use mosquito nets.',
    'Typhoid': 'Drink clean water, eat hygienic food, and complete your antibiotic course.',
    'Tuberculosis (TB)': 'Take your medication as prescribed for the full duration and cover your mouth when coughing.',
    'Migraine': 'Rest in a dark, quiet room, use cold packs, and take pain relievers.',
    'Food Poisoning': 'Stay hydrated, eat bland foods, and rest.',
    'Unknown': 'Please consult a healthcare professional for a proper diagnosis.'
}

ADVICE = {
    'Common Cold': 'Consult a doctor if symptoms last more than 10 days or if you have a high fever.',
    'Flu (Influenza)': 'Seek medical attention if you have difficulty breathing, chest pain, or severe symptoms.',
    'Diabetes': 'Regular check-ups with a doctor are essential to manage the condition.',
    'Hypertension (High Blood Pressure)': 'Consult a doctor for regular blood pressure monitoring and management.',
    'Asthma': 'See a doctor if your symptoms worsen or if your inhaler is not providing relief.',
    'COVID-19': 'Seek immediate medical attention if you have trouble breathing, persistent chest pain, or confusion.',
    'Dengue': 'Consult a doctor immediately if you suspect you have dengue, especially if you have severe abdominal pain or bleeding.',
    'Malaria': 'Malaria is a medical emergency; seek immediate medical attention.',
    'Typhoid': 'Consult a doctor if you have a high fever and other symptoms of typhoid.',
    'Tuberculosis (TB)': 'It is crucial to see a doctor if you have a persistent cough or other TB symptoms.',
    'Migraine': 'Consult a doctor if you have frequent or severe migraines.',
    'Food Poisoning': 'See a doctor if you have a high fever, blood in your stool, or signs of dehydration.',
    'Unknown': 'If symptoms persist or worsen, seek medical attention immediately.'
}
@app.route('/predict', methods=['POST'])
def predict():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    symptoms_desc = request.form['symptoms'].lower()
    common_symptoms = request.form.getlist('common_symptoms')
    
    all_symptoms = symptoms_desc + " " + " ".join(common_symptoms)

    # 👇 YAHAN NEW LOGIC LAGANA HAI
    best_match = 0
    predicted_disease = "Unknown"

    for disease, keywords in DISEASES.items():
        match_count = sum(1 for keyword in keywords if keyword in all_symptoms)
        
        if match_count > best_match:
            best_match = match_count
            predicted_disease = disease

    # baaki code same rahega

    description = DESCRIPTIONS.get(predicted_disease)
    precautions = PRECAUTIONS.get(predicted_disease)
    advice = ADVICE.get(predicted_disease)

    conn = get_db_connection()
    conn.execute('INSERT INTO patients (name, age, gender, symptoms, disease, precautions, advice) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (name, age, gender, all_symptoms, predicted_disease, precautions, advice))
    conn.commit()
    conn.close()

    return render_template('result.html', 
                           disease=predicted_disease, 
                           description=description,
                           precautions=precautions, 
                           advice=advice)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)