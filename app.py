from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(800))
    is_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' %self.id

@app.route('/', methods=['POST', 'GET'])

# render_template knows to look in templates
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_description = request.form['description']
        new_task = Todo(content=task_content, description=task_description)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Failed to delete that task"

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.description = request.form['description']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "The update was unsuccessful"
    else:
        return render_template('update.html', task=task)

@app.route('/mark_complete/<int:id>')
def mark_complete(id):
    task_completed = Todo.query.get_or_404(id)

    task_completed.is_completed = True
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Failed to mark the task as complete"

@app.route('/history/')
def history():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('history.html', tasks=tasks)

if __name__ == "__main__":
    app.run(debug=True)