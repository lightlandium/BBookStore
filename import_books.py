import json
import os
from app import create_app, db
from app.models import Book, Genre

app = create_app()

def import_books(json_path):
    with app.app_context():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            # Проверка дубликатов
            existing = Book.query.filter_by(title=item['title'], author=item['author']).first()
            if existing:
                print(f'Книга "{item["title"]}" уже есть, пропускаем')
                continue
            # Находим или создаём жанр
            genre_name = item['genre']
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.flush()
            # Создаём книгу с правильным путём к обложке
            book = Book(
                title=item['title'],
                author=item['author'],
                year=item.get('year', 0),
                price=float(item['price']),
                cover_image=f'books/{item["id"]}.png',   # ← вот так формируется путь
                description=item.get('description', ''),
                rating=float(item.get('rating', 0.0))
            )
            book.genres.append(genre)
            db.session.add(book)
            count += 1
            print(f'Добавлена книга: {book.title} (id={book.id}, обложка: {book.cover_image})')
        db.session.commit()
        print(f'Импортировано книг: {count}')

if __name__ == '__main__':
    import_books('books_catalog.json')