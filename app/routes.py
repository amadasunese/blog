from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app.extensions import db, bcrypt, csrf
import os
from werkzeug.utils import secure_filename
from app.models import User, Post, Category, Advertisement, Comment
from app.forms import PostForm, UpdateAccountForm, LoginForm, RegistrationForm, CategoryForm, AdForm
import os
# from app.forms import CommentForm, ResetPasswordForm, ResetPasswordRequestForm
# from app.token import generate_confirmation_token, confirm_token, generate_token
from flask import current_app
import imghdr
from app.utils.convert import convert_to_paragraphs
from PIL import Image
from app.utils.decorators import admin_required

from flask_mail import Message, Mail
import smtplib
from itsdangerous import URLSafeTimedSerializer
from config import Config

# from utils.email import send_email, mail


from app.forms import RequestResetForm, ResetPasswordForm, ContactForm, CommentForm
from app.utils.email import send_reset_email
from app import mail




main = Blueprint('main', __name__)


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Prepare the email message
        msg = Message(
            subject=f"New Contact Form Submission: {form.subject.data}",
            sender=form.email.data,
            recipients=[current_app.config['MAIL_DEFAULT_RECIPIENT']]
        )
        msg.body = f"Message from {form.name.data} ({form.email.data}):\n\n{form.message.data}"

        # Send the email
        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f"An error occurred while sending your message: {str(e)}", 'danger')

        return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)


@main.route('/')
@main.route('/home')
def home():
    homepage_ads = Advertisement.query.filter_by(location='homepage', is_active=True).first()

    news_page = request.args.get('news_page', 1, type=int)
    opinions_page = request.args.get('opinions_page', 1, type=int)

    # Query for featured posts
    featured_posts = Post.query.filter_by(is_featured=True).order_by(Post.date_posted.desc()).limit(5).all()

    # Filter and order posts by category and date
    news_posts = Post.query.join(Category).filter(Category.name == 'News').order_by(Post.date_posted.desc()).paginate(page=news_page, per_page=5, error_out=False)
    opinion_posts = Post.query.join(Category).filter(Category.name == 'Opinions').order_by(Post.date_posted.desc()).paginate(page=opinions_page, per_page=5, error_out=False)

    # Query for news items to display in the ticker
    ticker_posts = Post.query.join(Category).filter(Category.name == 'News').order_by(Post.date_posted.desc()).paginate(page=news_page, per_page=10, error_out=False)

    # Order latest posts by date
    latest_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()

    # Fetch an active advertisement
    active_ad = Advertisement.query.filter_by(is_active=True).order_by(Advertisement.date_posted.desc()).first()

    return render_template('home.html', 
                           featured_posts=featured_posts, 
                           news_posts=news_posts, 
                           opinion_posts=opinion_posts, 
                           latest_posts=latest_posts,
                           active_ad=active_ad,
                           ticker_posts=ticker_posts,
                           homepage_ads=homepage_ads)



@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/dashboard.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

###############################
#   Password resent routes    #
##############################


