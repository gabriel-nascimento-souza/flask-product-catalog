from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'database.db')

def create_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      description TEXT,
                      price REAL NOT NULL,
                      image TEXT
                    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form['description']
        image = request.form['image']

        try:
            price = float(request.form['price'])
        except ValueError:
            flash('❌ Invalid price. Please enter a valid number.')
            return redirect(url_for('add_product'))

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (title, description, price, image) VALUES (?, ?, ?, ?)',
                       (title, description, price, image))
        conn.commit()
        conn.close()

        flash('✅ Product added successfully!')
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_product(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('🗑️ Product deleted successfully.')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        image = request.form['image']

        try:
            price = float(request.form['price'])
        except ValueError:
            flash('❌ Invalid price. Please enter a valid number.')
            return redirect(url_for('edit_product', id=id))

        cursor.execute('''UPDATE products SET title = ?, description = ?, price = ?, image = ?
                          WHERE id = ?''', (title, description, price, image, id))
        conn.commit()
        conn.close()
        flash('✅ Product updated successfully!')
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM products WHERE id = ?', (id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        return render_template('edit.html', product=product)
    else:
        flash('❌ Product not found.')
        return redirect(url_for('index'))


if __name__ == '__main__':
    create_database()
    app.run(debug=True)