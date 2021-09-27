from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime as dt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    description = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    times = db.relationship('Times', backref='todo')

    def __repr__(self):
        return '<Task %r>' %self.id

class Times(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_elapsed = db.Column(db.Interval, nullable=False)
    date_worked = db.Column(db.DateTime, default=dt.utcnow) 
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)

    def __repr__(self):
        return '<Time %r>' %self.id

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
    is_history = task_to_delete.is_completed
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        if is_history == True:
            return redirect('/history/')
        else:    
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
            if task.is_completed == True:
                return redirect('/history/')
            else:  
                return redirect('/')
        except:
            return "The update was unsuccessful"
    else:
        return render_template('update.html', task=task)

@app.route('/change_completion/<int:id>')
def change_completion(id):
    task_completed = Todo.query.get_or_404(id)
    if task_completed.is_completed: 
        task_completed.is_completed = False
    else:
        task_completed.is_completed = True
    try:
        db.session.commit()
        if task_completed.is_completed:
            return redirect('/')
        else:    
            return redirect('/history/')
    except:
        return "Failed to change completion value"

@app.route('/history/')
def history():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('history.html', tasks=tasks)

@app.route('/settimer/<int:id>', methods=["GET", "POST"])
def settimer(id):
    if request.method == 'POST':
        session['hours'] = int(request.form['hours'])
        session['minutes'] = int(request.form['minutes'])
        session['seconds'] = 0
        session['time_in_seconds'] = session['hours'] *3600 + session['minutes'] * 60


        return redirect(url_for('timer', id=id))
    else:
        task = Todo.query.get_or_404(id)
        session['hours'] = 0
        session['minutes'] = 0
        return render_template('settimer.html', task=task)

@app.route('/timer/<int:id>', methods=["GET", "POST"])
def timer(id):
    task = Todo.query.get_or_404(id)
    return render_template('timer.html', task=task, hrs=session['hours'], mins=session['minutes'], secs=session['seconds'])

if __name__ == "__main__":
    app.run(debug=True)