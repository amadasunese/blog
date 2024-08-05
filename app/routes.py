from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app.extensions import db, bcrypt, csrf
import os
from werkzeug.utils import secure_filename
from app.models import User, Post, Category, Advertisement
from app.forms import PostForm, UpdateAccountForm, LoginForm, RegistrationForm, CategoryForm, AdForm
import os


main = Blueprint('main', __name__)

# @main.route('/')
# def home():
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
#     return render_template('home.html', posts=posts)

# @main.route('/')
# @main.route('/home')
# def home():
#     news_page = request.args.get('news_page', 1, type=int)
#     opinions_page = request.args.get('opinions_page', 1, type=int)

#     featured_posts = Post.query.filter_by(is_featured=True).limit(5).all()
#     news_posts = Post.query.filter_by(category='News').paginate(page=news_page, per_page=5)
#     opinion_posts = Post.query.filter_by(category='Opinions').paginate(page=opinions_page, per_page=5)
#     latest_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()

#     return render_template('home.html', 
#                            featured_posts=featured_posts, 
#                            news_posts=news_posts, 
#                            opinion_posts=opinion_posts, 
#                            latest_posts=latest_posts)


# @main.route('/')
# @main.route('/home')
# def home():
#     news_page = request.args.get('news_page', 1, type=int)
#     opinions_page = request.args.get('opinions_page', 1, type=int)

#     # Get category instances
#     news_category = Category.query.filter_by(name='News').first()
#     opinions_category = Category.query.filter_by(name='Opinions').first()

#     # Ensure category exists before querying and handle NoneType for pagination
#     news_posts = None
#     if news_category:
#         news_posts = Post.query.filter_by(category=news_category).paginate(page=news_page, per_page=5)

#     opinion_posts = None
#     if opinions_category:
#         opinion_posts = Post.query.filter_by(category=opinions_category).paginate(page=opinions_page, per_page=5)

#     featured_posts = Post.query.filter_by(is_featured=True).limit(5).all()
#     latest_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()

#     return render_template('home.html', 
#                            featured_posts=featured_posts, 
#                            news_posts=news_posts, 
#                            opinion_posts=opinion_posts, 
#                            latest_posts=latest_posts)



# @main.route('/')
# @main.route('/home')
# def home():
#     news_page = request.args.get('news_page', 1, type=int)
#     opinions_page = request.args.get('opinions_page', 1, type=int)

#     featured_posts = Post.query.filter_by(is_featured=True).limit(5).all()

#     # Ensure these queries return paginated objects
#     news_posts = Post.query.filter_by(category='News').paginate(page=news_page, per_page=5, error_out=False)
#     opinion_posts = Post.query.filter_by(category='Opinions').paginate(page=opinions_page, per_page=5, error_out=False)

#     latest_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()

#     return render_template('home.html', 
#                            featured_posts=featured_posts, 
#                            news_posts=news_posts, 
#                            opinion_posts=opinion_posts, 
#                            latest_posts=latest_posts)


# @main.route('/')
# @main.route('/home')
# def home():
#     news_page = request.args.get('news_page', 1, type=int)
#     opinions_page = request.args.get('opinions_page', 1, type=int)

#     # Query for featured posts
#     featured_posts = Post.query.filter_by(is_featured=True).limit(5).all()

#     # Correctly filter posts by category using a join or by accessing the category relationship
#     news_posts = Post.query.join(Category).filter(Category.name == 'News').paginate(page=news_page, per_page=5, error_out=False)
#     opinion_posts = Post.query.join(Category).filter(Category.name == 'Opinions').paginate(page=opinions_page, per_page=5, error_out=False)

#     latest_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    

#     return render_template('home.html', 
#                            featured_posts=featured_posts, 
#                            news_posts=news_posts, 
#                            opinion_posts=opinion_posts, 
#                            latest_posts=latest_posts)


@main.route('/')
@main.route('/home')
def home():
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
                           ticker_posts=ticker_posts)



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

