// Дополнительная клиентская логика (например, подтверждение удаления товара)
document.querySelectorAll('.delete-item').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (!confirm('Удалить товар из корзины?')) e.preventDefault();
    });
});