from flask import Flask, render_template, request

# import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# flask functions as a state based application

app = Flask(__name__)

# Setup app to use a sqlalchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sampleDB.db'
db = SQLAlchemy(app)



# Setup a simple table for database
class Employee(db.Model):
    username = db.Column(db.String(100), primary_key = True)
    position = db.Column(db.String(100), default = "Employee")
    # numVisits = db.Column(db.Integer, default = 1) #num of visits will be 1 by default

    def __repr__(self):
        return f"{self.username} - {self.numVisits}"



# Create tables in a Database
with app.app_context():
    db.create_all()



# Make a homepage
@app.route("/")
def homepage():
    #return "<h1> This is the homepage of my App! </h1>"
    return render_template('base.html')



@app.route("/hello/<name>")
def hello(name):
    #listOfNames = [name, "yoyo", "yennifer"]
    #return render_template('name.html', Sname = name, nameList = listOfNames)
    return render_template("base.html")



@app.route('/form', methods=['GET', 'POST'])
def formDemo():
    name = None
    if request.method == 'POST':
        if request.form['name']:
            name=request.form['name']
            # Check if user is in database
            visitor = Visitor.query.get(name)
            if visitor == None:
                # Add Visitor to the database
                visitor = Visitor(username = name)
                db.session.add(visitor)
            else:
                visitor.numVisits += 1
        
            # commit changes to the database
            db.session.commit()
    return render_template('form.html', name=name)


# Add in a page to view all visitors
@app.route("/visitors")
def visitors():
    # Query the database to find all the visitors
    people = Visitor.query.all()
    return render_template("visitors.html", people = people)







# Add the option to run this file directly
if __name__ == "__main__":
    app.run(debug = True) # debug allows you to see what is happening 

