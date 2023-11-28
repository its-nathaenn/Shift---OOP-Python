from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import re

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
    firstName = db.Column(db.String(100), default = "first name")
    lastName = db.Column(db.String(100), default = "last name")
    password = db.Column(db.String(100), default = "no password")
    email = db.Column(db.String(100), default = "no email", primary_key = True)
    position = db.Column(db.String(100), default = "Employee")
    time_off_requests = db.relationship('TimeOffRequest', backref='employee', lazy=True)

    def __repr__(self):
        return f"{self.username}"

class TimeOffRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_email = db.Column(db.String(100), db.ForeignKey('employee.email'), nullable=False)
    date = db.Column(db.Date)
    reason = db.Column(db.String(250))
    status = db.Column(db.String(100), default='Pending')

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
                session['position'] = user.position
                return redirect('/home')
            else:
                # Invalid credentials; show error message
                return redirect('/')
            
        elif action == 'Sign Up':
            # Process new account creation
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            # Check if the 'is_manager' checkbox was checked
            is_manager = 'is_manager' in request.form

            # Set position based on the checkbox
            position = 'Manager' if is_manager else 'Employee'

            # check for duplicates
            existing_user = Employee.query.filter((Employee.email == email) | (Employee.username == username)).first()
            if existing_user:
                # User with this email or username already exists
                # Handle this scenario - perhaps redirect back with an error message
                flash('An account with this email or username already exists.', 'error')
                return redirect('/')
            
            hashed_password = generate_password_hash(password)
            new_employee = Employee(username=username, email=email, password=hashed_password, position=position)
            db.session.add(new_employee)
            try:
                db.session.commit()
                # refresh information for the user
                session['user_id'] = new_employee.email
                session['username'] = new_employee.username
                session['position'] = new_employee.position  # Include the position in the session
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
    
    # Retrieve session data
    username = session.get('username')
    email = session.get('user_id')  # 'user_id' in the session is the email
    position = session.get('position')  # Retrieve the position from the session

    # Use session data to display on the homepage
    return render_template('homepage.html', name=username, email=email, position=position)



@app.route('/edit_profile')
def edit_profile():
    if 'username' not in session:
        return redirect('/')

    current_email = session.get('user_id')
    employee = Employee.query.filter_by(email=current_email).first()

    if employee:
        # Pass the most recent data to the template
        return render_template('personal_info.html', employee=employee)
    else:
        flash("Employee not found.", "error")
        return redirect('/home')

    
@app.route('/update_personal_info', methods=['POST'])
def update_personal_info():
    if 'username' not in session:
        flash('You must be logged in to update your information.', 'error')
        return redirect('/')

    current_username = session.get('username')
    new_username = request.form.get('new_username')
    new_first_name = request.form.get('new_first_name')
    new_last_name = request.form.get('new_last_name')
    new_email = request.form.get('new_email')

    employee = Employee.query.filter_by(username=current_username).first()

    if employee and employee.username == current_username:
        employee.username = new_username
        employee.first_name = new_first_name
        employee.last_name = new_last_name
        employee.email = new_email
        db.session.commit()
        flash('Personal information updated successfully!', 'success')

        # Update the session information
        session['username'] = new_username
        session['user_id'] = new_email
        session['firstName'] = new_first_name
        session['lastName'] = new_last_name
    else:
        flash('Unauthorized action or employee not found.', 'error')

    return redirect('/home')


@app.route('/request_time_off', methods=['GET'])
def request_time_off():
    # Ensure that only logged-in users can access this page
    if 'username' not in session:
        return redirect('/')

    # Check if the user's position is 'Employee'
    if session.get('position') != 'Employee':
        # Redirect or show an error for non-employees
        flash('This action is only available for employees.', 'error')
        return redirect('/home')
    
    if request.method == 'POST':
        validation_result, message = validate_request()
        if validation_result:
            # Process the form data here (e.g., save to database)
            flash('Form submitted successfully!', 'success')
            return redirect('/home')  # Redirect after successful submission
        else:
            flash(message, 'error')  # Show validation error message

    return render_template('off_request_EMP.html')

def validate_request():
    if is_empty(request.form['data_3']):
        return False, 'First name is required!'
    if is_empty(request.form['data_4']):
        return False, 'Last name is required!'
    if not validate_email(request.form['data_5']):
        return False, 'Valid email is required!'
    if is_empty(request.form['data_6']):
        return False, 'Date is required!'
    if is_empty(request.form['data_8']):
        return False, 'Reason is required!'
    return True, None

def validate_email(email):
    # Simple email validation regex
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


@app.route('/submit_time_off', methods=['POST'])
def submit_time_off():
    validation_result, message = validate_request()
    if validation_result:
        # Process the form data here (e.g., save to database)
        flash('Form submitted successfully!', 'success')
        return redirect('/home')  # Redirect after successful submission
    else:
        flash(message, 'error')  # Show validation error message
        return render_template('off_request.html')

def is_empty(value):
    return len(value) == 0 or not value.strip()



@app.route('/work_schedule')
def work_schedule():
    if 'username' not in session:
        flash('You must be logged in to view the work schedule.', 'error')
        return redirect('/')

    # You can add any logic here to fetch the necessary data for the schedule
    # ...

    return render_template('schedule_view_EMP.html')



@app.route('/employee_list')
def employee_list():
    if 'username' not in session or session.get('position') != 'Manager':
        return redirect('/')

    # Fetch the list of employees from the database
    employees = Employee.query.all()
    return render_template('employee_List_MAN.html', employees=employees)


@app.route('/employee_info/<email>')
def employee_info_page(email):
    # Fetch the employee details from the database using the email
    employee = Employee.query.filter_by(email=email).first()
    
    if employee:
        return render_template('employee_info.html', employee=employee)
    else:
        flash('Employee not found', 'error')
        return redirect('/employee_list')

@app.route('/manager_request_view')
def manager_request_view():
    if 'username' not in session or session.get('position') != 'Manager':
        return redirect('/')

    employee_forms = TimeOffRequest.query.all()
    return render_template('manager_request_view.html', employee_forms=employee_forms)


@app.route('/approve/<int:request_id>', methods=['POST'])
def approve_route(request_id):
    request_to_approve = TimeOffRequest.query.get(request_id)
    if request_to_approve and request_to_approve.status == 'Pending':
        request_to_approve.status = 'Approved'
        db.session.commit()
        flash('Time-off request approved', 'success')
    else:
        flash('Request not found or already processed', 'error')
    return redirect('/manager_request_view')

@app.route('/deny/<int:request_id>', methods=['POST'])
def deny_route(request_id):
    request_to_deny = TimeOffRequest.query.get(request_id)
    if request_to_deny and request_to_deny.status == 'Pending':
        request_to_deny.status = 'Denied'
        db.session.commit()
        flash('Time-off request denied', 'error')
    else:
        flash('Request not found or already processed', 'error')
    return redirect('/manager_request_view')

# Add the option to run this file directly
if __name__ == "__main__":
    app.run(debug = True) # debug allows you to see what is happening 

