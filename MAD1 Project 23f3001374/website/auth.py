import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@auth.route('/user_login', methods=["GET", 'POST'])
def userlogin():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")
        if role == 'Admin' and username == 'Admin' and password == 'bdhani26':
            flash("Logged in as Admin successfully!", category="success")
            return redirect( url_for('views.admin_dashboard'))
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                if role == user.role and role == 'Influencer':
                    return redirect('/influencer_dashboard')
                elif role == user.role and role == 'Sponsor':
                    return redirect('/sponsor_dashboard')
            else:
                flash("Incorrect Password. Try again", category="error")
        else:
            flash("Username does not exist. Register yourself", category="error")
    return render_template("login_user.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.userlogin"))

@auth.route('/ireg', methods=["GET", 'POST'])
def influencer_register():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        niche = request.form.get("niche")
        profile_pic = request.files.get("profile_pic")
        reach_yt = request.form.get("reach_yt") or 0
        reach_tw = request.form.get("reach_tw") or 0
        reach_meta = request.form.get("reach_meta") or 0
        reach_insta = request.form.get("reach_insta") or 0
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists! Try another", category="error")
        if len(username) < 5:
            flash('Username must be a minimum of 5 characters', category="error")
        elif len(password1) < 7:
            flash('Password must be a minimum of 7 characters', category="error")
        elif password1 != password2:
            flash('Confirmed password does not match', category="error")
        else:
            filename = "default.png"
            if profile_pic:
                if allowed_file(profile_pic.filename):
                    filename = secure_filename(profile_pic.filename)
                    profile_pic_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    profile_pic.save(profile_pic_path)

            new_influencer = User(username=username, 
                                  password=generate_password_hash(password2, method="pbkdf2:sha256"), 
                                  role='Influencer', 
                                  niche=niche, 
                                  reach_yt=int(reach_yt), 
                                  reach_tw=int(reach_tw), 
                                  reach_meta=int(reach_meta), 
                                  reach_insta=int(reach_insta),
                                  min_reach=int(reach_yt) + int(reach_tw) + int(reach_meta) + int(reach_insta), 
                                  company_name="Individual", 
                                  flagged=False, 
                                  active=True, 
                                  profile_pic=filename, 
                                  earnings=0, 
                                  ratings=0)
            db.session.add(new_influencer)
            db.session.commit()
            flash("Account created successfully!", category="success")
            return redirect('/user_login')
    return render_template("register_influencer.html", user=current_user)

@auth.route('/sreg', methods=["GET", 'POST'])
def sponsor_register():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        niche = request.form.get("niche")
        company_name = request.form.get("company_name")
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists! Try another", category="error")
        if len(username) < 5:
            flash('Username must be a minimum of 5 characters', category="error")
        elif len(password1) < 7:
            flash('Password must be a minimum of 7 characters', category="error")
        elif password1 != password2:
            flash('Confirmed password does not match', category="error")
        else:
            filename = "default.png"
            new_sponsor = User(username=username, 
                                  password=generate_password_hash(password2, method="pbkdf2:sha256"), 
                                  role='Sponsor', 
                                  niche=niche, 
                                  reach_yt=0, 
                                  reach_tw=0, 
                                  reach_meta=0, 
                                  reach_insta=0,
                                  min_reach=0, 
                                  company_name=company_name, 
                                  flagged=False, 
                                  active=True, 
                                  profile_pic=filename, 
                                  earnings=0, 
                                  ratings=0)
            db.session.add(new_sponsor)
            db.session.commit()
            flash("Account created successfully!", category="success")
            return redirect('/user_login')
    return render_template("register_sponsor.html", user=current_user)

@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role != 'Influencer':
        flash("You are not authorized to edit this profile.", category="error")
        return redirect('/user_login')

    if request.method == 'POST':
        profile_pic = request.files.get("profile_pic")
        reach_yt = request.form.get("reach_yt")
        reach_tw = request.form.get("reach_tw")
        reach_meta = request.form.get("reach_meta")
        reach_insta = request.form.get("reach_insta")

        if profile_pic and allowed_file(profile_pic.filename):
                filename = secure_filename(profile_pic.filename)
                profile_pic.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_pic=filename

        current_user.reach_yt = int(reach_yt)
        current_user.reach_tw = int(reach_tw)
        current_user.reach_meta = int(reach_meta)
        current_user.reach_insta = int(reach_insta)
        current_user.min_reach = current_user.reach_yt + current_user.reach_tw + current_user.reach_meta + current_user.reach_insta
        db.session.commit()

        flash('Profile updated successfully!', category="success")
        return redirect(url_for('views.influencer_dashboard'))  
    return render_template('edit_profile.html', user=current_user)

@auth.route('/flag_user/<int:user_id>', methods=['POST'])
def flag_user(user_id):
    user_to_flag = User.query.filter_by(id=user_id).first()
    if user_to_flag:
        user_to_flag.flagged = True
        db.session.commit()
        flash('User has been flagged', category='success')
    else:
        flash('User not found', category='error')
    return redirect(url_for('views.admin_dashboard'))

