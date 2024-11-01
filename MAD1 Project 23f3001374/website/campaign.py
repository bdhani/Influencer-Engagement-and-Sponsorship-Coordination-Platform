from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Campaign
from . import db
from datetime import datetime

campaign = Blueprint('campaign', __name__)

@campaign.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        budget = request.form.get('budget')
        niche = request.form.get('niche')
        visibility = request.form.get('visibility')
        goals = request.form.get('goals')
        new_campaign = Campaign(name=name, start_date=start_date, end_date=end_date, budget=budget, niche=niche, visibility=visibility, goals=goals, sponsor_id=current_user.id)
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', category='success')
        return redirect(url_for('campaign.view_campaigns'))
    return render_template('create_campaign.html',user=current_user)

@campaign.route('/update_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        campaign.name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        campaign.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        campaign.budget = request.form.get('budget')
        campaign.niche = request.form.get('niche')
        campaign.visibility = request.form.get('visibility')
        campaign.goals = request.form.get('goals')
        db.session.commit()
        flash('Campaign updated successfully!', category='success')
        return redirect(url_for('campaign.view_campaigns'))
    return render_template('update_campaign.html', campaign=campaign, user=current_user)

@campaign.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', category='success')
    return redirect(url_for('campaign.view_campaigns'))

@campaign.route('/view_campaigns')
@login_required
def view_campaigns():
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    return render_template('view_campaigns.html', campaigns=campaigns,user=current_user)
