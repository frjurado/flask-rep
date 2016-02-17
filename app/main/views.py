from flask import request, session, render_template, redirect, url_for, flash
from . import main
from .forms import NameForm

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        flash('Your name has been changed!')
        return redirect(url_for('main.index'))
    return render_template('index.html', form=form)
