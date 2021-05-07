from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Echo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Verify Echo Device')

    def validate_code(form, field):
            if len(field.data) != 5:
                raise ValidationError('Verification code must be five digits long')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not field.data.isalnum():
            raise ValidationError('Username must not contain any special characters')
        if user is not None:
            raise ValidationError('Username has already been registered')


class TokenForm(FlaskForm):
    token = StringField("Token", validators=[DataRequired()])
    submit = SubmitField('Set Token')