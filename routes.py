import os
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import app, db
from models import User, LostItem, FoundItem, Match, ItemCategory
from forms import (RegistrationForm, LoginForm, ReportLostItemForm, 
                  ReportFoundItemForm, SearchItemForm, AdminMatchForm)
from utils import save_image, calculate_match_score, find_potential_matches

# Ensure categories exist in the database
def create_default_categories():
    categories = ['Electronics', 'Clothing', 'Personal Documents', 'Accessories', 'Books', 'Others']
    for category_name in categories:
        if not ItemCategory.query.filter_by(name=category_name).first():
            category = ItemCategory(name=category_name)
            db.session.add(category)
    db.session.commit()

# Home page
@app.route('/')
def home():
    stats = {
        'lost_items': LostItem.query.count(),
        'found_items': FoundItem.query.count(),
        'matches_made': Match.query.filter_by(status='approved').count(),
        'success_rate': 0
    }
    
    # Calculate success rate
    if LostItem.query.count() > 0:
        resolved = LostItem.query.filter_by(status='resolved').count()
        stats['success_rate'] = int((resolved / stats['lost_items']) * 100)
    
    recent_lost = LostItem.query.order_by(LostItem.created_at.desc()).limit(5).all()
    recent_found = FoundItem.query.order_by(FoundItem.created_at.desc()).limit(5).all()
    
    return render_template('index.html', stats=stats, recent_lost=recent_lost, recent_found=recent_found)

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        # Make the first user an admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login failed. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/dashboard/user')
@login_required
def user_dashboard():
    lost_items = LostItem.query.filter_by(user_id=current_user.id).order_by(LostItem.created_at.desc()).all()
    found_items = FoundItem.query.filter_by(user_id=current_user.id).order_by(FoundItem.created_at.desc()).all()
    
    # Get potential matches for user's lost items
    potential_matches = []
    for item in lost_items:
        item_matches = Match.query.filter_by(lost_item_id=item.id).all()
        for match in item_matches:
            if match.status != 'rejected':
                potential_matches.append({
                    'match': match,
                    'lost_item': item,
                    'found_item': match.found_item
                })
    
    return render_template('dashboard/user.html', 
                          title='Dashboard',
                          lost_items=lost_items, 
                          found_items=found_items,
                          potential_matches=potential_matches)

@app.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get counts for dashboard
    stats = {
        'total_users': User.query.count(),
        'total_lost': LostItem.query.count(),
        'total_found': FoundItem.query.count(),
        'pending_matches': Match.query.filter_by(status='pending').count(),
        'approved_matches': Match.query.filter_by(status='approved').count()
    }
    
    # Get recent items
    recent_lost = LostItem.query.order_by(LostItem.created_at.desc()).limit(10).all()
    recent_found = FoundItem.query.order_by(FoundItem.created_at.desc()).limit(10).all()
    
    # Get pending matches for review
    pending_matches = []
    for match in Match.query.filter_by(status='pending').all():
        pending_matches.append({
            'match': match,
            'lost_item': match.lost_item,
            'found_item': match.found_item,
            'lost_by': User.query.get(match.lost_item.user_id).username,
            'found_by': User.query.get(match.found_item.user_id).username
        })
    
    return render_template('dashboard/admin.html', 
                          title='Admin Dashboard',
                          stats=stats,
                          recent_lost=recent_lost,
                          recent_found=recent_found,
                          pending_matches=pending_matches)

