from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from .models import File, User, db
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    return render_template("index.html")

@main_bp.route('/voorpagina')
@login_required
def voorpagina():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Get user's files
    files = File.query.filter_by(user_id=user_id).order_by(File.upload_date.desc()).all()
    
    # Calculate storage
    total_storage_bytes = sum(f.file_size for f in files)
    total_storage_gb = total_storage_bytes / (1024 * 1024 * 1024)
    max_storage_gb = 15
    available_storage_gb = max_storage_gb - total_storage_gb
    storage_percentage = (total_storage_gb / max_storage_gb) * 100
    
    # Format files for display
    files_display = []
    for file in files:
        files_display.append({
            'id': file.id,
            'filename': file.original_filename,
            'size': file.get_size_formatted(),
            'upload_date': file.upload_date.strftime('%d-%m-%Y %H:%M')
        })
    
    return render_template(
        "voorpagina.html",
        username=user.username,
        files=files_display,
        files_count=len(files),
        used_storage_gb=f"{total_storage_gb:.2f}",
        available_storage_gb=f"{available_storage_gb:.2f}",
        storage_percentage=min(storage_percentage, 100)
    )

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('Geen bestand geselecteerd', 'error')
        return redirect(url_for('main.voorpagina'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Geen bestand geselecteerd', 'error')
        return redirect(url_for('main.voorpagina'))
    
    if file and allowed_file(file.filename):
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            flash('Bestand is te groot (max 100 MB)', 'error')
            return redirect(url_for('main.voorpagina'))
        
        # Check total storage
        user_id = session.get('user_id')
        user_files = File.query.filter_by(user_id=user_id).all()
        total_storage = sum(f.file_size for f in user_files)
        
        if total_storage + file_size > 15 * 1024 * 1024 * 1024:  # 15 GB
            flash('Opslaglimiet bereikt', 'error')
            return redirect(url_for('main.voorpagina'))
        
        # Save file
        original_filename = secure_filename(file.filename)
        filename = f"{user_id}_{datetime.now().timestamp()}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Save to database
        new_file = File(
            filename=filename,
            original_filename=original_filename,
            file_size=file_size,
            user_id=user_id
        )
        db.session.add(new_file)
        db.session.commit()
        
        flash('Bestand succesvol geüpload!', 'success')
        return redirect(url_for('main.voorpagina'))
    
    flash('Bestandstype niet toegestaan', 'error')
    return redirect(url_for('main.voorpagina'))

@main_bp.route('/download/<int:file_id>')
@login_required
def download(file_id):
    user_id = session.get('user_id')
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not file:
        flash('Bestand niet gevonden', 'error')
        return redirect(url_for('main.voorpagina'))
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=file.original_filename)
    
    flash('Bestand niet gevonden op server', 'error')
    return redirect(url_for('main.voorpagina'))

@main_bp.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete(file_id):
    user_id = session.get('user_id')
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not file:
        flash('Bestand niet gevonden', 'error')
        return redirect(url_for('main.voorpagina'))
    
    # Delete from filesystem
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Delete from database
    db.session.delete(file)
    db.session.commit()
    
    flash('Bestand verwijderd', 'success')
    return redirect(url_for('main.voorpagina'))

@main_bp.route('/login')
def login_page():
    return render_template("login.html")