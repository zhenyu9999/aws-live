from flask import Flask, render_template, request, redirect, url_for, session, flash
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


# @app.route("/")
# def start():
#     # if session.get("admin_id"):
#     return render_template("dashboard.html")

@app.route('/')
def Index():
    if session.get("admin_id"):
        return render_template('/dashboard.html')

    else:
        return render_template('/login.html')


# LIST OUT ALL THE EMPLOYEES
@app.route("/listEmployee")
def listEmployee():
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee")
    data = cursor.fetchall()
    cursor.close()
    return render_template("listEmployee.html", employee=data)


# REDIRECT TO ADD EMPLOYEE PAGE
@app.route("/addEmployee")
def add():
    return render_template("addEmployee.html")


@app.route("/delete/<string:employee_id>", methods=['POST', 'GET'])
def deleteEmp(employee_id):
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM employee WHERE employee_id = {0}".format(employee_id))
    cursor.close()
    flash('Employee Removed Successfully')
    return redirect(url_for('listEmployee'))


# RETRIEVE THE SPECIFIC EMPLOYEE DETAILS BEFORE GOING TO UPDATE
@app.route("/editEmployee/<employee_id>", methods=['POST', 'GET'])
def editEmp(employee_id):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM employee WHERE employee_id = %s', employee_id)
    details = cursor.fetchall()
    cursor.close()
    print(details[0])
    return render_template('editEmployee.html', employees=details[0])


# UPDATE THE EMPLOYEE DETAILS.AFTER UPDATED GO DIRECT BACK TO LIST ALL EMPLOYEE PAGE
@app.route("/updateEmployee/<employee_id>", methods=['POST', 'GET'])
def updateEmployee(employee_id):
    if request.method == 'POST':
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        employee_email = request.form['employee_email']
        employee_address = request.form['employee_address']
        employee_mobile = request.form['employee_mobile']

    editEmployees = (
        "UPDATE employee SET employee_name = %s, employee_password = %s,employee_email = %s, employee_address = %s,employee_mobile = %s WHERE employee_id = %s"
    )
    cursor = db_conn.cursor()

    try:
        cursor.execute(editEmployees,
                       (employee_name, employee_password, employee_email, employee_address, employee_mobile,
                        employee_id))
    finally:
        db_conn.commit()
    print("UPDATE SUCCESSFULLY")
    return redirect(url_for('listEmployee'))


# ADD THE NEW EMPLOYEE TO DATABASE
@app.route("/addEmployee", methods=['POST'])
def addEmployee():
    if request.method == 'POST' and 'employee_name' in request.form and 'employee_password' in request.form and 'employee_email' in request.form and 'employee_address' in request.form and 'employee_mobile' in request.form:
        # emp_id = request.form['emp_id']
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        employee_email = request.form['employee_email']
        employee_address = request.form['employee_address']
        employee_mobile = request.form['employee_mobile']
        emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    addEmployees = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(addEmployees,
                       ('', employee_name, employee_password, employee_email, employee_address, employee_mobile))
        db_conn.commit()
        emp_image_file_name_in_s3 = "emp-id-" + str(employee_name) + "_image_file"
        # s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            # s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            # s3_location = (bucket_location['LocationConstraint'])
            #
            # if s3_location is None:
            #     s3_location = ''
            # else:
            #     s3_location = '-' + s3_location
            #
            # object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
            #     s3_location,
            #     custombucket,
            #     emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("Employee added successfully")
    return redirect(url_for('listEmployee'))


# THE LOGIN FUNCTION
@app.route("/login", methods=['GET', 'POST'])
# Login function
def login():
    if request.method == 'POST' and 'admin_name' in request.form and 'admin_password' in request.form:
        # Create variables for easy access
        admin_name = request.form['admin_name']
        admin_password = request.form['admin_password']
        validateAccount = "SELECT * FROM admin WHERE admin_name = '{}' AND admin_password = '{}'".format(admin_name,
                                                                                                         admin_password, )

        cursor = db_conn.cursor()
        cursor.execute(validateAccount)
        account = cursor.fetchone()

        if account:
            session['logged'] = True
            session['admin_id'] = account[0]
            session['admin_name'] = account[1]
            cursor.close()
            return render_template("/dashboard.html")
        else:
            msg = 'Incorrect username/password!'
    return render_template('/login.html', msg=msg)


# LOGOUT FUNCTION
@app.route("/logout")
def logout():
    session['logged'] = False
    session["admin_id"] = []
    session["admin_name"] = []
    return render_template('/login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
