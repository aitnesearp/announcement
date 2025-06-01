from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///announcements.db'
db = SQLAlchemy(app)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_url = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    checked = db.Column(db.Boolean, default=False)

class EmailSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    selector = db.Column(db.String(200), nullable=False)
    last_checked = db.Column(db.DateTime)

def send_email(subject, message, recipient):
    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def check_announcements():
    sites = Site.query.all()
    for site in sites:
        try:
            response = requests.get(site.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            announcements = soup.select(site.selector)
            
            for announcement in announcements:
                title = announcement.get_text(strip=True)
                date = datetime.now()
                
                existing = Announcement.query.filter_by(
                    site_url=site.url,
                    title=title
                ).first()
                
                if not existing:
                    new_announcement = Announcement(
                        site_url=site.url,
                        title=title,
                        date=date,
                        checked=False
                    )
                    db.session.add(new_announcement)
                    db.session.commit()
                    
                    # Send email to all subscribers
                    subscribers = EmailSubscription.query.all()
                    for subscriber in subscribers:
                        send_email(
                            f"새 공지사항: {title}",
                            f"새로운 공지사항이 등록되었습니다:\n\n{title}\n\n{site.url}",
                            subscriber.email
                        )
            
            site.last_checked = datetime.now()
            db.session.commit()
            
        except Exception as e:
            print(f"Error checking site {site.url}: {e}")

@app.route('/api/sites', methods=['GET', 'POST'])
def manage_sites():
    if request.method == 'POST':
        data = request.json
        site = Site(
            url=data['url'],
            selector=data['selector']
        )
        db.session.add(site)
        db.session.commit()
        return jsonify({'message': 'Site added successfully'}), 201
    
    sites = Site.query.all()
    return jsonify([{
        'id': site.id,
        'url': site.url,
        'selector': site.selector,
        'last_checked': site.last_checked
    } for site in sites])

@app.route('/api/sites/<int:site_id>', methods=['DELETE'])
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    return jsonify({'message': 'Site deleted successfully'})

@app.route('/api/subscriptions', methods=['POST', 'DELETE'])
def manage_subscriptions():
    if request.method == 'POST':
        email = request.json['email']
        subscription = EmailSubscription(email=email)
        db.session.add(subscription)
        db.session.commit()
        return jsonify({'message': 'Subscription added successfully'}), 201
    
    if request.method == 'DELETE':
        email = request.json['email']
        subscription = EmailSubscription.query.filter_by(email=email).first_or_404()
        db.session.delete(subscription)
        db.session.commit()
        return jsonify({'message': 'Subscription removed successfully'})

if __name__ == '__main__':
    db.create_all()
    schedule.every(1).minutes.do(check_announcements)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
