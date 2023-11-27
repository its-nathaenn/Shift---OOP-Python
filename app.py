from flask import Flask, render_template, request, redirect, session

# import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# flask functions as a state based application

app = Flask(__name__)

# Setup app to use a sqlalchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sampleDB.db'
db = SQLAlchemy(app)



# Setup a simple table for database
class Employee(db.Model):
    name = db.Column(db.String(100), default = "no name")
    email = db.Column(db.String(100), default = "no email", primary_key = True)
    position = db.Column(db.String(100), default = "Employee")
    work_id = db.Column(db.String(100), default = "0000")

    def __repr__(self):
        return f"{self.username} - {self.work_id}"


# Create tables in a Database
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email') # Add an email input field in HTML
        # ... similarly retrieve other fields like password, etc. if needed

        # Create Employee object
        new_employee = Employee(name=username, email=email)
        # Add default values for other fields if not provided in the form

        # Save to database
        db.session.add(new_employee)
        db.session.commit()

        # Redirect or send a response
        return redirect('/home')  # Redirect to home or another appropriate page

    return render_template('signin.html')


@app.route('/home')
def homepage():
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

