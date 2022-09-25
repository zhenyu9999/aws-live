"""


@app.route("/department_assign")
def d():
    department=department.query.all()
    employe=employees.query.all()
    role= role.query.all()
    return render_template("assign_department.html",role=role,department=department,employe=employe)

@app.route("/assign_department",methods=['GET','POST'])
def assign_department():
    if request.method == 'POST':
        employe= request.form.get("employe")
        department= request.form.get("department")
        role= request.form.get("role")
        add = assign_department(employee=employe,department=department,role=role)
        db.session.add(add)
        db.session.commit()
        return redirect("/department_assign")





@app.route("/view_assign",methods=['GET','POST'])
def view_assign():
    assign= assign_department.query.all()
    return render_template("view_assign.html",assign=assign)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    """
