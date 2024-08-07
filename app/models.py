from datetime import datetime
from app.extensions import db
from flask_login import UserMixin
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(
                token,
                salt=current_app.config['SECURITY_PASSWORD_SALT'],
                max_age=expires_sec
            )['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    posts = db.relationship('Post', back_populates='category')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', back_populates='posts')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_code = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(20), nullable=True)
    embed_link = db.Column(db.String(255), nullable=True)  # Add this field
    is_active = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100), nullable=True)

    # Increment view count
    def increment_view(self):
        self.views += 1
        db.session.commit()

    # Increment click count
    def increment_click(self):
        self.clicks += 1
        db.session.commit()

    def __repr__(self):
        return f"Advertisement('{self.id}', '{self.image_file}', '{self.is_active}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)  # Moderation status
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"