from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)
app.secret_key = "7"

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'logout', 'index', 'everyone']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():
    owner = User.query.filter_by(email=session['email']).first()
    posts = Post.query.all()
    users = User.query.all()
    return render_template('index.html', title="Blog", posts=posts, users=users)

@app.route("/blog", methods = ["POST", "GET"])
def blog():
    num = request.args.get('id')
    post = Post.query.filter_by(id=num).first()
    if num:
        return render_template('justone.html', post=post)
    else:
        owner = User.query.filter_by(email=session['email']).first()
        posts = Post.query.filter_by(owner=owner).all()
        return render_template('allposts.html', title="Blog", posts=posts)

@app.route("/allposts")
def allposts():
    id = int(request.args.get('id'))
    posts = Post.query.filter_by(owner_id=id).all()
    return render_template('allposts.html', posts=posts)  
        
@app.route('/post_form', methods=["POST", "GET"])   
def post_form():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        owner = User.query.filter_by(email=session['email']).first()
        if body == "" or title == "":
            flash("Make sure to fill out both fields please!", "error")
            return redirect("/post_form")
        new_post = Post(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/blog?id=" + str(new_post.id))
           
    return render_template("blog.html", title="New Post")


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Post', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged In")
            return redirect('/home')
        else:
            flash('User or password incorrect, or user does not exist', 'error')
           
    return render_template('login.html')

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['pw_check']
        
        #TODO - *Validate user data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            #TODO - user better response message
            return "<h1>Duplicate User</h1>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return render_template('logout.html')

@app.route('/everyone')
def everyone():
    num = request.args.get('owner')
    post = Post.query.filter_by(id=num).first()
    users = User.query.all()
    if num:
        return render_template('justone.html', post=post)
    else:
        owner = User.query.filter_by(email=session['email']).first()
        posts = Post.query.all()
        return render_template('everyone.html', title="Blog", posts=posts, users=users)

@app.route('/authorlist')
def authorlist():
    users = User.query.all()
    return render_template('authorlist.html', users=users)

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()