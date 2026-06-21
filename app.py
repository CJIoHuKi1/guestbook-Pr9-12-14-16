from flask import Flask, render_template, request, redirect, session, flash
from database import (
    init_db, get_all_messages, get_all_messages_sorted, 
    add_message, delete_message, delete_all_messages, get_message_count, check_user
)
from filters import format_date_russian
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'секретный_ключ_для_гостевой_книги_12345'

# Добавляем фильтр для русских дат
app.jinja_env.filters['date_russian'] = format_date_russian

# Инициализируем базу данных только если не в тестовом режиме
if not os.environ.get('TESTING'):
    init_db()

@app.route('/')
def index():
    """Главная страница: показывает все сообщения (сначала новые)."""
    messages = get_all_messages()
    total_count = get_message_count()
    today = date.today().isoformat()
    
    return render_template(
        'index.html',
        messages=messages,
        total_count=total_count,
        today=today,
        logged_in=session.get('logged_in', False),
        username=session.get('username')
    )

@app.route('/add', methods=['POST'])
def add():
    """Обрабатывает отправку нового сообщения."""
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    
    if name and message:
        add_message(name, message)
        flash('Сообщение добавлено!', 'success')
        return redirect('/')
    else:
        messages = get_all_messages()
        total_count = get_message_count()
        today = date.today().isoformat()
        error = '⚠️ Заполните все поля!'
        return render_template('index.html', messages=messages, total_count=total_count, 
                             today=today, error=error, logged_in=session.get('logged_in', False),
                             username=session.get('username'))

@app.route('/delete/<int:message_id>')
def delete(message_id):
    """Удаляет сообщение по id. Только для авторизованных."""
    if not session.get('logged_in'):
        return redirect('/login')
    
    delete_message(message_id)
    flash('Сообщение удалено!', 'success')
    return redirect('/')

@app.route('/sort/newest')
def sort_newest():
    """Сортировка: сначала новые сообщения."""
    messages = get_all_messages_sorted('DESC')
    total_count = get_message_count()
    today = date.today().isoformat()
    return render_template('index.html', messages=messages, total_count=total_count, 
                         today=today, logged_in=session.get('logged_in', False),
                         username=session.get('username'))

@app.route('/sort/oldest')
def sort_oldest():
    """Сортировка: сначала старые сообщения."""
    messages = get_all_messages_sorted('ASC')
    total_count = get_message_count()
    today = date.today().isoformat()
    return render_template('index.html', messages=messages, total_count=total_count, 
                         today=today, logged_in=session.get('logged_in', False),
                         username=session.get('username'))

@app.route('/delete-all')
def delete_all_page():
    """Страница подтверждения удаления всех сообщений."""
    if not session.get('logged_in'):
        return redirect('/login')
    
    total_count = get_message_count()
    return render_template('delete_all.html', total_count=total_count)

@app.route('/delete-all-confirm', methods=['POST'])
def delete_all_confirm():
    """Подтверждение удаления всех сообщений."""
    if not session.get('logged_in'):
        return redirect('/login')
    
    delete_all_messages()
    flash('Все сообщения удалены!', 'success')
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа."""
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if check_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Вы успешно вошли!', 'success')
            return redirect('/')
        else:
            error = '❌ Неверный логин или пароль'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Выход из системы."""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Вы вышли из системы', 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)