# @main.route('/post/new', methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         post = Post(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('main.home'))
#     return render_template('create_post.html', title='New Post', form=form, legend='New Post')


# @main.route('/post/new', methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         # Handle file upload
#         if form.image.data:
#             image_file = secure_filename(form.image.data.filename)
#             image_path = os.path.join('static/featured_images/', image_file)
#             form.image.data.save(image_path)
#             form.image.data.save(os.path.join('static/featured_images/', image_file))
#         else:
#             image_file = None

#         post = Post(title=form.title.data, content=form.content.data, image_file=image_file, author=current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('main.home'))
#     return render_template('create_post.html', title='New Post', form=form, legend='New Post')


# @main.route('/post/new', methods=['GET', 'POST'])
# @login_required
# def new_post():
#     # category = Category.query.all()
#     form = PostForm()
#     form.category.choices = [(c.id, c.name) for c in Category.query.all()]
#     if form.validate_on_submit():
#         # Handle file upload
#         if form.image.data:
#             # Secure the filename
#             image_file = secure_filename(form.image.data.filename)
#             # Define the upload path
#             upload_path = os.path.join('app/static/featured_images/')
            
#             # Ensure the directory exists
#             if not os.path.exists(upload_path):
#                 os.makedirs(upload_path)
            
#             # Save the file
#             image_path = os.path.join(upload_path, image_file)
#             form.image.data.save(image_path)
#         else:
#             image_file = None

#         # Create the post object
#         post = Post(
#             title=form.title.data,
#             content=form.content.data,
#             image_file=image_file,
#             author=current_user,
#             category_id=form.category.choices,
#             is_featured=form.is_featured.data)
        

        
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('main.home'))
#     return render_template('create_post.html',
#                            categories=form.category.choices,
#                            title='New Post',
#                            form=form,
#                            legend='New Post')




from app.utils import convert_to_paragraphs  # Import your utility function

