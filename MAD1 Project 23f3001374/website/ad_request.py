from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Campaign, AdRequest
from . import db

ad_request = Blueprint('ad_request', __name__)

@ad_request.route('/create_ad_request', methods=['GET', 'POST'])
@login_required
def create_ad_request():
    if request.method == 'POST':
        campaign_id = request.form.get('campaign_id')
        influencer_id = request.form.get('influencer_id')
        sponsor_id = request.form.get('sponsor_id')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        new_ad_request = AdRequest(campaign_id=campaign_id, influencer_id=influencer_id, sponsor_id=sponsor_id, requirements=requirements, payment_amount=payment_amount, creator=current_user.id, status='Pending')
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request created successfully!', category='success')
        return redirect(url_for('ad_request.view_ad_requests'))
    
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    campaigns_influencer = Campaign.query.all()
    all_influencers = User.query.filter_by(role='Influencer').all()
    all_sponsors = User.query.filter_by(role='Sponsor').all()
    c_influencer = User.query.filter_by(id=current_user.id).all()
    c_sponsor = User.query.filter_by(id=current_user.id).all()
    return render_template('create_ad_request.html', campaigns=campaigns, campaigns_influencer=campaigns_influencer, all_influencers=all_influencers, all_sponsors=all_sponsors, c_influencer=c_influencer, c_sponsor=c_sponsor, user=current_user)

@ad_request.route('/update_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def update_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        ad_request.requirements = request.form.get('requirements')
        ad_request.payment_amount = request.form.get('payment_amount')
        ad_request.status = request.form.get('status')
        db.session.commit()
        flash('Ad request updated successfully!', category='success')
        return redirect(url_for('ad_request.view_ad_requests'))
    return render_template('update_ad_request.html', ad_request=ad_request, user=current_user)

@ad_request.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', category='success')
    return redirect(url_for('ad_request.view_ad_requests'))

@ad_request.route('/view_ad_requests')
@login_required
def view_ad_requests():
    if current_user.role == 'Sponsor':
        sent_ad_requests = AdRequest.query.filter_by(creator=current_user.id).all()
        received_ad_requests = AdRequest.query.filter(AdRequest.sponsor_id == current_user.id, AdRequest.creator != current_user.id).all()
    elif current_user.role == 'Influencer':
        sent_ad_requests = AdRequest.query.filter_by(creator=current_user.id).all()
        received_ad_requests = AdRequest.query.filter(AdRequest.influencer_id == current_user.id, AdRequest.creator != current_user.id).all()
    return render_template('view_ad_requests.html', sent_ad_requests=sent_ad_requests, received_ad_requests=received_ad_requests, user=current_user)

@ad_request.route('/accept_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Ad request accepted!', category='success')
    return redirect(url_for('ad_request.view_ad_requests'))

@ad_request.route('/reject_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Rejected'
    db.session.commit()
    flash('Ad request rejected!', category='success')
    return redirect(url_for('ad_request.view_ad_requests'))

@ad_request.route('/negotiate_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        ad_request.negotiated_payment = request.form.get('payment_amount')
        ad_request.status = 'Negotiating'
        db.session.commit()
        flash('Negotiation request sent to sponsor!', category='success')
        return redirect(url_for('ad_request.view_ad_requests'))
    return render_template('negotiate_ad_request.html', ad_request=ad_request, user=current_user)

@ad_request.route('/submit_rating/<int:ad_request_id>', methods=['POST'])
def submit_rating(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        if ad_request.status == 'Completed':
            flash('This ad request has already been completed.', category='error')
            return redirect(url_for('views.sponsor_dashboard'))
        rating = float(request.form.get('sponsor_rating'))
        ad_request.sponsor_rating = rating
        ad_request.status = 'Completed'
        db.session.commit()
        influencer = ad_request.influencer
        influencer_ratings = [r.sponsor_rating for r in influencer.ad_requests_received if r.status == 'Completed']
        influencer.ratings = sum(influencer_ratings) / len(influencer_ratings)
        if ad_request.negotiated_payment:
            influencer.earnings += (ad_request.negotiated_payment)
        else:
            influencer.earnings += (ad_request.payment_amount)
        db.session.commit()
        flash('Rating submitted and earnings updated.', category='success')
        return redirect(url_for('views.sponsor_dashboard'))
    
