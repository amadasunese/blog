from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from app.models import User, Category
from flask_wtf.file import FileField, FileRequired, FileAllowed
# from wtforms.validators import Optional, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',

                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose a different one.')

# class PostForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     submit = SubmitField('Post')


# class PostForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     image = FileField('Featured Image', validators=[
#         FileAllowed(['jpg', 'png'], 'Images only!'),
#         FileRequired('File was not selected')
#     ])
#     submit = SubmitField('Submit')

# class PostForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     category = SelectField('Category', choices=[], coerce=int)
#     submit = SubmitField('Post')

#     def __init__(self, *args, **kwargs):
#         super(PostForm, self).__init__(*args, **kwargs)
#         self.category.choices = [(c.id, c.name) for c in Category.query.all()]
    

# class PostForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
#     category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])
#     submit = SubmitField('Post')

#     def __init__(self, *args, **kwargs):
#         super(PostForm, self).__init__(*args, **kwargs)
#         self.category.choices = [(category.id, category.name) for category in Category.query.all()]


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    is_featured = BooleanField('Featured Post')
    submit = SubmitField('Post')

    # def __init__(self, *args, **kwargs):
    #     super(PostForm, self).__init__(*args, **kwargs)
    #     self.category.choices = [(category.id, category.name) for category in Category.query.all()]


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Create Category')

    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('That category is already created. Please choose a different one.')
    

# class AdForm(FlaskForm):
#     ad_code = TextAreaField('Ad Code', validators=[Optional()])
#     image = FileField('Ad Image', validators=[Optional(), FileAllowed(['jpg', 'png'])])
#     is_active = BooleanField('Active')
#     submit = SubmitField('Submit')

#     def validate_image(form, field):
#         if field.data:
#             # Perform size validation if the image is uploaded
#             image = field.data
#             image.stream.seek(0)
#             image_size = image.size
#             image_width, image_height = image_size[0], image_size[1]

#             if image_width not in [200, 300]:
#                 raise ValidationError('Image width must be either 200px or 300px.')



from PIL import Image

# class AdForm(FlaskForm):
#     ad_code = TextAreaField('Ad Code', validators=[Optional()])
#     image = FileField('Ad Image', validators=[Optional(), FileAllowed(['jpg', 'png'])])
#     is_active = BooleanField('Active')
#     submit = SubmitField('Submit')

#     def validate_image(form, field):
#         if field.data:
#             try:
#                 # Open the image using Pillow
#                 image = Image.open(field.data)
#                 image_width, image_height = image.size

#                 # Determine the new width for resizing
#                 if image_width > 300:
#                     new_width = 300
#                 elif image_width > 200:
#                     new_width = 200
#                 else:
#                     new_width = image_width

#                 # Calculate the new height while maintaining the aspect ratio
#                 aspect_ratio = image_height / image_width
#                 new_height = int(new_width * aspect_ratio)

#                 # Resize the image
#                 resized_image = image.resize((new_width, new_height), Image.LANCZOS)

#                 # Save the resized image temporarily
#                 resized_image.save(field.data, format=image.format)

#             except Exception as e:
#                 raise ValidationError(f'Invalid image format: {str(e)}')


class AdForm(FlaskForm):
    ad_code = TextAreaField('Ad Code', validators=[Optional()])
    image = FileField('Ad Image', validators=[Optional(), FileAllowed(['jpg', 'png'])])
    embed_link = StringField('Embed Link', validators=[Optional()])
    is_active = BooleanField('Active')
    submit = SubmitField('Submit')
    

    def validate_image(form, field):
        if field.data:
            try:
                # Open the image using Pillow
                image = Image.open(field.data)
                image_width, image_height = image.size

                # Determine the new width for resizing
                if image_width > 300:
                    new_width = 300
                elif image_width > 200:
                    new_width = 200
                else:
                    new_width = image_width

                # Calculate the new height while maintaining the aspect ratio
                aspect_ratio = image_height / image_width
                new_height = int(new_width * aspect_ratio)

                # Resize the image
                resized_image = image.resize((new_width, new_height), Image.LANCZOS)

                # Save the resized image temporarily
                field.data.seek(0)  # Reset file stream position
                resized_image.save(field.data, format=image.format)

            except Exception as e:
                raise ValidationError(f'Invalid image format: {str(e)}')