# Item routes
@app.route('/items/lost/report', methods=['GET', 'POST'])
@login_required
def report_lost_item():
    form = ReportLostItemForm()
    
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_image(form.image.data, 'lost_items')
        
        lost_item = LostItem(
            title=form.title.data,
            description=form.description.data,
            date_lost=form.date_lost.data,
            location_lost=form.location_lost.data,
            category_id=form.category.data,
            image_path=image_path,
            user_id=current_user.id
        )
        
        db.session.add(lost_item)
        db.session.commit()
        
        # Find potential matches
        potential_matches = find_potential_matches(lost_item)
        for found_item_id, score in potential_matches:
            match = Match(
                lost_item_id=lost_item.id,
                found_item_id=found_item_id,
                match_score=score,
                status='pending'
            )
            db.session.add(match)
        
        db.session.commit()
        
        flash('Your lost item has been reported successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('items/report_lost.html', title='Report Lost Item', form=form)

@app.route('/items/found/report', methods=['GET', 'POST'])
@login_required
def report_found_item():
    form = ReportFoundItemForm()
    
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_image(form.image.data, 'found_items')
        
        found_item = FoundItem(
            title=form.title.data,
            description=form.description.data,
            date_found=form.date_found.data,
            location_found=form.location_found.data,
            category_id=form.category.data,
            image_path=image_path,
            user_id=current_user.id
        )
        
        db.session.add(found_item)
        db.session.commit()
        
        # Check if this found item matches any lost items
        lost_items = LostItem.query.filter_by(status='unresolved').all()
        for lost_item in lost_items:
            score = calculate_match_score(lost_item, found_item)
            if score > 0.5:  # Only create matches with significant similarity
                match = Match(
                    lost_item_id=lost_item.id,
                    found_item_id=found_item.id,
                    match_score=score,
                    status='pending'
                )
                db.session.add(match)
        
        db.session.commit()
        
        flash('Your found item has been reported successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('items/report_found.html', title='Report Found Item', form=form)

@app.route('/items/lost/<int:item_id>')
def view_lost_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    owner = User.query.get(item.user_id)
    
    # Check if there are any approved matches
    matches = Match.query.filter_by(lost_item_id=item.id, status='approved').all()
    matched_items = [match.found_item for match in matches]
    
    return render_template('items/view_item.html', 
                          title=f'Lost Item: {item.title}',
                          item=item,
                          item_type='lost',
                          owner=owner,
                          matches=matched_items,
                          now=datetime.now().date())

@app.route('/items/found/<int:item_id>')
def view_found_item(item_id):
    item = FoundItem.query.get_or_404(item_id)
    finder = User.query.get(item.user_id)
    
    # Check if there are any approved matches
    matches = Match.query.filter_by(found_item_id=item.id, status='approved').all()
    matched_items = [match.lost_item for match in matches]
    
    return render_template('items/view_item.html', 
                          title=f'Found Item: {item.title}',
                          item=item,
                          item_type='found',
                          owner=finder,
                          matches=matched_items,
                          now=datetime.now().date())

@app.route('/items/search', methods=['GET', 'POST'])
def search_items():
    form = SearchItemForm()
    
    results = {
        'lost': [],
        'found': []
    }
    
    if request.method == 'POST' and form.validate():
        # Build query for lost items
        lost_query = LostItem.query
        found_query = FoundItem.query
        
        # Filter by search term
        if form.query.data:
            search_term = f'%{form.query.data}%'
            lost_query = lost_query.filter(
                (LostItem.title.like(search_term)) | 
                (LostItem.description.like(search_term)) |
                (LostItem.location_lost.like(search_term))
            )
            found_query = found_query.filter(
                (FoundItem.title.like(search_term)) | 
                (FoundItem.description.like(search_term)) |
                (FoundItem.location_found.like(search_term))
            )
        
        # Filter by category
        if form.category.data != 0:  # 0 is "All Categories"
            lost_query = lost_query.filter_by(category_id=form.category.data)
            found_query = found_query.filter_by(category_id=form.category.data)
        
        # Filter by status
        if form.status.data == 1:  # Unresolved/Unclaimed
            lost_query = lost_query.filter_by(status='unresolved')
            found_query = found_query.filter_by(status='unclaimed')
        elif form.status.data == 2:  # Resolved/Claimed
            lost_query = lost_query.filter_by(status='resolved')
            found_query = found_query.filter_by(status='claimed')
        
        # Filter by date range
        if form.date_from.data:
            lost_query = lost_query.filter(LostItem.date_lost >= form.date_from.data)
            found_query = found_query.filter(FoundItem.date_found >= form.date_from.data)
        if form.date_to.data:
            lost_query = lost_query.filter(LostItem.date_lost <= form.date_to.data)
            found_query = found_query.filter(FoundItem.date_found <= form.date_to.data)
        
        # Execute queries
        results['lost'] = lost_query.all()
        results['found'] = found_query.all()
    
    return render_template('items/search_items.html', 
                          title='Search Items',
                          form=form,
                          results=results)

# Match routes
@app.route('/matches')
@login_required
def view_matches():
    user_lost_items = LostItem.query.filter_by(user_id=current_user.id).all()
    user_found_items = FoundItem.query.filter_by(user_id=current_user.id).all()
    
    lost_item_matches = []
    for item in user_lost_items:
        matches = Match.query.filter_by(lost_item_id=item.id).all()
        for match in matches:
            lost_item_matches.append({
                'match': match,
                'lost_item': item,
                'found_item': match.found_item,
                'finder': User.query.get(match.found_item.user_id)
            })
    
    found_item_matches = []
    for item in user_found_items:
        matches = Match.query.filter_by(found_item_id=item.id).all()
        for match in matches:
            found_item_matches.append({
                'match': match,
                'found_item': item,
                'lost_item': match.lost_item,
                'owner': User.query.get(match.lost_item.user_id)
            })
    
    return render_template('matches/view_matches.html',
                          title='My Matches',
                          lost_item_matches=lost_item_matches,
                          found_item_matches=found_item_matches)

@app.route('/items/update_status', methods=['POST'])
@login_required
def update_item_status():
    item_id = request.form.get('item_id')
    item_type = request.form.get('item_type')
    new_status = request.form.get('status')
    
    if item_type == 'lost':
        item = LostItem.query.get_or_404(item_id)
        if current_user.id != item.user_id and not current_user.is_admin:
            abort(403)
        item.status = new_status
    elif item_type == 'found':
        item = FoundItem.query.get_or_404(item_id)
        if current_user.id != item.user_id and not current_user.is_admin:
            abort(403)
        item.status = new_status
    else:
        abort(400)
    
    db.session.commit()
    flash(f'Item status updated to {new_status}!', 'success')
    
    if item_type == 'lost':
        return redirect(url_for('view_lost_item', item_id=item_id))
    else:
        return redirect(url_for('view_found_item', item_id=item_id))

@app.route('/admin/matches/<int:match_id>', methods=['POST'])
@login_required
def process_match(match_id):
    if not current_user.is_admin:
        abort(403)
    
    match = Match.query.get_or_404(match_id)
    form = AdminMatchForm()
    
    if form.validate_on_submit():
        match.status = form.action.data
        match.admin_notes = form.notes.data
        match.updated_at = datetime.utcnow()
        
        # If match is approved, update the items' status
        if form.action.data == 'approve':
            lost_item = LostItem.query.get(match.lost_item_id)
            found_item = FoundItem.query.get(match.found_item_id)
            
            lost_item.status = 'resolved'
            found_item.status = 'claimed'
            
            # Also reject any other pending matches for these items
            other_lost_matches = Match.query.filter(
                Match.lost_item_id == lost_item.id,
                Match.id != match.id,
                Match.status == 'pending'
            ).all()
            
            other_found_matches = Match.query.filter(
                Match.found_item_id == found_item.id,
                Match.id != match.id,
                Match.status == 'pending'
            ).all()
            
            for m in other_lost_matches + other_found_matches:
                m.status = 'rejected'
                m.admin_notes = 'Automatically rejected as another match was approved'
        
        db.session.commit()
        flash(f'Match has been {form.action.data}d successfully.', 'success')
    
    return redirect(url_for('admin_dashboard'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
