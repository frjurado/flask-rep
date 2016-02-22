from flask import request, session, render_template, redirect, url_for, flash
from . import main
from .. import db
from .forms import NameForm
from ..models import User, Role

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        role = Role.query.filter_by(name=form.role.data).first()
        if role is None:
            role = Role(name=form.role.data)
            db.session.add(role)
        if user is None or user.role == role:
            if user is None:
                user = User(name=form.name.data, role=role)
                db.session.add(user)
                flash('Welcome!')
            else:
                flash('Welcome back!')
            session['name'] = form.name.data
            session['role'] = form.role.data
        else:
            flash("We don't think you're REALLY {}".format(form.name.data))
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('index.html', form=form, users=users)
