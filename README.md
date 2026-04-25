Health Checkup Web Application

A beginner-friendly full-stack web application that helps users perform a basic health checkup by entering symptoms and receiving a predicted disease along with precautions and medical advice.

🚀 Features:
👤 User Registration & Login System (with password hashing)
🩺 Symptom-based Disease Prediction
📊 Stores Patient Data in Database
💡 Displays Disease Description, Precautions & Advice
🎨 Clean and Responsive User Interface
🔐 Secure Authentication using hashed passwords

Tech Stack
Frontend:
HTML
CSS
JavaScript
Backend:
Python
Flask (Lightweight Web Framework)
Database:
SQLite (File-based database)

📁 Project Structure
templates/ → HTML pages (UI)
static/ → CSS styling
app.py → Main backend logic
schema.sql → Database schema
init_db.py → Database initialization
database.db → SQLite database file

⚙️ How It Works
1.User registers and logs into the system
2.User enters symptoms in the form
3.Backend processes symptoms using keyword matching logic
4.System predicts the most relevant disease
5.Results (disease, precautions, advice) are displayed
6.Data is stored in the database for future reference
