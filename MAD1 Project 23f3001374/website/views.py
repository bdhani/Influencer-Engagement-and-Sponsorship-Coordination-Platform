from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, send_from_directory, current_app
from flask_login import login_required, current_user
from .models import User, Campaign, AdRequest
from . import db
import os 

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'Influencer':
        flash('Unauthorized access!', category='error')
        return redirect(url_for('views.home'))
    sent_ad_requests = AdRequest.query.filter_by(creator=current_user.id).all()
    received_ad_requests = AdRequest.query.filter(AdRequest.influencer_id == current_user.id, AdRequest.creator != current_user.id).all()
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    return render_template('influencer_dashboard.html', 
                           sent_ad_requests=sent_ad_requests, 
                           received_ad_requests=received_ad_requests,
                           ad_requests=ad_requests, 
                           user=current_user)

@views.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
    if current_user.role != 'Sponsor':
        flash('Unauthorized access!', category='error')
        return redirect(url_for('views.home'))

    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    sent_ad_requests = AdRequest.query.filter_by(creator=current_user.id).all()
    received_ad_requests = AdRequest.query.filter(AdRequest.sponsor_id == current_user.id, AdRequest.creator != current_user.id).all()
    ad_requests = AdRequest.query.filter_by(sponsor_id=current_user.id).all()
    return render_template('sponsor_dashboard.html', 
                           campaigns=campaigns, 
                           sent_ad_requests=sent_ad_requests, 
                           received_ad_requests=received_ad_requests,
                           ad_requests=ad_requests, 
                           user=current_user)

@views.route('/admin_dashboard')
def admin_dashboard():
    active_users = User.query.filter_by(active=True).count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequest.query.count()
    flagged_sponsors = User.query.filter_by(role='Sponsor', flagged=True).count()
    flagged_influencers = User.query.filter_by(role='Influencer', flagged=True).count()
    sponsors = User.query.filter_by(role='Sponsor').count()
    influencers = User.query.filter_by(role='Influencer').count()
    accepted_adrequests = AdRequest.query.filter_by(status='Accepted').count()
    pending_adrequests = AdRequest.query.filter_by(status='Pending').count()
    completed_adrequests = AdRequest.query.filter_by(status='Completed').count()
    negotiating_adrequests = AdRequest.query.filter_by(status='Negotiating').count()
    rejected_adrequests = AdRequest.query.filter_by(status='Rejected').count()
    iniche_data = db.session.query(User.niche, db.func.count(User.id)).filter(User.role == 'Influencer').group_by(User.niche).all()
    iniches = [niche for niche, count in iniche_data]
    incounts = [count for niche, count in iniche_data]
    cniche_data = db.session.query(Campaign.niche, db.func.count(Campaign.id)).group_by(Campaign.niche).all()
    cniches = [niche for niche, count in cniche_data]
    cncounts = [count for niche, count in cniche_data]
    public_campaigns = Campaign.query.filter_by(visibility='Public').count()
    private_campaigns = Campaign.query.filter_by(visibility='Private').count()
    return render_template('admin_dashboard.html', 
                            active_users=active_users, 
                            total_campaigns=total_campaigns, 
                            total_ad_requests=total_ad_requests,
                            flagged_sponsors=flagged_sponsors,
                            flagged_influencers=flagged_influencers,
                            sponsors=sponsors,
                            influencers=influencers,
                            accepted_adrequests=accepted_adrequests,
                            pending_adrequests=pending_adrequests,
                            completed_adrequests=completed_adrequests,
                            negotiating_adrequests=negotiating_adrequests,
                            rejected_adrequests=rejected_adrequests,
                            iniches=iniches,
                            incounts=incounts,
                            cniches=cniches,
                            cncounts=cncounts,
                            public_campaigns=public_campaigns,
                            private_campaigns=private_campaigns,
                            user=current_user)

@views.route('/search_influencers', methods=['GET', 'POST'])
@login_required
def search_influencers():
    if request.method == 'POST':
        niche = request.form.get('niche')
        min_reach = request.form.get('min_reach')
        influencers = User.query.filter(User.role == 'Influencer', User.niche.contains(niche), User.min_reach >= min_reach).all()
        return render_template('search_results.html', users=influencers, user=current_user)
    return render_template('search_influencers.html',  user=current_user)

@views.route('/search_campaigns', methods=['GET', 'POST'])
@login_required
def search_campaigns():
    if request.method == 'POST':
        niche = request.form.get('niche')
        budget_range = request.form.get('budget')
        if budget_range == '20000+':
            min_budget = 20000
            max_budget = None
        else:
            min_budget, max_budget = map(int, budget_range.split('-'))
        campaigns_query = Campaign.query.filter(Campaign.niche.contains(niche))
        if max_budget:
            campaigns = campaigns_query.filter(Campaign.budget.between(min_budget, max_budget)).all()
        else:
            campaigns = campaigns_query.filter(Campaign.budget >= min_budget).all()
        return render_template('search_results.html', campaigns=campaigns, user=current_user)
    return render_template('search_campaigns.html',  user=current_user)

@views.route('/view_full_profile/<int:user_id>')
def view_full_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('view_full_profile.html', user=user)

@views.route('/profile_pic/<filename>')
def profile_pic(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'profile_pic'), filename)

@views.route('/view_sponsor_profiles')
def view_sponsor_profiles():
    sponsors = User.query.filter_by(role='Sponsor').all()
    return render_template('view_sponsor_profiles.html', sponsors=sponsors)

@views.route('/view_influencer_profiles')
def view_influencer_profiles():
    influencers = User.query.filter_by(role='Influencer').all()
    return render_template('view_influencer_profiles.html', influencers=influencers)

@views.route('/view_campaigns_admin')
def view_campaigns_admin():
    campaigns = Campaign.query.all()
    return render_template('view_campaigns_admin.html', campaigns=campaigns)


