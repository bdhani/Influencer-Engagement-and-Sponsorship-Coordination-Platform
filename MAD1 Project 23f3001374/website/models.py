from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    niche = db.Column(db.String(60), nullable=False)
    company_name = db.Column(db.String(60), nullable=True)
    reach_yt = db.Column(db.Integer, default=0)
    reach_tw = db.Column(db.Integer, default=0)
    reach_insta = db.Column(db.Integer, default=0)
    reach_meta = db.Column(db.Integer, default=0)
    min_reach = db.Column(db.Integer, default=0)
    flagged = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    profile_pic = db.Column(db.String(255), default="website/static/default.png", nullable=True)
    earnings = db.Column(db.Integer, default=0)
    ratings = db.Column(db.Integer, default=0)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True, foreign_keys='Campaign.sponsor_id')
    ad_requests_sent = db.relationship('AdRequest', foreign_keys='AdRequest.sponsor_id', backref='sponsor', lazy=True)
    ad_requests_received = db.relationship('AdRequest', foreign_keys='AdRequest.influencer_id', backref='influencer', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False, default="No description")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(20), nullable=False, default="Public")
    goals = db.Column(db.Text, nullable=False, default="ALL")
    niche = db.Column(db.String(100), nullable=False, default="General")
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True, foreign_keys='AdRequest.campaign_id')

    def __repr__(self):
        return f'<Campaign {self.name}>'

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.Column(db.String(50), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  
    negotiated_payment = db.Column(db.Float, nullable=True) 
    sponsor_rating = db.Column(db.Float)
    
    def __repr__(self):
        return f'<AdRequest {self.id} - {self.status}>'

    def is_sent_by(self, user):
        return self.sponsor_id == user.id

    def is_received_by(self, user):
        return self.influencer_id == user.id

