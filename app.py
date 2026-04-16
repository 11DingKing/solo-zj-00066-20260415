import datetime
import os
import math
from flask import Flask, render_template, redirect, url_for, request, jsonify
from sqlalchemy import func

from forms import SignupForm, SearchForm
from models import User, OperationLog, Signups
from database import db_session, init_db

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
PER_PAGE = 10


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def log_operation(user_id, action, details=''):
    log = OperationLog(
        user_id=user_id,
        action=action,
        details=details,
        timestamp=datetime.datetime.now()
    )
    db_session.add(log)
    db_session.commit()


@app.route("/", methods=('GET', 'POST'))
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            form.email.errors.append('该邮箱已被注册')
            return render_template('signup.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            date_signed_up=datetime.datetime.now()
        )
        user.set_password(form.password.data)
        db_session.add(user)
        db_session.commit()
        
        log_operation(user.id, '用户注册', f'用户 {user.name} 完成注册')
        return redirect(url_for('success'))
    return render_template('signup.html', form=form)


@app.route("/success")
def success():
    return render_template('success.html')


@app.route("/users", methods=['GET', 'POST'])
def users_list():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '', type=str)
    
    form = SearchForm()
    if form.validate_on_submit():
        search_query = form.search.data
        return redirect(url_for('users_list', search=search_query))
    elif request.method == 'GET' and search_query:
        form.search.data = search_query
    
    query = User.query
    if search_query:
        query = query.filter(User.name.ilike(f'%{search_query}%'))
    
    total = query.count()
    total_pages = math.ceil(total / PER_PAGE)
    
    offset = (page - 1) * PER_PAGE
    users = query.order_by(User.date_signed_up.desc()).offset(offset).limit(PER_PAGE).all()
    
    return render_template('users.html',
                           users=users,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           total=total,
                           search_query=search_query)


@app.route("/users/<int:user_id>")
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    logs = OperationLog.query.filter_by(user_id=user_id).order_by(OperationLog.timestamp.desc()).all()
    return render_template('user_detail.html', user=user, logs=logs)


@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


@app.route("/api/stats")
def get_stats():
    today = datetime.datetime.now().date()
    week_ago = today - datetime.timedelta(days=7)
    
    total_users = db_session.query(func.count(User.id)).scalar() or 0
    
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_users = db_session.query(func.count(User.id)).filter(
        User.date_signed_up >= today_start
    ).scalar() or 0
    
    week_start = datetime.datetime.combine(week_ago, datetime.time.min)
    week_users = db_session.query(func.count(User.id)).filter(
        User.date_signed_up >= week_start
    ).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'today_new': today_users,
        'week_new': week_users
    })


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5090, debug=True)
