from flask import Flask, render_template, redirect, request, jsonify, session, flash, g
from models import *
from forms import LoginForm, SaveForecastForm
from helper import format_num
from sqlalchemy.exc import IntegrityError
import datetime
import os

from findata import *

"""stockval application."""

# setting up app, getting environment variables from Railway
app = Flask(__name__)
database_url = os.environ.get('SQLALCHEMY_URL', 'postgresql:///stockval')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'abc123')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# Initializing Postgres database
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
    """Render the homepage (search)"""

    return render_template('home.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup_page():
    """Render the signup page"""

    # If user already logged in, redirect to homepage
    if g.user:
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit(): # if user submits the form with valid information, continue to signup process
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

        # render the signup form if it is a get request, or input is invalid
        return render_template('signup.html', form=form, login=False)

@app.route('/update/<ticker>')
def update_stock(ticker):
    """Allow user to update stock information when clicking the update button"""

    stock = Stock.query.get(ticker)
    # If the stock exist in the databse, update the stock with new information
    if stock:
        stock.update_stock()
        return redirect(f'/search/{ticker}')
    else:
        return render_template('notfound.html', term=ticker)

@app.route('/login', methods=['POST', 'GET'])
def login_page():
    """Render the user login page"""
    
    # If user is already logged in, redirect to homepage
    if g.user:
        return redirect('/')
    # Otherwise, follow the same process as signup route, except pass login as True
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
    """Logout the user when the user clicks logout button"""

    # logg the user out if user is logged in
    if g.user:
        session.pop('username')
        flash("You have successully logged out", 'success')
    return redirect('/')


@app.route('/user/<username>')
def user_details(username):
    """Render a page showing user details"""
    
    user = User.query.get(username)
    # if user exist in the database
    if user:
        # get the stocks that user had forecasts for
        covered_stocks = user.get_forecast_summary()
        # adjust the format of the result to display nicely
        for stock in covered_stocks:
            stock['date'] = datetime.date.strftime(stock['date'], "%m/%d/%Y") # in mm/dd/yyyy
            stock['target'] = "{:,.2f}".format(stock['target']) # in $ amt format
        return render_template('user-details.html', user=user, covered_stocks=covered_stocks, g=g)
    else:
        return render_template('notfound.html', term=username)


@app.route('/user/<username>/forecast/<ticker>')
def user_forecast_details(username, ticker):
    """show details about a user's forecasts for a stock"""

    user = User.query.get(username)
    forecasts = user.get_forecast().get(ticker, None)
    # if both the user and the forecasts exist
    if user and forecasts:
        # format the forecast information to display nicely
        for forecast in forecasts:
            forecast['date'] = datetime.date.strftime(forecast['date'], "%m/%d/%Y")
            forecast['target'] = "{:,.2f}".format(forecast['target'])
        return render_template('user-forecast-details.html', forecasts=forecasts, g=g, user=user, ticker=ticker)
    else:
        return render_template('notfound.html', term=f'{username}s {ticker} forecast')


@app.route('/forecast/<int:forecast_id>')
def display_forecast(forecast_id):
    """Display one particular user forecast given forecast_id"""

    # getting the forecast in the database
    forecast = Forecast.query.get(forecast_id)
    if forecast:
        # calculating the subtotals(e.g. gross income) for the forecast to display
        forecast_dict = forecast.serialize()
        price = get_price(forecast_dict['ticker'])
        forecast_dict['gross_income'] = [sum(i) for i in zip(forecast_dict['revenue'], forecast_dict['cogs'])]
        forecast_dict['ebitda'] = [sum(i) for i in zip(forecast_dict['gross_income'], forecast_dict['opex'])]
        forecast_dict['operating_income'] = [sum(i) for i in zip(forecast_dict['ebitda'], forecast_dict['depreciation'])]
        forecast_dict['ebt'] = [sum(i) for i in zip(forecast_dict['operating_income'], forecast_dict['other'])]
        forecast_dict['last_eps'] = forecast_dict['net_income'][len(forecast_dict['net_income']) - 1] / forecast_dict['shares_out']
        forecast_dict['date'] = datetime.date.strftime(forecast_dict['date'], "%m/%d/%Y")

        # if the forecast uses price to sales, set multiple to ps, otherwise set multiple to pe
        if forecast_dict['ps'] != -1:
            forecast_dict['multiple'] = forecast_dict['ps']
        else:
            forecast_dict['multiple'] = forecast_dict['pe']
        # calculating subtotals in the valuation section (e.g. dividends per share)
        forecast_dict['price'] = forecast_dict['last_eps'] * forecast_dict['multiple']
        forecast_dict['dividend_per_share'] = sum(forecast_dict['dividend']) / forecast_dict['shares_out']
        # the curprice will be based on the stock's current price in the market
        forecast_dict['return'] = (forecast_dict['target'] / price['cur_price']) ** (1/4) - 1


        # formating display to show nicely on UI
        for k in forecast_dict:
            if k in ['revenue', 'cogs', 'opex', 'depreciation', 'other', 'tax', 'net_income', 'dividend', 'ebitda', 'operating_income', 'ebt', 'gross_income']:
                for i in range(len(forecast_dict[k])):
                    forecast_dict[k][i] = "${:,.0f}".format(forecast_dict[k][i] / 1000000) # show as $ amt in millions
            elif k == 'return':
                forecast_dict[k] = "{:,.2f}%".format(forecast_dict[k]*100) # show as %
            elif k in ['multiple', 'last_eps', 'price', 'dividend_per_share', 'target']:
                forecast_dict[k] = "{:,.2f}".format(forecast_dict[k]) # show as $ amt
    
        return render_template('forecast-details.html', forecast=forecast_dict, g=g)
    else: # show the not found page if forecast id does not exist
        return render_template('notfound.html', term='Forecast')


@app.route('/user/<username>/forecast/<ticker>/update-weighting', methods=['POST'])
def update_weighting(username, ticker):
    """Allows the user to update weightings for a particular stock"""

    # get user and forecasts given ticker and username
    user = User.query.get(username)
    forecasts = user.get_forecast().get(ticker, None)
    if forecasts and user:
        # Update the forecast's weight for each forecast in the user's forecasts for
        # the particular stock
        for forecast_dict in forecasts:
            forecast = Forecast.query.get(forecast_dict['id'])
            new_weighting = float(request.form[str(forecast_dict['id'])]) # get the new weighting from form
            # If the user input is valid, update the weighting
            if isinstance(new_weighting, numbers.Number):
                forecast.weight = request.form[str(forecast_dict['id'])]
                db.session.add(forecast)
                db.session.commit()
            else: # otherwise, rerender the page and show a warning
                flash("Please enter a valid weighting", 'danger')
                return redirect('')
        flash("Weighting successfully updated", 'success')
        return redirect(f'/user/{username}/forecast/{ticker}')
    else:
        return render_template('notfound.html', term="Forecast")



@app.route('/search', methods=["POST"])
def search():
    """Search a stock ticker given search term"""

    ticker = request.form["search-term"]
    return redirect(f'/search/{ticker}')


@app.route('/search/<ticker>')
def display_stock(ticker):
    """Display information about a stock"""

    stock = Stock.get_stock(ticker)
    price = get_price(ticker)
    if stock and price: # if both stock and price are not None
        stock_data = stock.serialize()
        cur_price = format_num(
            price['cur_price'])
        equity = True
        # If the stock is not an equity (e.g. an ETF), flag it so that the page
        # will not include valuation
        if stock_data['type'].upper() != 'EQUITY':
            equity = False
        # updating the stock's current price in the database
        stock.update_price(price['cur_price'])
        user_forecast_data = stock.get_forecast_data()
        for k in stock_data.keys(): # format all items to display nicely on UI
            if stock_data[k] == None:
                stock_data[k] = 'N/A'
            elif not isinstance(stock_data[k], numbers.Number):
                pass
            elif k == 'rev_estimate':
                stock_data[k] = "{:,.2f}".format(stock_data[k] * 100) # in %
            elif k == 'market_cap':
                stock_data[k] = "{:,.2f}".format(stock_data[k] / 1000000000) # in $ billions
            else:
                stock_data[k] = "{:,.2f}".format(stock_data[k]) # in $
        up_to_date = (datetime.datetime.today() - stock_data['last_updated']).seconds < 1800
        return render_template('stock-details.html', data=stock_data, price=price,
                               cur_price=cur_price, forecast_data=user_forecast_data, equity=equity, up_to_date=up_to_date)
    else:
        return render_template('notfound.html', term=ticker)


@app.route('/search/<ticker>/valuation')
def val_summary(ticker):
    """Show the page for a stock valuation"""
    
    stock = Stock.get_stock(ticker)
    # continue only if the stock is an equity
    if stock and stock.type == "EQUITY":
        data = stock.serialize()
        # the two forms used to login/signup and save forecast
        login_form = LoginForm()
        save_form = SaveForecastForm()
        forecast_data = stock.get_forecast_data()
        for k in data: # format all % items to display nicely on UI
            if 'avg' in k:
                data[k] = "{:,.2f}".format(data[k] * 100) # in %
        return render_template('stock-valuation.html', data=data['financials'], login_form=login_form, save_form=save_form, user=g.user, forecast_data=forecast_data, info=data, histperiod=len(data['financials']['period']))
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
