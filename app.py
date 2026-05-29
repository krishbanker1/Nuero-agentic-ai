{
  "files": [
    {
      "path": "app.py",
      "content": "import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SECRET_KEY'] = 'super-secret'

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
cors = CORS(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, title, description):
        self.title = title
        self.description = description

class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if username == 'admin' and password == 'password':
        return jsonify({'token': 'admin-token'})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify(todos_schema.dump(todos))

@app.route('/todos', methods=['POST'])
def create_todo():
    new_todo = Todo(request.json['title'], request.json['description'])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(todo_schema.dump(new_todo))

@app.route('/todos/<id>', methods=['GET'])
def get_todo(id):
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo_schema.dump(todo))

@app.route('/todos/<id>', methods=['PUT'])
def update_todo(id):
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    db.session.commit()
    return jsonify(todo_schema.dump(todo))

@app.route('/todos/<id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
"
    },
    {
      "path": "templates/index.html",
      "content": "<html>
  <head>
    <title>Todo App</title>
    <link rel='stylesheet' href='/static/style.css'>
  </head>
  <body>
    <h1>Todo App</h1>
    <ul id='todos'></ul>
    <form id='create-todo'>
      <input type='text' id='title' placeholder='Title'>
      <input type='text' id='description' placeholder='Description'>
      <button type='submit'>Create Todo</button>
    </form>
    <script src='/static/script.js'></script>
  </body>
</html>
"
    },
    {
      "path": "static/style.css",
      "content": "body {
  font-family: Arial, sans-serif;
}

#todos {
  list-style: none;
  padding: 0;
  margin: 0;
}

#todos li {
  padding: 10px;
  border-bottom: 1px solid #ccc;
}

#todos li:last-child {
  border-bottom: none;
}

#create-todo {
  margin-top: 20px;
}

#create-todo input {
  padding: 10px;
  margin-right: 10px;
  border: 1px solid #ccc;
}

#create-todo button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

#create-todo button:hover {
  background-color: #3e8e41;
}
"
    },
    {
      "path": "static/script.js",
      "content": "const todosList = document.getElementById('todos');
const createTodoForm = document.getElementById('create-todo');

createTodoForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = document.getElementById('title').value;
  const description = document.getElementById('description').value;
  const response = await fetch('/todos', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title, description })
  });
  const todo = await response.json();
  const todoListItem = document.createElement('li');
  todoListItem.textContent = `${todo.title} - ${todo.description}`;
  todosList.appendChild(todoListItem);
  document.getElementById('title').value = '';
  document.getElementById('description').value = '';
});

fetch('/todos')
  .then(response => response.json())
  .then(todos => {
    todos.forEach(todo => {
      const todoListItem = document.createElement('li');
      todoListItem.textContent = `${todo.title} - ${todo.description}`;
      todosList.appendChild(todoListItem);
    });
  });
"
    },
    {
      "path": "requirements.txt",
      "content": "flask
flask_sqlalchemy
flask_marshmallow
flask_bcrypt
flask_jwt_extended
flask_cors
"
    }
  ]
}