import os

from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__, template_folder='./templates')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/")
def start():
    if session.get("admin_id"):
        return render_template("dashboard.html")
    else:
        return render_template("login.html")


@app.route("/login",methods=['GET','POST'])
def login():

   def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'admin_name' in request.form and 'admin_password' in request.form:
        # Create variables for easy access
        admin_name = request.form['admin_name']
        admin_password = request.form['admin_password']
        # Check if account exists using MySQL
        validateAccount = 'SELECT * FROM admin WHERE username = %s AND password = %s', (admin_name, admin_password,)
        cursor = db_conn.cursor()
        cursor.execute(validateAccount)
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['admin_id'] = account['admin_id']
            session['admin_name'] = account['admin_name']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
