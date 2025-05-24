from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import date
from models import User, ItemCategory

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReportLostItemForm(FlaskForm):
    title = StringField('Item Name', validators=[DataRequired(), Length(min=3, max=100)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    date_lost = DateField('Date Lost', validators=[DataRequired()], default=date.today)
    location_lost = StringField('Location Lost', validators=[DataRequired(), Length(min=3, max=100)])
    image = FileField('Item Image (Optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Report Lost Item')
    
    def validate_date_lost(self, date_lost):
        if date_lost.data > date.today():
            raise ValidationError('Date lost cannot be in the future.')
    
    def __init__(self, *args, **kwargs):
        super(ReportLostItemForm, self).__init__(*args, **kwargs)
        # Populate categories from database
        self.category.choices = [(c.id, c.name) for c in ItemCategory.query.all()]
        # Add default category if none exist yet
        if not self.category.choices:
            self.category.choices = [(1, 'General')]

class ReportFoundItemForm(FlaskForm):
    title = StringField('Item Name', validators=[DataRequired(), Length(min=3, max=100)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    date_found = DateField('Date Found', validators=[DataRequired()], default=date.today)
    location_found = StringField('Location Found', validators=[DataRequired(), Length(min=3, max=100)])
    image = FileField('Item Image (Optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Report Found Item')
    
    def validate_date_found(self, date_found):
        if date_found.data > date.today():
            raise ValidationError('Date found cannot be in the future.')
    
    def __init__(self, *args, **kwargs):
        super(ReportFoundItemForm, self).__init__(*args, **kwargs)
        # Populate categories from database
        self.category.choices = [(c.id, c.name) for c in ItemCategory.query.all()]
        # Add default category if none exist yet
        if not self.category.choices:
            self.category.choices = [(1, 'General')]

class SearchItemForm(FlaskForm):
    query = StringField('Search', validators=[Length(min=0, max=100)])
    category = SelectField('Category', coerce=int, validators=[])
    status = SelectField('Status', choices=[
        (0, 'All'), 
        (1, 'Unresolved/Unclaimed'), 
        (2, 'Resolved/Claimed')
    ], coerce=int)
    date_from = DateField('From Date', validators=[], default=None)
    date_to = DateField('To Date', validators=[], default=None)
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(SearchItemForm, self).__init__(*args, **kwargs)
        # Populate categories from database with an "All" option
        choices = [(0, 'All Categories')]
        choices.extend([(c.id, c.name) for c in ItemCategory.query.all()])
        self.category.choices = choices

class AdminMatchForm(FlaskForm):
    match_id = HiddenField('Match ID')
    action = SelectField('Action', choices=[
        ('approve', 'Approve Match'), 
        ('reject', 'Reject Match')
    ])
    notes = TextAreaField('Admin Notes')
    submit = SubmitField('Submit Decision')
