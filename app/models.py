from datetime import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Модель пользователя
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Новые поля для хранения полного имени пользователя
    last_name = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    interests = db.Column(db.String(256))

    birth_date = db.Column(db.Date)
    is_student = db.Column(db.Boolean, default=False)

    ege_math = db.Column(db.Integer)
    ege_russian = db.Column(db.Integer)
    ege_physics = db.Column(db.Integer)

    # ВАЖНО: results с backref
    results = db.relationship('Result', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Возвращает полное имя пользователя."""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join([p for p in parts if p])

    def __repr__(self):
        return f'<User {self.username}>'

# Модель теста
class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20))  # "career" или "knowledge"

    questions = db.relationship('Question', backref='test', cascade='all, delete-orphan', lazy=True)
    results = db.relationship('Result', backref='test', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Test {self.title}>'

# Модель вопроса
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)

    options = db.relationship('Option', backref='question', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Question {self.text[:50]}>'

# Модель варианта ответа
class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)

    def __repr__(self):
        return f'<Option {self.text}>'

# Модель результата
class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    result_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Result user={self.user_id} test={self.test_id}>'
