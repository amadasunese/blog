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

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    is_featured = BooleanField('Featured Post')
    submit = SubmitField('Post')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Create Category')

    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('That category is already created. Please choose a different one.')
    


from PIL import Image


class AdForm(FlaskForm):
    ad_code = TextAreaField('Ad Code', validators=[Optional()])
    image = FileField('Ad Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'])])
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
            

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')



class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Reset Password')