from flask import Flask, render_template, request, redirect, url_for, session
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__, template_folder='./templates')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

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


@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST' and 'admin_name' in request.form and 'admin_password' in request.form:
        # Create variables for easy access
        admin_name = request.form['admin_name']
        admin_password = request.form['admin_password']
        validateAccount = "SELECT * FROM admin WHERE username = '{}' AND password = '{}'".format(admin_name, admin_password,)

        cursor = db_conn.cursor()
        cursor.execute(validateAccount)
        account = cursor.fetchone()

        if account:
            session['logged'] = True
            session['admin_id'] = account[0]
            session['admin_name'] = account[1]
            cursor.close()
            return render_template("dashboard.html")
        else:
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('/login.html', msg=msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
