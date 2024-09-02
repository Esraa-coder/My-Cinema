from flask import Flask, request, render_template, flash, redirect,  url_for, session
import dataBase 
import passwordAuthentication as auth
import imageValidation as val
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "fklsd;akfdsaf.fosakfdausnsi\"fsdafd"
limiter =Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])

@app.route('/')
@app.route('/home')
def index():
    if 'username' in session:
        return render_template("index.html", movies = dataBase.get_all_movies())
    return render_template("notLogged.html")

@app.route("/login", methods= ["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = dataBase.get_user(username)
        if user:
            if auth.is_password_match(password, user[2]):
                session['username'] = user[1]
                session['user_id']=user[0]
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or Password", "danger")
                return render_template('login.html')
        else:
            flash("Invalid Username or Password", "danger")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/register", methods= ["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not auth.is_strong_pass(password):
            flash("Sorry You Entered a weak Password Please Choose a stronger one", "danger")
            return render_template('register.html')
        is_user_found = dataBase.get_user(username)
        if is_user_found:
            flash("User Is already created", "danger")
            return render_template("register.html")
        dataBase.add_user(username, password)
        flash("User Created Successfully", "success")
        return redirect(url_for("index"))
    else:
        return render_template("register.html")
    

@app.route("/upload-movie", methods= ["GET", "POST"])
@limiter.limit("10 per minute")
def uploadmovie():
    if not 'user_id' in session:
        flash("Please login first", "danger")
        return redirect(url_for("login"))
    if session['username'] == 'admin':
        if request.method == "POST":
            movieImage = request.files['image']
            if movieImage.filename == '':
                flash("image is required", "danger")
                return render_template("upload-movie.html")
            
            if not movieImage or not val.allowed_file(movieImage.filename) or not val.allowed_size(movieImage):
                flash("Invalid File", "danger")
                return render_template("upload-movie.html")
            
            title = request.form['title'] 
            description = request.form['description']
            price = request.form['price']
            image_url =f"uploads/{movieImage.filename}"
            movieImage.save("static/" + image_url)
            user_id = session['user_id']
            dataBase.add_movie(user_id, title, description, price,image_url)
            return redirect(url_for("index"))
        else:
            return render_template("upload-movie.html")
    else:
        flash("You Can't Access This Page", "danger")
        return redirect(url_for("index"))


@app.route("/movie/<movie_id>")
def getmovie(movie_id):
    movie = dataBase.get_movie(movie_id)
    comments = dataBase.get_comments_for_movie(movie[0])
    return render_template("movie.html", movie=movie, comments = comments)

@app.route('/buy-movie/<movie_id>',methods=['POST'])
def buy_item(movie_id):
    movie = dataBase.get_movie(movie_id)
    movie_price = float(movie[4])
    is_sold = dataBase.is_movie_sold(movie_id)
    if is_sold == 0:
       if movie:
            new_balance = float(dataBase.get_balance(session["username"])[0]) - movie_price
            if new_balance < 0:
                flash("You Have Not Enough Money يا كحيان" , "danger")
                return redirect(url_for("getmovie", movie_id=movie_id))
            dataBase.mark_movie_as_sold(movie[0])
            dataBase.update_balance(newBalance=new_balance , username=session["username"])
            flash(f"Congratulations You have bought the item !","success")
            return redirect(url_for("getmovie", movie_id=movie_id))
       else:
            return redirect(url_for("getmovie", movie_id=movie_id))
    else:
        flash("Sorry the item is already sold", "danger")
        return redirect(url_for('getmovie', movie_id=movie_id))


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template("profile.html", user  = dataBase.get_user(session['username']))
    else:
        flash("You are Not Logged In", "danger")
        return redirect(url_for("login"))


@app.route('/withdraw')
def withdraw():
    if 'username' in session:
        return render_template("withdraw.html", user = dataBase.get_user(session['username']))
    flash("You are Not Logged In", "danger")
    return redirect(url_for("login"))

@app.route('/add')
def add():
    if 'username' in session:
        return render_template("add.html", user = dataBase.get_user(session['username']))
    flash("You are Not Logged In", "danger")
    return redirect(url_for("login"))

@app.route("/balance_input" ,  methods = ["POST"])
def balance_input():
    amount = request.form.get("input-balance")
    if amount == "":
        flash("Please Add Value !! " , "danger")
        return redirect(url_for("profile"))
    if float(amount) < 0:
        flash("Cannot Add -ve Values !!" , "danger")
        return redirect(url_for("profile"))
    old_balance = dataBase.get_balance(session["username"])[0]
    new_balance = float(amount) + float(old_balance)
    dataBase.update_balance(newBalance=new_balance , username=session["username"])
    flash("Deposit Added Successfully !" , "success")
    return redirect(url_for("profile"))

@app.route("/submit" , methods = ["POST"])
def submit():
    input_balance = request.form.get("input-balance")
    if input_balance == "":
        flash("Please Add Value !! " , "danger")
        return redirect(url_for("profile"))
    if float(input_balance) < 0:
        flash("Cannot withdraw -ve Values !!" , "danger")
        return redirect(url_for("profile"))
    balance = dataBase.get_balance(username = session['username'])[0]
    newBalance = float(balance) - float(input_balance)
    if newBalance < 0:
        flash("The Required Balance Does Not Exist !" , "danger")
        return redirect(url_for("profile"))
    dataBase.update_balance(newBalance = newBalance , username = session['username'])
    flash("Balance has been updated !" , "success")
    return redirect(url_for("profile"))

@app.route("/add-comment/<movie_id>", methods= ['POST'])
def addComment(movie_id):
    text = request.form['comment']
    user_id = session['user_id']
    dataBase.add_comment(movie_id, user_id, text)
    return redirect(url_for("getmovie", movie_id = movie_id))

@app.route("/search")
def search():
    movie_name = request.args.get("search_input")
    movies = dataBase.get_all_movies()
    for movie in movies:
        if str(movie[2]).lower() == str(movie_name).lower():
            return redirect(url_for("getmovie", movie_id = movie[0])) 
    flash("Not Found !" , "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    dataBase.init_db()
    dataBase.init_movie_table()
    dataBase.init_comments_table()
    dataBase.seed_admin_user()
    app.run(debug=True)

