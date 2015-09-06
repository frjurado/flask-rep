from flask import request, session, render_template, redirect, url_for, flash
from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST" and request.form['name'] != "":
        session['name'] = request.form['name']
        flash('Your name has been changed!')
        return redirect(url_for('main.index'))
    return render_template('index.html')
