import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


def validate_password_strength(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('密码至少需要8个字符')
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError('密码必须包含至少一个字母')
    if not re.search(r'[0-9]', password):
        raise ValidationError('密码必须包含至少一个数字')


class SignupForm(FlaskForm):
    name = StringField('姓名', validators=[
        DataRequired(message='请输入姓名'),
        Length(min=2, max=100, message='姓名长度在2-100个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        validate_password_strength
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')


class SearchForm(FlaskForm):
    search = StringField('搜索姓名', validators=[
        DataRequired(message='请输入搜索内容')
    ])
    submit = SubmitField('搜索')
