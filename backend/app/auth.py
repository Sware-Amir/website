import os
import requests
from flask import Blueprint, request, redirect, url_for, render_template, session, flash, current_app
from .models import User, db
from datetime import datetime
from . import limiter
import logging

HCAPTCHA_SECRET = os.getenv('HCAPTCHA_SECRET')
logger = logging.getLogger(__name__)

def verify_hcaptcha(token, remoteip=None):
    if not HCAPTCHA_SECRET or not token:
        return False
    resp = requests.post("https://hcaptcha.com/siteverify", data={
        'secret': HCAPTCHA_SECRET,
        'response': token,
        'remoteip': remoteip
    }, timeout=5)
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get('success', False)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    generic_error = 'Ongeldige gebruikersnaam of wachtwoord'
    if request.method == 'POST':
        token = request.form.get('h-captcha-response')
        if not verify_hcaptcha(token, request.remote_addr):
            return render_template('login.html', error='Captcha verificatie mislukt')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error=generic_error)
        if user.is_locked():
            remaining_min = max(1, int((user.locked_until - datetime.utcnow()).total_seconds() // 60))
            return render_template('login.html', error=f'Account tijdelijk geblokkeerd. Probeer over {remaining_min} min.')
        if user.check_password(password):
            user.reset_failed_attempts()
            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.voorpagina'))
        user.register_failed_attempt()
        if user.is_locked():
            logger.warning("Account locked", extra={'username': user.username, 'ip': request.remote_addr})
            return render_template('login.html', error='Te veel mislukte pogingen. Account tijdelijk geblokkeerd.')
        return render_template('login.html', error=generic_error)
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        token = request.form.get('h-captcha-response')
        if not verify_hcaptcha(token, request.remote_addr):
            return render_template('register.html', error='Captcha verificatie mislukt')
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Gebruiker bestaat al')
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))