@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    # Adding placeholder as the first choice
    form.category.choices = [(0, 'Select a category')] + [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        try:
            # Handle file upload
            image_file = None
            if form.image.data:
                # Secure the filename
                image_file = secure_filename(form.image.data.filename)
                # Define the upload path
                upload_path = os.path.join('app/static/featured_images/')

                # Ensure the directory exists
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                # Save the file
                image_path = os.path.join(upload_path, image_file)
                form.image.data.save(image_path)

            # Determine category: default to 'News' if no category is selected
            category_id = form.category.data if form.category.data != 0 else Category.query.filter_by(name='News').first().id

            # Convert content to paragraphs
            formatted_content = convert_to_paragraphs(form.content.data)

            # Create the post object
            post = Post(
                title=form.title.data,
                content=formatted_content,  # Store the formatted content
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
            # Handle any errors that occur
            db.session.rollback()
            flash(f'An error occurred while creating the post: {str(e)}', 'danger')

    return render_template(
        'create_post.html',
        categories=form.category.choices,
        title='New Post',
        form=form,
        legend='New Post'
    )

# @main.route('/post/new', methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()

#     # Adding placeholder as the first choice
#     form.category.choices = [(0, 'Select a category')] + [(c.id, c.name) for c in Category.query.all()]

#     if form.validate_on_submit():
#         try:
#             # Handle file upload
#             image_file = None
#             if form.image.data:
#                 # Secure the filename
#                 image_file = secure_filename(form.image.data.filename)
#                 # Define the upload path
#                 upload_path = os.path.join('app/static/featured_images/')

#                 # Ensure the directory exists
#                 if not os.path.exists(upload_path):
#                     os.makedirs(upload_path)

#                 # Save the file
#                 image_path = os.path.join(upload_path, image_file)
#                 form.image.data.save(image_path)

#             # Determine category: default to 'News' if no category is selected
#             category_id = form.category.data if form.category.data != 0 else Category.query.filter_by(name='News').first().id

#             # Create the post object
#             post = Post(
#                 title=form.title.data,
#                 content=form.content.data,
#                 image_file=image_file,
#                 author=current_user,
#                 category_id=category_id,
#                 is_featured=form.is_featured.data
#             )

#             db.session.add(post)
#             db.session.commit()
#             flash('Your post has been created!', 'success')
#             return redirect(url_for('main.home'))

#         except Exception as e:
#             # Handle any errors that occur
#             db.session.rollback()
#             flash(f'An error occurred while creating the post: {str(e)}', 'danger')

#     return render_template('create_post.html',
#                            categories=form.category.choices,
#                            title='New Post',
#                            form=form,
#                            legend='New Post')

@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)

    # Convert content to paragraphs
    formatted_content = convert_to_paragraphs(post.content)


    return render_template('post.html',
                           title=post.title,
                           formatted_content=formatted_content,
                           post=post)

# @main.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
# @login_required
# def update_post(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author != current_user:
#         abort(403)
#     form = PostForm()
#     if form.validate_on_submit():
#         post.title = form.title.data
#         post.content = form.content.data
#         db.session.commit()
#         flash('Your post has been updated!', 'success')
#         return redirect(url_for('main.post', post_id=post.id))
#     elif request.method == 'GET':
#         form.title.data = post.title
#         form.content.data = post.content
#     return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@main.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
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
@login_required
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

@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

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





# @main.route('/manage_ads', methods=['GET', 'POST'])
# @login_required
# def manage_ads():
#     form = AdForm()
#     ads = Advertisement.query.all()  # Query all ads to display them

#     if form.validate_on_submit():
#         try:
#             image_file = None
#             if form.image.data:
#                 image_file = secure_filename(form.image.data.filename)
#                 # Define the upload path
#                 upload_path = os.path.join('app/static/ads/')

#                 # Ensure the directory exists
#                 if not os.path.exists(upload_path):
#                     os.makedirs(upload_path)

#                 # Save the file
#                 image_path = os.path.join(upload_path, image_file)
#                 form.image.data.save(image_path)

#             # Create or update an ad
#             ad = Advertisement(ad_code=form.ad_code.data,
#                                image_file=image_file,
#                                is_active=form.is_active.data)
#             db.session.add(ad)
#             db.session.commit()
#             flash('Ad has been updated!', 'success')
#             return redirect(url_for('main.manage_ads'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'An error occurred: {str(e)}', 'danger')

#     return render_template('manage_ads.html',
#                            title='Manage Ads',
#                            form=form, ads=ads)



# @main.route('/manage_ads', methods=['GET', 'POST'])
# @login_required
# def manage_ads():
#     form = AdForm()
#     ads = Advertisement.query.all()  # Query all ads to display them

#     if form.validate_on_submit():
#         try:
#             image_file = None
#             if form.image.data:
#                 # Check file size
#                 file_data = form.image.data.read()
#                 file_size = len(file_data)  # Get the size of the file data

#                 # Reset file pointer to the beginning
#                 form.image.data.seek(0)

#                 max_file_size = 5 * 1024 * 1024  # 5MB size limit

#                 if file_size > max_file_size:
#                     flash('File is too large. Maximum size is 5MB.', 'danger')
#                     return redirect(url_for('main.manage_ads'))

#                 # Secure the filename
#                 image_file = secure_filename(form.image.data.filename)

#                 # Define the upload path
#                 upload_path = os.path.join('app/static/ads/')

#                 # Ensure the directory exists
#                 if not os.path.exists(upload_path):
#                     os.makedirs(upload_path)

#                 # Save the file
#                 image_path = os.path.join(upload_path, image_file)
#                 form.image.data.save(image_path)

#             # Create or update an ad
#             ad = Advertisement(
#                 ad_code=form.ad_code.data,
#                 image_file=image_file,
#                 is_active=form.is_active.data
#             )
#             db.session.add(ad)
#             db.session.commit()
#             flash('Ad has been updated!', 'success')
#             return redirect(url_for('main.manage_ads'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'An error occurred: {str(e)}', 'danger')

#     return render_template('manage_ads.html', title='Manage Ads', form=form, ads=ads)

# @main.route('/manage_ads', methods=['GET', 'POST'])
# @login_required
# def manage_ads():
#     form = AdForm()
#     ads = Advertisement.query.all()  # Query all ads to display them

#     if form.validate_on_submit():
#         try:
#             image_file = None
#             if form.image.data:
#                 # Secure the filename
#                 image_file = secure_filename(form.image.data.filename)
                
#                 # Define the upload path
#                 upload_path = os.path.join('app/static/ads/')

#                 # Ensure the directory exists
#                 if not os.path.exists(upload_path):
#                     os.makedirs(upload_path)

#                 # Save the file with the resized image
#                 image_path = os.path.join(upload_path, image_file)
#                 form.image.data.seek(0)  # Reset the file stream position
#                 with open(image_path, 'wb') as f:
#                     f.write(form.image.data.read())

#             # Create or update an ad
#             ad = Advertisement(
#                 ad_code=form.ad_code.data,
#                 image_file=image_file,
#                 is_active=form.is_active.data
#             )
#             db.session.add(ad)
#             db.session.commit()
#             flash('Ad has been updated!', 'success')
#             return redirect(url_for('main.manage_ads'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'An error occurred: {str(e)}', 'danger')

#     return render_template('manage_ads.html', title='Manage Ads', form=form, ads=ads)

# @main.route('/manage_ads', methods=['GET', 'POST'])
# @login_required
# def manage_ads():
#     form = AdForm()
#     ads = Advertisement.query.all()  # Query all ads to display them

#     if form.validate_on_submit():
#         try:
#             image_file = None
#             if form.image.data:
#                 # Secure the filename
#                 image_file = secure_filename(form.image.data.filename)
                
#                 # Define the upload path
#                 upload_path = os.path.join('app/static/ads/')

#                 # Ensure the directory exists
#                 if not os.path.exists(upload_path):
#                     os.makedirs(upload_path)

#                 # Save the file with the resized image
#                 image_path = os.path.join(upload_path, image_file)
#                 form.image.data.seek(0)  # Reset the file stream position
#                 with open(image_path, 'wb') as f:
#                     f.write(form.image.data.read())

#             # Create or update an ad
#             ad = Advertisement(
#                 ad_code=form.ad_code.data,
#                 image_file=image_file,
#                 embed_link=form.embed_link.data,  # Save the embed link
#                 is_active=form.is_active.data
#             )
#             db.session.add(ad)
#             db.session.commit()
#             flash('Ad has been updated!', 'success')
#             return redirect(url_for('main.manage_ads'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'An error occurred: {str(e)}', 'danger')

#     return render_template('manage_ads.html', title='Manage Ads', form=form, ads=ads)


from PIL import Image

@main.route('/manage_ads', methods=['GET', 'POST'])
@login_required
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
@login_required
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


from PIL import Image

@main.route('/ads', methods=['GET', 'POST'])
@login_required
def ads():
    # Query all ads to display them
    ads = Advertisement.query.all()

    return render_template('ads.html', ads=ads)

# @main.route('/advertisement/delete/<int:ad_id>', methods=['POST'])
# @login_required
# def delete_advertisement(ad_id):
#     ad = Advertisement.query.get_or_404(ad_id)
#     try:
#         db.session.delete(ad)
#         db.session.commit()
#         flash('Ad has been deleted!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash(f'An error occurred: {str(e)}', 'danger')
#     return redirect(url_for('main.ads'))


# In your routes.py
from flask import render_template, redirect, url_for
from app.models import Advertisement

@main.route('/ad_view/<int:ad_id>')
def ad_view(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    ad.increment_view()  # Increment view count
    return redirect(url_for('main.home'))  # Redirect to the main page or where needed


@main.route('/ad_click/<int:ad_id>')
def ad_click(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    ad.increment_click()  # Increment click count
    return redirect(ad.embed_link or url_for('main.home'))  # Redirect to embed link if available
