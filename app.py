from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import subprocess
import threading

app = Flask(__name__)
app.secret_key = 'jits1234'  # Replace with your own secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/vr_blackboard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

# Define your Drawing model
class Drawing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drawing_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/collection')
def collection():
    if 'user_id' in session:
        # This list should be dynamically retrieved from your storage (e.g., database)
        images = ['saved_images/image1.png', 'saved_images/image2.png', 'saved_images/image3.png']
        return render_template('collection.html', images=images)
    else:
        return redirect(url_for('login'))

@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Implement your logic to handle password reset here, such as sending a reset email
        return "A password reset link has been sent to your email."
    
    return render_template('forget_password.html')

def run_blackboard_script(): 
    subprocess.run(["python", "blackboard.py"])

@app.route('/run_blackboard')
def run_blackboard():
    if 'user_id' in session:
        subprocess.run(["python", "blackboard.py"])
        return "BlackBoard script has been executed!"
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
