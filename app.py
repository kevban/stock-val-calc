from flask import Flask, render_template, redirect, request, jsonify, session, flash, g
from models import *
from forms import LoginForm, SaveForecastForm
from helper import format_num
from sqlalchemy.exc import IntegrityError
import datetime
import os

from findata import *

"""stockval application."""

app = Flask(__name__)
database_url = os.environ.get('SQLALCHEMY_URL', 'postgresql:///stockval')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'abc123')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url


connect_db(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

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
            except IntegrityError:  # if the input is invalid, notify the user and rerender the page
                flash("Username already taken", 'danger')
                return render_template('signup.html', form=form)
            except ValueError:
                flash("Please enter a valid username/password", 'danger')
                return render_template('signup.html', form=form)

            session['username'] = user.username
            flash("Successfully logged in", 'success')
            return redirect("/")

        return render_template('signup.html', form=form, login=False)

@app.route('/update/<ticker>')
def update_stock(ticker):
    stock = Stock.query.get(ticker)
    if stock:
        stock.update_stock()
        return redirect(f'/search/{ticker}')
    else:
        return render_template('notfound.html', term=ticker)

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
                flash("Successfully logged in", 'success')
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
    if user:
        covered_stocks = user.get_forecast_summary()
        for stock in covered_stocks:
            stock['date'] = datetime.date.strftime(stock['date'], "%m/%d/%Y")
            stock['target'] = "{:,.2f}".format(stock['target'])
        return render_template('user-details.html', user=user, covered_stocks=covered_stocks, g=g)
    else:
        return render_template('notfound.html', term=username)


@app.route('/user/<username>/forecast/<ticker>')
def user_forecast_details(username, ticker):
    user = User.query.get(username)
    forecasts = user.get_forecast().get(ticker, None)
    for forecast in forecasts:
        forecast['date'] = datetime.date.strftime(forecast['date'], "%m/%d/%Y")
        forecast['target'] = "{:,.2f}".format(forecast['target'])
    return render_template('user-forecast-details.html', forecasts=forecasts, g=g, user=user, ticker=ticker)


@app.route('/forecast/<int:forecast_id>')
def display_forecsat(forecast_id):
    forecast = Forecast.query.get(forecast_id)
    if forecast:
        # calculating line items for the forecast to display
        forecast_dict = forecast.serialize()
        price = get_price(forecast_dict['ticker'])
        forecast_dict['gross_income'] = [sum(i) for i in zip(forecast_dict['revenue'], forecast_dict['cogs'])]
        forecast_dict['ebitda'] = [sum(i) for i in zip(forecast_dict['gross_income'], forecast_dict['opex'])]
        forecast_dict['operating_income'] = [sum(i) for i in zip(forecast_dict['ebitda'], forecast_dict['depreciation'])]
        forecast_dict['ebt'] = [sum(i) for i in zip(forecast_dict['operating_income'], forecast_dict['other'])]
        forecast_dict['last_eps'] = forecast_dict['net_income'][len(forecast_dict['net_income']) - 1] / forecast_dict['shares_out']
        forecast_dict['date'] = datetime.date.strftime(forecast_dict['date'], "%m/%d/%Y")
        if forecast_dict['ps'] != -1:
            forecast_dict['multiple'] = forecast_dict['ps']
        else:
            forecast_dict['multiple'] = forecast_dict['pe']
        forecast_dict['price'] = forecast_dict['last_eps'] * forecast_dict['multiple']
        forecast_dict['dividend_per_share'] = sum(forecast_dict['dividend']) / forecast_dict['shares_out']
        forecast_dict['return'] = (forecast_dict['target'] / price['cur_price']) ** (1/4) - 1


        # formating display
        for k in forecast_dict:
            if k in ['revenue', 'cogs', 'opex', 'depreciation', 'other', 'tax', 'net_income', 'dividend', 'ebitda', 'operating_income', 'ebt', 'gross_income']:
                for i in range(len(forecast_dict[k])):
                    forecast_dict[k][i] = "${:,.0f}".format(forecast_dict[k][i] / 1000000)
            elif k == 'return':
                forecast_dict[k] = "{:,.2f}%".format(forecast_dict[k]*100)
            elif k in ['multiple', 'last_eps', 'price', 'dividend_per_share', 'target']:
                forecast_dict[k] = "{:,.2f}".format(forecast_dict[k])
    
        return render_template('forecast-details.html', forecast=forecast_dict, g=g)
    else:
        return render_template('notfound.html', term='Forecast')


@app.route('/user/<username>/forecast/<ticker>/update-weighting', methods=['POST'])
def update_weighting(username, ticker):
    user = User.query.get(username)
    forecasts = user.get_forecast().get(ticker, None)
    for forecast_dict in forecasts:
        forecast = Forecast.query.get(forecast_dict['id'])
        forecast.weight = request.form[str(forecast_dict['id'])]
        db.session.add(forecast)
    db.session.commit()
    flash("Weighting successfully updated", 'success')
    return redirect(f'/user/{username}/forecast/{ticker}')



@app.route('/search', methods=["POST"])
def search():
    ticker = request.form["search-term"]
    return redirect(f'/search/{ticker}')


@app.route('/search/<ticker>')
def display_stock(ticker):
    stock = Stock.get_stock(ticker)
    price = get_price(ticker)
    if stock and price: # if both stock and price are not None
        stock_data = stock.serialize()
        cur_price = format_num(
            price['cur_price'])
        equity = True
        if stock_data['type'].upper() != 'EQUITY':
            equity = False
        user_forecast_data = stock.get_forecast_data()
        for k in stock_data.keys(): # format all items to display nicely on UI
            if stock_data[k] == None:
                stock_data[k] = 'N/A'
            elif not isinstance(stock_data[k], numbers.Number):
                pass
            elif k == 'rev_estimate':
                stock_data[k] = "{:,.2f}".format(stock_data[k] * 100)
            elif k == 'market_cap':
                stock_data[k] = "{:,.2f}".format(stock_data[k] / 1000000000)
            else:
                stock_data[k] = "{:,.2f}".format(stock_data[k])
        up_to_date = (datetime.datetime.today() - stock_data['last_updated']).seconds < 1800
        return render_template('stock-details.html', data=stock_data, price=price,
                               cur_price=cur_price, forecast_data=user_forecast_data, equity=equity, up_to_date=up_to_date)
    else:
        return render_template('notfound.html', term=ticker)


@app.route('/search/<ticker>/valuation')
def val_summary(ticker):
    stock = Stock.get_stock(ticker)
    if stock and stock.type == "EQUITY":
        data = stock.serialize()
        login_form = LoginForm()
        save_form = SaveForecastForm()
        forecast_data = stock.get_forecast_data()
        for k in data: # format all % items to display nicely on UI
            if 'avg' in k:
                data[k] = "{:,.2f}".format(data[k] * 100)
        return render_template('stock-valuation.html', data=data['financials'], login_form=login_form, save_form=save_form, user=g.user, forecast_data=forecast_data, info=data)
    else:
        return render_template('notfound.html', term=f"{ticker}'s valuation")


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
        return (None, 401)  # return unauthorized if not signed in
