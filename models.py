from http.client import PRECONDITION_FAILED, PRECONDITION_REQUIRED
from flask_sqlalchemy import SQLAlchemy
from findata import get_price, get_stock_data
from flask_bcrypt import Bcrypt
from datetime import datetime


"""Models for stockval."""

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    with app.app_context():

        db.app = app
        db.init_app(app)
        # db.drop_all()
        db.create_all()


class Stock(db.Model):
    __tablename__ = 'stocks'

    ticker = db.Column(db.String, primary_key=True)

    shares_out = db.Column(db.BigInteger, nullable=False)
    eps_estimate = db.Column(db.Float)
    rev_estimate = db.Column(db.BigInteger)
    price_estimate_high = db.Column(db.Float)
    price_estimate_low = db.Column(db.Float)
    target_price = db.Column(db.Float)
    eps = db.Column(db.Float)
    beta = db.Column(db.Float)
    fifty_two_wk_low = db.Column(db.Float)
    fifty_two_wk_high = db.Column(db.Float)
    de_ratio = db.Column(db.Float)
    market_cap = db.Column(db.BigInteger)
    ev_ebitda = db.Column(db.Float)
    ps_ratio = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    two_hundred_day_ma = db.Column(db.Float)
    fifty_day_ma = db.Column(db.Float)
    avg_volume = db.Column(db.BigInteger)
    avg_volume_10d = db.Column(db.BigInteger)

    @classmethod
    def add_stock(cls, ticker):
        """Add a stock to database given ticker, return it

        if the ticker does not exist, return None
        """
        stock_data = get_stock_data(ticker)
        if stock_data != None:
            stock = Stock(
                ticker=stock_data['ticker'],
                shares_out=stock_data['shares_out'],
                eps_estimate=stock_data['eps_estimate'],
                rev_estimate=stock_data['rev_estimate'],
                price_estimate_high=stock_data['price_estimate_high'],
                price_estimate_low=stock_data['price_estimate_low'],
                target_price=stock_data['price_estimate_low'],
                eps=stock_data['eps'],
                beta=stock_data['beta'],
                fifty_two_wk_low=stock_data['fifty_two_wk_low'],
                fifty_two_wk_high=stock_data['fifty_two_wk_high'],
                de_ratio=stock_data['de_ratio'],
                market_cap=stock_data['market_cap'],
                ev_ebitda=stock_data['ev_ebitda'],
                ps_ratio=stock_data['ps_ratio'],
                pe_ratio=stock_data['pe_ratio'],
                pb_ratio=stock_data['pb_ratio'],
                two_hundred_day_ma=stock_data['two_hundred_day_ma'],
                fifty_day_ma=stock_data['fifty_day_ma'],
                avg_volume=stock_data['avg_volume'],
                avg_volume_10d=stock_data['avg_volume_10d'],
            )
            for i in range(len(stock_data['periods'])):
                financial = Financial(
                    company_ticker=ticker, period=stock_data['periods'][i].year,
                    revenue=stock_data['revenue'][i], cogs=stock_data['cogs'][i],
                    opex=stock_data['opex'][i], depreciation=stock_data['depreciation'][i],
                    other=stock_data['other'][i], tax=stock_data['tax'][i], net_income=stock_data['net_income'][i])
                db.session.add(financial)
            db.session.add(stock)
            db.session.commit()
            return stock
        else:
            return None

    def serialize(self):
        """Return a dictionary of stock data"""

        financials = {
            'ticker': [],
            'period': [],
            'revenue': [],
            'cogs': [],
            'opex': [],
            'depreciation': [],
            'other': [],
            'tax': [],
            'net_income': []
        }
        for financial in self.financials:
            serialized = financial.serialize()
            for key in serialized:
                financials[key].append(serialized[key])

        return {
            "ticker": self.ticker,
            "financials": financials,
            "shares_out": self.shares_out,
            "eps_estimate": self.eps_estimate,
            "rev_estimate": self.rev_estimate,
            "price_estimate_high": self.price_estimate_high,
            "price_estimate_low": self.price_estimate_low
        }

    @classmethod
    def get_stock(cls, ticker):
        """Return the stock instance with the ticker. Update its current price.

            If ticker does not exist, add it to the database

        """

        stock = cls.query.get(ticker)
        if stock:
            stock.price = get_price(ticker)
            db.session.add(stock)
            db.session.commit()
            return stock
        else:
            return cls.add_stock(ticker)


