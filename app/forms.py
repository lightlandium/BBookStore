from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Фамилия', validators=[Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class ConfirmationForm(FlaskForm):
    code = StringField('Код подтверждения', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Подтвердить')

class ReviewForm(FlaskForm):
    rating = SelectField('Оценка', choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Оставить отзыв')

class CheckoutForm(FlaskForm):
    delivery_method = RadioField('Способ доставки', choices=[('pickup','Самовывоз'),('courier','До двери')], default='pickup')
    address = StringField('Адрес доставки', validators=[Length(max=300)])
    submit = SubmitField('Подтвердить и оформить заказ')