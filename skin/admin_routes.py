from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import User, Picture, VisitLog
from . import db

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def admin_required():
    if not current_user.is_admin:
        flash('You do not have access to this page.', category='danger')
        return redirect(url_for('main_bp.index'))

@admin_bp.route('/')
def admin_dashboard():
    users = User.query.all()
    pictures = Picture.query.all()
    visit_logs = VisitLog.query.all()
    visit_count = VisitLog.query.count()
    return render_template('admin_dashboard.html', users=users, pictures=pictures, visit_logs=visit_logs, visit_count=visit_count)

@admin_bp.route('/user/<int:user_id>')
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    pictures = Picture.query.filter_by(user_id=user.id).all()
    return render_template('user_detail.html', user=user, pictures=pictures)