class Financial(db.Model):
    __tablename__ = 'financials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_ticker = db.Column(
        db.String, db.ForeignKey('stocks.ticker'), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.BigInteger)
    cogs = db.Column(db.BigInteger)
    opex = db.Column(db.BigInteger)
    depreciation = db.Column(db.BigInteger)
    other = db.Column(db.BigInteger)
    tax = db.Column(db.BigInteger)
    net_income = db.Column(db.BigInteger)

    company = db.relationship('Stock', backref='financials')

    def serialize(self):
        """Return a dictionary of stock financials"""

        return {
            'ticker': self.company_ticker,
            'period': self.period,
            'revenue': self.revenue,
            'cogs': self.cogs,
            'opex': self.opex,
            'depreciation': self.depreciation,
            'other': self.other,
            'tax': self.tax,
            'net_income': self.net_income
        }


class PriceHistory(db.Model):
    """30-day market data for each company"""

    __tablename__ = "history"

    # primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign key - company
    ticker = db.Column(db.String, db.ForeignKey(
        'stocks.ticker'), nullable=False)

    # data
    date = db.Column(db.Date)
    price = db.Column(db.Float)
    volume = db.Column(db.Integer)
    stock = db.relationship('Stock', backref='history_30d')

    @classmethod
    def update(cls, company):
        """ Update the historic prices and volumes using stock info"""

        # first delete all existing market data about the company
        cls.query.filter(cls.ticker == company['ticker']).delete()

        # create a new entry in the database for each data point in
        # market data
        for i in range(len(company['hist_30d_dates'])):
            new_record = cls(
                ticker=company['ticker'],
                date=company['hist_30d_dates'][i],
                price=company['hist_30d_prices'][i],
                volume=company['hist_30d_volumes'][i])
            db.session.add(new_record)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    def get_forecast(self):
        """Get all saved forecasts that user made in dict format"""

        dict_to_return = {}
        for forecast in self.forecasts:
            if not dict_to_return.get(forecast.ticker, None):
                dict_to_return[forecast.ticker] = []
            dict_to_return[forecast.ticker].append(forecast.serialize())
        return dict_to_return


class Forecast(db.Model):
    __tablename__ = 'forecasts'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String, db.ForeignKey(
        'users.username'), nullable=False)
    ticker = db.Column(db.String, db.ForeignKey(
        'stocks.ticker'), nullable=False)
    target = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String)
    description = db.Column(db.String)
    weight = db.Column(db.Float, default=1)

    user = db.relationship('User', backref='forecasts')
    stock = db.relationship('Stock', backref='user_forecasts')

    @classmethod
    def save_forecast(cls, forecasts, username):
        new_forecast = Forecast(
            username=username, ticker=forecasts['ticker'], target=forecasts['price'], name=forecasts['name'], description=forecasts['description'])
        db.session.add(new_forecast)
        db.session.commit()
        for i in range(len(forecasts['period'])):
            forecast_financial = ForecastFinancials(forecast_id=new_forecast.id,
                                                    period=forecasts['period'][i],
                                                    revenue=forecasts['revenue'][i],
                                                    cogs=forecasts['cogs'][i],
                                                    opex=forecasts['opex'][i],
                                                    depreciation=forecasts['depreciation'][i],
                                                    other=forecasts['other'][i],
                                                    tax=forecasts['tax'][i],
                                                    net_income=forecasts['net-income'][i])
            db.session.add(forecast_financial)
        db.session.commit()
        return new_forecast.serialize()

    def serialize(self):
        """Return a dictionary representation of the forecast"""
        financials = {
            'ticker': self.ticker,
            'user': self.username,
            'date': self.date,
            'target': self.target,
            'weight': self.weight,
            'period': [],
            'revenue': [],
            'cogs': [],
            'opex': [],
            'depreciation': [],
            'other': [],
            'tax': [],
            'net_income': []
        }
        for financial in self.forecast_financials:
            serialized = financial.serialize()
            for key in serialized:
                financials[key].append(serialized[key])
        return financials


class ForecastFinancials(db.Model):
    __tablename__ = 'forecast_financials'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    forecast_id = db.Column(
        db.Integer, db.ForeignKey('forecasts.id'), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.BigInteger)
    cogs = db.Column(db.BigInteger)
    opex = db.Column(db.BigInteger)
    depreciation = db.Column(db.BigInteger)
    other = db.Column(db.BigInteger)
    tax = db.Column(db.BigInteger)
    net_income = db.Column(db.BigInteger)

    forecast = db.relationship('Forecast', backref='forecast_financials')

    def serialize(self):
        return {
            'period': self.period,
            'revenue': self.revenue,
            'cogs': self.cogs,
            'opex': self.opex,
            'depreciation': self.depreciation,
            'other': self.other,
            'tax': self.tax,
            'net_income': self.net_income
        }
