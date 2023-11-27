from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# flask functions as a state based application

app = Flask(__name__)
app.secret_key = 'Shift'

# Setup app to use a sqlalchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sampleDB.db'
db = SQLAlchemy(app)



# Setup a simple table for database
class Employee(db.Model):
    username = db.Column(db.String(100), default = "no username")
    password = db.Column(db.String(100), default = "no password")
    email = db.Column(db.String(100), default = "no email", primary_key = True)
    position = db.Column(db.String(100), default = "Employee")
    # work_id = db.Column(db.String(100), default = "0000")

    def __repr__(self):
        return f"{self.username} - {self.work_id}"


# Create tables in a Database
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Sign In':
            # Process login
            username = request.form.get('username')
            password = request.form.get('password')

            # Validate user credentials via query
            user = Employee.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                # Credentials are valid; Redirect to home 
                session['user_id'] = user.email
                session['username'] = user.username
                return redirect('/home')
            else:
                # Invalid credentials; show error message
                return redirect('/')
            
        elif action == 'Sign Up':
            # Process new account creation
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')


            # check for duplicates
            existing_user = Employee.query.filter((Employee.email == email) | (Employee.username == username)).first()
            if existing_user:
                # User with this email or username already exists
                # Handle this scenario - perhaps redirect back with an error message
                flash('An account with this email or username already exists.', 'error')
                return redirect('/')
            
            hashed_password = generate_password_hash(password)
            new_employee = Employee(username=username, email=email, password=hashed_password)
            db.session.add(new_employee)
            try:
                db.session.commit()
            except SQLAlchemy.exc.IntegrityError:
                db.session.rollback()
                flash('An account with this email or username already exists.', 'error')
                return redirect('/')

        # Redirect or send a response
        return redirect('/home')  # Redirect to home or another appropriate page
    
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('/')
    # Proceed with the logic for authenticated users
    return render_template('homepage.html')


@app.route('/request', methods=['GET', 'POST'])
def requestform():
    if request.method == 'POST':
        if validate_request():
            # Process the form data here (e.g., send email, save to database)
            return "Form submitted successfully!"
        else:
            return "Form validation failed. Please check the entered data."
    return render_template('request.html')

def validate_request():
    if is_empty(request.form['data_1']):
        return False, 'First name is required!'
    if is_empty(request.form['data_2']):
        return False, 'Last name is required!'
    if is_empty(request.form['data_6']):
        return False, 'Work ID is required!'
    if is_empty(request.form['data_3']):
        return False, 'Date is required!'
    if is_empty(request.form['data_4']):
        return False, 'Reason is required!'
    return True, None

def is_empty(value):
    return len(value) == 0 or not value.strip()
# Replace this with your actual data store or database
employee_forms = [
    {"first_name": "John", "last_name": "Doe", "work_id": "12345", "date": "2023-01-01", "reason": "Vacation", "status": "Pending"},
    {"first_name": "Jane", "last_name": "Smith", "work_id": "67890", "date": "2023-02-15", "reason": "Sick Leave", "status": "Pending"}
    # Add more employee forms as needed
]

def approve_request(work_id):
    for form in employee_forms:
        if form['work_id'] == work_id:
            form['status'] = 'Approved'
            # Implement logic to perform approval action (e.g., send email, update database)
            break

def deny_request(work_id):
    for form in employee_forms:
        if form['work_id'] == work_id:
            form['status'] = 'Denied'
            # Implement logic to perform denial action (e.g., send email, update database)
            break

@app.route('/manager_view')
def manager_view():
    return render_template('managerrequestview.html', employee_forms=employee_forms)

@app.route('/approve/<work_id>', methods=['POST'])
def approve_route(work_id):
    approve_request(work_id)
    return redirect('/manager_view')

@app.route('/deny/<work_id>', methods=['POST'])
def deny_route(work_id):
    deny_request(work_id)
    return redirect('/manager_view')

# Add the option to run this file directly
if __name__ == "__main__":
    app.run(debug = True) # debug allows you to see what is happening 

