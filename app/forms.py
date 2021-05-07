from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Echo

class LoginForm(FlaskForm):
    #set the username
    username = StringField('Username', validators=[DataRequired()])
    #set the password
    password = PasswordField('Password', validators=[DataRequired()])
    #either set the remember me to either true or false if they want the application to remember the username and password
    remember_me = BooleanField('Remember Me')
    #submit the information
    submit = SubmitField('Sign In')

class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Verify Echo Device')

    def validate_code(form, field):
            if len(field.data) != 6:
                raise ValidationError('Verification code must be six digits long')

class RegistrationForm(FlaskForm):
    #sets the new username for account creation
    username = StringField('Username', validators=[DataRequired()])
    #sets the new password for account creation
    password = PasswordField('Password', validators=[DataRequired()])
    #sets the new password for account creation but makes sure that the previous password is equal to the current one being set here
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    #submit the field to sign up
    submit = SubmitField('Sign Up')

    #makes sure the username is unique
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not field.data.isalnum():
            raise ValidationError('Username must not contain any special characters')
        if user is not None:
            raise ValidationError('Username has already been registered')


class TokenForm(FlaskForm):
    token = StringField("Token", validators=[DataRequired()])
    submit = SubmitField('Set Token')
