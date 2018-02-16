from flask import Flask, render_template, request, redirect, session, render_template_string
import random, string
import sys
import os
import ast
import csv
import collections

from init import app, db
from models import Template

from fix_emails.matthew import Matthew
from fix_emails.job import Job



def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class UserSession(object):
    def __init__(self):
        self.template = ""
        if session.get("user_id", ""):
            # Old session
            self.user_id = session["user_id"]
            self.template = Template.query.filter_by(session=self.user_id).first()

        if not self.template:
            # New session
            self.user_id = randomword(32)
            session["user_id"] = self.user_id
            self.template = Template(self.user_id)
            db.session.add(self.template)
            db.session.commit()


@app.route('/', methods=["GET", "POST"])
def index():
    user = UserSession()

    if request.method == "POST":
        form = request.form
        country = form.get("country_select", "CA")
        source = form.get("source", "")

        user.template.country = country
        user.template.source = source

        job = Job(False, input_type="qt")

        obj = job.process_email(user.template.html, source_code=source, country=country)
        user.template.html = obj.get_content()
        user.template.result_images = str(obj.get_images())
        user.template.result_links = str(obj.get_links())
        user.template.result_source = str(obj.get_source_codes())
        user.template.result_notes = str(obj.notifications)
        db.session.add(user.template)
        db.session.commit()

        return render_template("index.html", result=True, country=user.template.country)

    return render_template("index.html", country=user.template.country)


@app.route('/editor/')
def editor():
    user = UserSession()
    html = user.template.html
    return render_template("editor.html", html=html)


@app.route('/preview/', methods=["GET", "POST"])
def preview():
    user = UserSession()
    if request.method == "POST":
        form = request.form
        if form["html"] and form["html"] != user.template.html:
            html = form["html"]
            user.template.html = html
            db.session.add(user.template)
            db.session.commit()
    else:
        html = user.template.html
    return render_template("preview.html", html=html)


def str_to_dict(data):
    try:
        result = ast.literal_eval(data)
        return result
    except:
        return ["Error getting result data"]


@app.route('/result/', methods=["GET", "POST"])
def result():
    user = UserSession()
    images = str_to_dict(user.template.result_images)
    links = str_to_dict(user.template.result_links)
    source = str_to_dict(user.template.result_source)
    notes = str_to_dict(user.template.result_notes)
    return render_template("result.html", images=images, links=links, source=source, notes=notes)


@app.route('/country/', methods=["GET", "POST"])
def country():
    user = UserSession()
    if request.method == "POST":
        form = request.form
        try:
            user.template.country = form["country"]
        except:
            user.template.country = form["country_select"]
        db.session.add(user.template)
        db.session.commit()
    return render_template_string("Country Updated to {}".format(user.template.country))


@app.route('/replace/', methods=["GET", "POST"])
def replace():
    user = UserSession()
    country = user.template.country
    if not country:
        country = "CA"
    save = False
    if request.method == "POST":
        form = request.form
        csv_data = []
        form_data = {}

        for key, item in form.items():
            form_data[key] = item

        type = form_data["type"]

        del form_data["type"]

        count = 1
        while form_data.get("{}-old".format(count), ""):
            if form_data["{}-old".format(count)] != "*DEL":
                csv_data.append(
                    (
                        form_data["{}-old".format(count)],
                        form_data["{}-new".format(count)]
                    )
                )
            count += 1

        with open('data/{}_{}.csv'.format(type, country), 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f, delimiter='|', lineterminator='\n')
            writer.writerows(csv_data)
        save = True

    csv_data = { "replace": [], "links": [] }
    with open('data/replace_{}.csv'.format(country), 'r', newline='') as f:
        data = csv.reader(f, delimiter='|')
        for item in data:
            csv_data["replace"].append(item)

    with open('data/links_{}.csv'.format(country), 'r', newline='') as f:
        data = csv.reader(f, delimiter='|')
        for item in data:
            csv_data["links"].append(item)


    return render_template("replace.html", data=csv_data, save=save, country=country)


