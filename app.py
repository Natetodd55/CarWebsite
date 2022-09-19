import flask
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(20))
    model = db.Column(db.String(20))
    year = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


from app import db, User, Car


@login_manager.user_loader
def load_user(uid):
    user = User.query.get(uid)
    return user



@app.route('/')
def home():
    return render_template('home.html')



@app.route('/create', methods = ['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['uName']
        age = request.form['age']
        password = request.form['pWord']
        temp = User(username = username, password = password, name = name, age = age)
        user = User.query.filter_by(username=request.form['uName']).first()
        if user != None:
            return render_template('create.html'), 'username already exists'
        db.session.add(temp)
        db.session.commit()
        user = User.query.filter_by(username=request.form['uName']).first()
        login_user(user)
        return flask.redirect('/')
    return render_template('create.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uName']
        user = User.query.filter_by(username=username).first()
        if user != None:
            if request.form['pWord'] != user.password:
                return render_template('login.html')
            login_user(user)
            return flask.redirect('/')
        return render_template('login.html')
    return render_template('login.html')


@app.route('/read')
@login_required
def read():
    results = User.query.filter_by(id = current_user.id)
    results2 = Car.query.filter_by(user_id = current_user.id).all()
    return render_template('read.html', users = results, cars = results2)


@app.route('/update/<id>', methods = ['GET', 'POST'])
def updateCar(id):
    if request.method == 'POST':
        updatedCar = Car.query.filter_by(id=id).first()
        updatedCar.make = request.form['make']
        updatedCar.model = request.form['model']
        updatedCar.year = request.form['year']
        db.session.commit()
        return flask.redirect('/read')
    temp = Car.query.filter_by(id=id).first()
    return render_template('create.html', id = id, make = temp.make, model = temp.model, year = temp.year)


@app.route('/update/', methods = ['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        oldPassword = request.form['oldP']
        if current_user.password != oldPassword:
            return render_template('update.html')
        updatedUser = User.query.filter_by(id=current_user.id).first()
        updatedUser.password = request.form['newP']
        db.session.commit()
        return flask.redirect('/')
    return render_template('update.html')


@app.route('/delete/<id>', methods = ['GET', 'POST'])
def delete(id):
    if request.method == 'POST':
        delCar = Car.query.filter_by(id=id).first()
        db.session.delete(delCar)
        db.session.commit()
        return flask.redirect('/read')
    return flask.redirect('/read')


@app.route('/addCar', methods = ['GET', 'POST'])
@login_required
def addCar():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        temp = Car(make=make, model=model, year=year, user_id = current_user.id)
        db.session.add(temp)
        db.session.commit()
    return render_template('addCar.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect('/')



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)