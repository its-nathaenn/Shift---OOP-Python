from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# Setup app to use a sqlalchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sampleDB.db'
db = SQLAlchemy(app)


# Setup a simple table for database
class Employee(db.Model):
    username = db.Column(db.String(100), primary_key = True)
    position = db.Column(db.String(100), default = "Employee")
    work_id = db.Column(db.String(100), default = "0000")

    def __repr__(self):
        return f"{self.username} - {self.work_id}"

# Create tables in a Database
with app.app_context():
    db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['Work ID'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('/home'))
    return render_template('base.html', error=error)


@app.route('/signin')
def signin():
    return render_template('signin.html')



@app.route('/home')
def homepage():
    return render_template('homepage.html') 



@app.route('/managerhome')
def managerpage():
    return render_template('managerpage.html') 



@app.route('/shift')
def schedule():
    return render_template('shift.html')
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
    return render_template('managerview.html', employee_forms=employee_forms)

@app.route('/approve/<work_id>', methods=['POST'])
def approve_route(work_id):
    approve_request(work_id)
    return redirect('/manager_view')



@app.route('/deny/<work_id>', methods=['POST'])
def deny_route(work_id):
    deny_request(work_id)
    return redirect('/manager_view')



if __name__ == '__main__':
    app.run(debug=True)

