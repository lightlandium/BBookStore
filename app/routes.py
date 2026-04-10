from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Book, Genre, CartItem, Order, OrderItem, Review
from app.forms import ReviewForm, CheckoutForm

main_bp = Blueprint('main', __name__)

# ---------- Главная страница ----------
@main_bp.route('/')
def index():
    top_books = Book.query.order_by(Book.rating.desc()).limit(3).all()
    genres = Genre.query.all()
    return render_template('index.html', top_books=top_books, genres=genres)


# ---------- Каталог (с фильтром по жанру) ----------
@main_bp.route('/catalog')
def catalog():
    genre_id = request.args.get('genre', type=int)
    query = Book.query
    if genre_id:
        genre = Genre.query.get_or_404(genre_id)
        query = query.filter(Book.genres.any(id=genre_id))
        title = genre.name
    else:
        title = 'Все книги'
    books = query.all()
    genres = Genre.query.all()
    return render_template('catalog.html', books=books, genres=genres, current_genre=genre_id, title=title)


# ---------- Страница книги (детально) ----------
@main_bp.route('/book/<int:id>')
def book_detail(id):
    book = Book.query.get_or_404(id)
    form = ReviewForm() if current_user.is_authenticated else None
    reviews = Review.query.filter_by(book_id=book.id).order_by(Review.created_at.desc()).all()
    return render_template('book_detail.html', book=book, form=form, reviews=reviews)


# ---------- Добавление в корзину ----------
@main_bp.route('/add_to_cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, book_id=book.id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    flash(f'Книга "{book.title}" добавлена в корзину', 'success')
    return redirect(request.referrer or url_for('main.catalog'))


# ---------- Корзина ----------
@main_bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.book.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)


# ---------- Обновление корзины (увеличить/уменьшить/удалить) ----------
@main_bp.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    action = request.form.get('action')
    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    elif action == 'remove':
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.cart'))


# ---------- Оформление заказа ----------
@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Корзина пуста.', 'warning')
        return redirect(url_for('main.cart'))
    total = sum(item.book.price * item.quantity for item in items)
    form = CheckoutForm()
    if form.validate_on_submit():
        delivery_method = form.delivery_method.data
        address = form.address.data if delivery_method == 'courier' else None
        order = Order(
            user_id=current_user.id,
            delivery_method=delivery_method,
            delivery_address=address,
            total_price=total,
            status='Оформлен'
        )
        db.session.add(order)
        db.session.flush()
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item.book_id,
                quantity=item.quantity,
                price_at_purchase=item.book.price
            )
            db.session.add(order_item)
            db.session.delete(item)  # очищаем корзину
        db.session.commit()
        flash('Заказ успешно оформлен!', 'success')
        return redirect(url_for('main.orders'))
    return render_template('checkout.html', form=form, total=total)


# ---------- История заказов ----------
@main_bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('orders.html', orders=user_orders)


# ---------- Детали заказа ----------
@main_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_detail.html', order=order)


# ---------- Отмена заказа ----------
@main_bp.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id or order.status != 'Оформлен':
        abort(403)
    order.status = 'Отменён'
    db.session.commit()
    flash('Заказ отменён.', 'warning')
    return redirect(url_for('main.orders'))


# ---------- Добавление отзыва и пересчёт рейтинга ----------
@main_bp.route('/add_review/<int:book_id>', methods=['POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            book_id=book.id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        book.update_rating()
        flash('Отзыв добавлен!', 'success')
    else:
        flash('Ошибка при добавлении отзыва.', 'danger')
    return redirect(url_for('main.book_detail', id=book.id))


# ---------- Поиск по названию или автору ----------
@main_bp.route('/search')
def search():
    q = request.args.get('q', '')
    books = []
    if q:
        books = Book.query.filter(
            Book.title.ilike(f'%{q}%') | Book.author.ilike(f'%{q}%')
        ).all()
    return render_template('catalog.html', books=books, title=f'Результаты поиска: {q}')