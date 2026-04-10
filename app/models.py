from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ассоциативная таблица для связи Book – Genre (многие ко многим)
book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmation_code = db.Column(db.String(6))
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship('Book', secondary=book_genre, back_populates='genres')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False, index=True)
    year = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    # ⬇️ ПОЛЕ ДЛЯ ОБЛОЖКИ (ПРОВЕРЬТЕ, ЧТО ОНО ЕСТЬ)
    cover_image = db.Column(db.String(300))   # хранит относительный путь, например 'books/100.png'
    description = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    genres = db.relationship('Genre', secondary=book_genre, back_populates='books')
    cart_items = db.relationship('CartItem', backref='book', lazy=True)
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    reviews = db.relationship('Review', backref='book', lazy=True, cascade='all, delete-orphan')

    def update_rating(self):
        """Пересчёт среднего рейтинга на основе отзывов"""
        if self.reviews:
            avg = sum(r.rating for r in self.reviews) / len(self.reviews)
            self.rating = round(avg, 1)
        else:
            self.rating = 0.0
        db.session.commit()

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book'),)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Оформлен')
    delivery_method = db.Column(db.String(20))
    delivery_address = db.Column(db.String(300))
    total_price = db.Column(db.Float)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)