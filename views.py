from flask import Flask, render_template, request, redirect, session
from init import app
from fix_emails.matthew import Matthew
from fix_emails.job import Job
import random, string
import sys
import os

def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def setup_session():
    user_id = randomword(32)
    session["user_id"] = user_id
    for path in ["html/{}-email.html", "html/{}-result.html" , "html/{}-print"]:
        path = path.format(user_id)
        with open(path, "w+") as f:
            f.write("")
    return user_id


# So we can capture print statements
class WritableObject(object):

    def __init__(self):
        self.content = []

    def write(self, string):
        self.content.append(string)


@app.route('/', methods=["GET", "POST"])
def index():
    user_id = session.get("user_id", "")
    if not user_id:
        user_id = setup_session()

    if request.method == "POST":
        form = request.form
        country = form.get("country_select", "CA")
        source = form.get("source", "")

        session['country'] = country
        session['source'] = source

        print_out = WritableObject()
        sys.stdout = print_out

        job = Job(False, input_type="qt")

        obj = job.html_email("html/{}-email.html".format(user_id), source_code=source, country=country)
        write_outfile(obj, user_id)


        obj = job.run_results("html/{}-email.html".format(user_id))
        write_results(job, obj, user_id)
        html = job.html_result(obj)

        write_print_out(print_out, user_id)

        return render_template("index.html", result=html)

    return render_template("index.html", country=session.get("country", ""))


@app.route('/editor/')
def editor():
    user_id = session.get("user_id", "")
    print("User ID - {}".format(user_id))

    if user_id:
        with open("html/{}-email.html".format(user_id), 'r+') as f:
            html = f.read()
    else:
        user_id = setup_session()
        html = ""
    return render_template("editor.html", html=html)


@app.route('/preview/', methods=["GET", "POST"])
def preview():
    user_id = session.get("user_id", "")
    if user_id:
        with open("html/{}-email.html".format(user_id), 'r+') as f:
            html = f.read()

        if request.method == "POST":
            form = request.form
            if form["html"] and form["html"] != html:
                html = form["html"]
                with open("html/{}-email.html".format(user_id), 'w+') as w:
                    w.write(html)
    else:
        user_id = setup_session()
        html = ""

    return render_template("preview.html", html=html)


@app.route('/result/', methods=["GET", "POST"])
def result():
    user_id = session.get("user_id", "")
    if user_id:
        with open("html/{}-result.html".format(user_id), 'r+') as f:
            result = f.read()

        with open("html/{}-print".format(user_id), 'r+') as f:
            print = f.readlines()
    else:
        user_id = setup_session()
        result = ""
        print = ""

    return render_template("result.html", html=result, print=print)


def write_outfile(obj, user_id):
    with open("html/{}-email.html".format(user_id), 'w+') as o:
        data = obj.get_content()
        o.write(data)


def write_results(job, obj, user_id):
    html = job.html_result(obj)
    if html:
        with open("html/{}-result.html".format(user_id), 'w+') as o:
            o.write(html)


def write_print_out(print, user_id):
    with open("html/{}-print".format(user_id), 'w+') as o:
        content = print.content
        o.writelines(content)
