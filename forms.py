from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Email, Length, URL, Optional
from email_validator import validate_email, EmailNotValidError


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField(
        'text',
        validators=[DataRequired(), Length(max=140)],
        )


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username',
        validators=[DataRequired(), Length(max=20)],
        )
    email = StringField(
        'E-mail',
        validators=[DataRequired(), Email()],
        )
    password = PasswordField(
        'Password',
        validators=[Length(min=6, max=20)],
        )
    image_url = StringField(
        '(Optional) Image URL',
        validators=[Optional(), URL()],
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[DataRequired(), Length(max=20)],
        )
    password = PasswordField(
        'Password',
        validators=[Length(min=6, max=20)],
        )


class UserEditForm(FlaskForm):
    """ Form for editing user info """

    # TODO: Add validation for max length for fields
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(max=20)],
        )
    email = StringField(
        'E-mail',
        validators=[DataRequired(), Email()],
        )
    image_url = StringField(
        '(Optional) Image URL',
        validators=[Optional()],
    )
    header_image_url = StringField(
        '(Optional) Header Image URL',
        validators=[Optional()],
    )
    bio = TextAreaField(
        'Bio',
        render_kw={'class': 'form-control', 'rows': 10},
        validators=[DataRequired()],
    )
    location = StringField(
        'Location',
        validators=[DataRequired(), Length(max=20)],
    )
    password = PasswordField(
        'Password',
        validators=[Length(min=6, max=20)]
        )


class UserLogoutForm(FlaskForm):
    """ Left empty for CSRF protection and caching. """
