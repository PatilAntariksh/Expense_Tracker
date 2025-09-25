from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    expenses = Expense.query.all()
    total = sum(e.amount for e in expenses)

    # Category Pie Chart
    categories = [e.category for e in expenses]
    amounts = [e.amount for e in expenses]
    pie_chart = None
    if categories:
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        pie_chart = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

    # Monthly Bar Chart
    months = {}
    for e in expenses:
        month = e.date[:7] if e.date else "Unknown"
        months[month] = months.get(month, 0) + e.amount
    bar_chart = None
    if months:
        fig, ax = plt.subplots()
        ax.bar(months.keys(), months.values(), color='skyblue')
        plt.xticks(rotation=45)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        bar_chart = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

    return render_template('index.html', expenses=expenses, total=total, pie_chart=pie_chart, bar_chart=bar_chart)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        title = request.form['title']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        new_expense = Expense(title=title, amount=amount, category=category, date=date)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_expense.html')

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
