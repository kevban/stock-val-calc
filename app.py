from flask import Flask, render_template, redirect, request, jsonify, session, flash, g
from models import *
from forms import StockValQuestionaire, LoginForm, SaveForecastForm
from helper import format_num
from sqlalchemy.exc import IntegrityError

from findata import *

"""stockval application."""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///stockval'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'abc123'


connect_db(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if 'username' in session:
        g.user = User.query.get(session['username'])

    else:
        g.user = None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if g.user:
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = User.signup(
                    username=form.username.data,
                    password=form.password.data
                )
                db.session.commit()
            except IntegrityError: # if the input is invalid, notify the user and rerender the page
                flash("Username already taken", 'danger')
                return render_template('signup.html', form=form)

            session['username'] = user.username
            return redirect("/")

        return render_template('signup.html', form=form, login=False)

@app.route('/login', methods=['POST', 'GET'])
def login_page():
    if g.user:
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.authenticate(form.username.data, form.password.data)
            if user:
                session['username'] = user.username
                return redirect('/')
            flash("Invalid credentials.", 'danger')
        return render_template('signup.html', form=form, login=True)

@app.route('/logout')
def logout():
    if g.user:
        session.pop('username')
        flash("You have successully logged out", 'success')
    return redirect('/')

@app.route('/user/<username>')
def user_details(username):
    user = User.query.get(username)
    user_forecasts = user.get_forecast()
    covered_stocks = []
    
    for k in user_forecasts.keys():
        price = get_price(k)
        recommendation = 'Buy'
        stock = {}
        stock['target'] = 0
        stock['ticker'] = k
        total_weight = 0
        count = 0
        for v in user_forecasts[k]:
            stock['date'] = v['date']
            stock['target'] = stock['target'] + v['target'] * v['weight']
            total_weight += v['weight']
            count += 1
        
        if stock['target'] < price['hist_30d_prices'][len(price['hist_30d_prices']) - 1]:
            recommendation = 'Sell'
        stock['recommendation'] = recommendation
        stock['target'] /= total_weight
        stock['ratings'] = count
        covered_stocks.append(stock)
    return render_template('user-details.html', user=user, covered_stocks=covered_stocks, g=g)


@app.route('/search', methods=["POST"])
def search():
    ticker = request.form["search-term"]
    return redirect(f'/search/{ticker}')


@app.route('/search/<ticker>')
def display_stock(ticker):
    data = Stock.get_stock(ticker)
    price = get_price(ticker)
    cur_price = format_num(price['hist_30d_prices'][len(price['hist_30d_prices']) - 1])
    return render_template('stock-details.html', data=data, price=price,
                           cur_price=cur_price)


@app.route('/search/<ticker>/valuation/start', methods=["GET", "POST"])
def val_quickstart(ticker):
    form = StockValQuestionaire()
    if form.validate_on_submit():
        growth = form.growth.data
        margin = form.margin.data
        pe = form.pe.data
        return redirect(f'/search/{ticker}/valuation/summary?growth={growth}&margin={margin}&pe={pe}')
    return render_template('questionaire.html', form=form)


@app.route('/search/<ticker>/valuation/summary')
def val_summary(ticker):
    data = get_stock_data(ticker)
    query_str = request.args
    login_form = LoginForm()
    save_form = SaveForecastForm()
    return render_template('stockcopy.html', data=data, query=query_str, login_form=login_form, save_form=save_form, user=g.user)



    
    
@app.route('/api/stocks/<ticker>')
def api_get_stock_data(ticker):
    """Get json data of a stock

        return None if ticker is invalid
    """

    stock = Stock.get_stock(ticker)
    price = get_price(ticker)
    if stock:
        response = jsonify(stock=stock.serialize(), price=price)
        return (response, 200)
    else:
        return (None, 404)

@app.route('/api/forecasts/save', methods=["POST"])
def api_save_forecast():
    """Save a user forecast to database"""
    if g.user:
        forecast = Forecast.save_forecast(request.json, g.user.username)
        return (forecast, 201)
    else:
        return (None, 401) # return unauthorized if not signed in