@main.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('main.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)



@main.route('/post/new', methods=['GET', 'POST'])
# @login_required
@admin_required
def new_post():
    form = PostForm()

    form.category.choices = [(0, 'Select a category')] + [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        try:
            image_file = None
            if form.image.data:
                image_file = secure_filename(form.image.data.filename)
                upload_path = os.path.join('app/static/featured_images/')

                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                image_path = os.path.join(upload_path, image_file)
                form.image.data.save(image_path)

            category_id = form.category.data if form.category.data != 0 else Category.query.filter_by(name='News').first().id

            formatted_content = convert_to_paragraphs(form.content.data)

            post = Post(
                title=form.title.data,
                content=formatted_content,
                image_file=image_file,
                author=current_user,
                category_id=category_id,
                is_featured=form.is_featured.data
            )

            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while creating the post: {str(e)}', 'danger')

    return render_template(
        'create_post.html',
        categories=form.category.choices,
        title='New Post',
        form=form,
        legend='New Post'
    )

@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
# @login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)

    # Convert content to paragraphs
    formatted_content = convert_to_paragraphs(post.content)

    form = CommentForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to log in to post a comment.', 'warning')
            return redirect(url_for('main.login'))

        comment = Comment(content=form.content.data,
                          author_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been submitted and is pending approval.', 'success')
        return redirect(url_for('main.post', post_id=post.id))

    comments = Comment.query.filter_by(post_id=post.id, approved=True).all()
    return render_template('post.html',
                           title=post.title,
                           post=post,
                           form=form,
                           formatted_content=formatted_content,
                           comments=comments)



    # return render_template('post.html',
    #                        title=post.title,
    #                        formatted_content=formatted_content,
    #                        post=post)

@main.route("/moderate_comments")
# @login_required
@admin_required
def moderate_comments():
    # if not current_user.is_admin:
    #     abort(403)  # For simplicity, assuming an is_admin property for user

    comments = Comment.query.filter_by(approved=False).all()
    return render_template('moderate_comments.html', comments=comments)

@main.route("/approve_comment/<int:comment_id>")
# @login_required
@admin_required
def approve_comment(comment_id):
    # if not current_user.is_admin:
    #     abort(403)

    comment = Comment.query.get_or_404(comment_id)
    comment.approved = True
    db.session.commit()
    flash('Comment has been approved.', 'success')
    return redirect(url_for('main.moderate_comments'))

@main.route("/delete_comment/<int:comment_id>")
# @login_required
@admin_required
def delete_comment(comment_id):
    # if not current_user.is_admin:
    #     abort(403)

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.', 'success')
    return redirect(url_for('main.moderate_comments'))



@main.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
# @login_required
@admin_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    # Adding placeholder as the first choice
    form.category.choices = [(0, 'Select a category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = form.category.data
        post.is_featured = form.is_featured.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.post',
                                post_id=post.id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category_id

    return render_template('create_post.html',
                           title='Update Post',
                           form=form,
                           legend='Update Post',
                           categories=form.category.choices)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
# @login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@main.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@main.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    categories = Category.query.all()
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category has been created!', 'success')
        return redirect(url_for('main.categories'))
    return render_template('categories.html',
                           form=form, 
                           title='Categories',
                           categories=categories)

@main.route('/category/<int:category_id>')
def category_posts(category_id):
    category = Category.query.get_or_404(category_id)
    posts = Post.query.filter_by(category_id=category.id).paginate(per_page=5)
    return render_template('category_posts.html', category=category, posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title='About')

# @main.route('/contact')
# def contact():
#     return render_template('contact.html', title='Contact')

@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@main.route('/manage_ads', methods=['GET', 'POST'])
# @login_required
@admin_required
def manage_ads():
    # Query all ads to display them
    ads = Advertisement.query.all()

    # Initialize the form
    form = AdForm()

    if form.validate_on_submit():
        # Check if an ad is being updated
        ad_id = request.form.get('ad_id')
        ad = Advertisement.query.get(ad_id) if ad_id else None
        
        try:
            # Handle file upload
            image_file = ad.image_file if ad else None
            if form.image.data:
                image_file = secure_filename(form.image.data.filename)
                upload_path = os.path.join('app/static/ads/')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                image_path = os.path.join(upload_path, image_file)
                
                # Resize and save the image
                image = Image.open(form.image.data)
                image_width = 200 if image.width < 250 else 300
                image_height = int(image.height * (image_width / image.width))
                image = image.resize((image_width, image_height), Image.LANCZOS)
                image.save(image_path)

            # Create or update an ad
            if ad:
                ad.ad_code = form.ad_code.data
                ad.image_file = image_file
                ad.embed_link = form.embed_link.data
                ad.is_active = form.is_active.data
            else:
                ad = Advertisement(ad_code=form.ad_code.data,
                                   image_file=image_file,
                                   embed_link=form.embed_link.data,
                                   is_active=form.is_active.data)
                db.session.add(ad)

            db.session.commit()
            flash('Ad has been updated!' if ad_id else 'Ad has been created!', 'success')
            return redirect(url_for('main.ads'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('manage_ads.html', form=form, ads=ads)

@main.route('/advertisement/delete/<int:ad_id>', methods=['POST'])
# @login_required
@admin_required
def delete_advertisement(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    try:
        db.session.delete(ad)
        db.session.commit()
        flash('Ad has been deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('main.manage_ads'))

@main.route('/ads', methods=['GET', 'POST'])
@login_required
def ads():
    # Query all ads to display them
    ads = Advertisement.query.all()

    return render_template('ads.html', ads=ads)

# In your routes.py
from flask import render_template, redirect, url_for
from app.models import Advertisement

@main.route('/ad_view/<int:ad_id>')
def ad_view(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    ad.increment_view()
    return redirect(url_for('main.home'))


@main.route('/ad_click/<int:ad_id>')
def ad_click(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    ad.increment_click()
    return redirect(ad.embed_link or url_for('main.home'))


# Home page ad placement

@main.route('/homepage_ads_view/<int:ad_id>')
def homepage_ads_view(ad_id):
    homepage_ads = Advertisement.query.get_or_404(ad_id)
    homepage_ads.increment_view()
    return redirect(url_for('main.home'))


@main.route('/homepage_ads_click/<int:ad_id>')
def homepage_ads_click(ad_id):
    homepage_ads = Advertisement.query.get_or_404(ad_id)
    homepage_ads.increment_click()
    return redirect(homepage_ads.embed_link or url_for('main.home'))


@main.route('/manage_homepage_ad', methods=['GET', 'POST'])
# @login_required
@admin_required
def manage_homepage_ad():
    # Query the current homepage ad
    homepage_ads = Advertisement.query.filter_by(location='homepage').first()

    # Initialize the form
    form = AdForm()

    if form.validate_on_submit():
        # Check if an ad is being updated
        ad_id = homepage_ads.id if homepage_ads else None

        try:
            # Handle file upload
            image_file = homepage_ads.image_file if homepage_ads else None
            if form.image.data:
                image_file = secure_filename(form.image.data.filename)
                upload_path = os.path.join('app/static/ads/')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                image_path = os.path.join(upload_path, image_file)
                
                # Resize and save the image
                image = Image.open(form.image.data)
                image_width = 200 if image.width < 250 else 900
                image_height = int(image.height * (image_width / image.width))
                image = image.resize((image_width, image_height), Image.LANCZOS)
                image.save(image_path)

            # Create or update an ad
            if homepage_ads:
                homepage_ads.ad_code = form.ad_code.data
                homepage_ads.image_file = image_file
                homepage_ads.embed_link = form.embed_link.data
                homepage_ads.is_active = form.is_active.data
            else:
                homepage_ads = Advertisement(
                    ad_code=form.ad_code.data,
                    image_file=image_file,
                    embed_link=form.embed_link.data,
                    is_active=form.is_active.data,
                    location='homepage'
                )
                db.session.add(homepage_ads)

            db.session.commit()
            flash('Ad has been updated!' if ad_id else 'Ad has been created!', 'success')
            return redirect(url_for('main.manage_homepage_ad'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('manage_homepage_ad.html',
                           form=form,
                           homepage_ads=homepage_ads)