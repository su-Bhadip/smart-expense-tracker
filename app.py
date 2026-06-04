from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense.db"

db = SQLAlchemy(app)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
   
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))
    amount = db.Column(db.Float)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        title = request.form["title"]
        amount = request.form["amount"]

        expense = Expense(
            title=title,
            amount=amount
        )

        db.session.add(expense)
        db.session.commit()

        return redirect("/")

    search = request.args.get("search", "")

    if search:
        expenses = Expense.query.filter(
        Expense.title.contains(search)
        ).all()
    else:
        expenses = Expense.query.all()
    
    incomes = Income.query.all()

    total_expense = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)

    balance = total_income - total_expense  
    

    return render_template(
    "index.html",
    expenses=expenses,
    total_expense=total_expense,
    total_income=total_income,
    balance=balance
)


@app.route("/delete/<int:id>")
def delete(id):

    expense = Expense.query.get(id)

    db.session.delete(expense)

    db.session.commit()

    return redirect("/")


@app.route("/income", methods=["GET", "POST"])
def income():

    if request.method == "POST":

        source = request.form["source"]
        amount = request.form["amount"]

        new_income = Income(
            source=source,
            amount=amount
        )

        db.session.add(new_income)
        db.session.commit()

        return redirect("/income")

    incomes = Income.query.all()

    total_income = sum(income.amount for income in incomes)

    return render_template(
        "income.html",
        incomes=incomes,
        total_income=total_income
    )


@app.route("/export")
def export():

    expenses = Expense.query.all()

    csv_data = "Title,Amount\n"

    for expense in expenses:
        csv_data += f"{expense.title},{expense.amount}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=expenses.csv"
        }
    )

@app.route("/chart")
def chart():

    expenses = Expense.query.all()

    labels = []
    amounts = []

    for expense in expenses:
        labels.append(expense.title)
        amounts.append(expense.amount)

    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=labels, autopct="%1.1f%%")

    plt.savefig("static/chart.png")
    plt.close()

    return render_template("chart.html")


if __name__ == "__main__":
    app.run(debug=True)


