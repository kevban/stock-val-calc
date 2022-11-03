from __future__ import division
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from findata import get_price, get_stock_data
from flask_bcrypt import Bcrypt
from datetime import datetime
from helper import format_num


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

    shares_out = db.Column(db.BigInteger)
    rev_estimate = db.Column(db.Float)
    price_estimate_high = db.Column(db.Float)
    price_estimate_low = db.Column(db.Float)
    target_price = db.Column(db.Float)
    type = db.Column(db.String)
    eps = db.Column(db.Float)
    beta = db.Column(db.Float)
    fifty_two_wk_low = db.Column(db.Float)
    fifty_two_wk_high = db.Column(db.Float)
    de_ratio = db.Column(db.Float)
    market_cap = db.Column(db.BigInteger)
    ev_ebitda = db.Column(db.Float)
    ev_sales = db.Column(db.Float)
    ps_ratio = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    two_hundred_day_ma = db.Column(db.Float)
    fifty_day_ma = db.Column(db.Float)
    avg_volume = db.Column(db.BigInteger)
    avg_volume_10d = db.Column(db.BigInteger)
    avg_growth = db.Column(db.Float)
    avg_cogs = db.Column(db.Float)
    avg_opex = db.Column(db.Float)
    avg_depreciation = db.Column(db.Float)
    avg_other = db.Column(db.Float)
    avg_tax = db.Column(db.Float)
    avg_dividend = db.Column(db.Float)
    cur_price = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.today().replace(microsecond=0))
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
                rev_estimate=stock_data['rev_estimate'],
                price_estimate_high=stock_data['price_estimate_high'],
                price_estimate_low=stock_data['price_estimate_low'],
                target_price=stock_data['target_price'],
                type=stock_data['type'],
                eps=stock_data['eps'],
                beta=stock_data['beta'],
                fifty_two_wk_low=stock_data['fifty_two_wk_low'],
                fifty_two_wk_high=stock_data['fifty_two_wk_high'],
                de_ratio=stock_data['de_ratio'],
                market_cap=stock_data['market_cap'],
                ev_ebitda=stock_data['ev_ebitda'],
                ev_sales=stock_data['ev_sales'],
                ps_ratio=stock_data['ps_ratio'],
                pe_ratio=stock_data['pe_ratio'],
                pb_ratio=stock_data['pb_ratio'],
                two_hundred_day_ma=stock_data['two_hundred_day_ma'],
                fifty_day_ma=stock_data['fifty_day_ma'],
                avg_volume=stock_data['avg_volume'],
                avg_volume_10d=stock_data['avg_volume_10d'],
                avg_growth=stock_data['avg_growth'],
                avg_cogs=stock_data['avg_cogs'],
                avg_opex=stock_data['avg_opex'],
                avg_depreciation=stock_data['avg_depreciation'],
                avg_other=stock_data['avg_other'],
                avg_tax=stock_data['avg_tax'],
                avg_dividend=stock_data['avg_dividend'],
                cur_price=stock_data['current_price']
            )
            for i in range(len(stock_data['periods'])):
                financial = Financial(
                    company_ticker=ticker, period=stock_data['periods'][i].year,
                    revenue=stock_data['revenue'][i], cogs=stock_data['cogs'][i],
                    opex=stock_data['opex'][i], depreciation=stock_data['depreciation'][i],
                    other=stock_data['other'][i], tax=stock_data['tax'][i], net_income=stock_data['net_income'][i],
                    dividend=-stock_data['dividend'][i])
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
            'net_income': [],
            'dividend': []
        }
        for financial in self.financials:
            serialized = financial.serialize()
            for key in serialized:
                financials[key].append(serialized[key])

        return {
            "ticker": self.ticker,
            "financials": financials,
            "shares_out": self.shares_out,
            "rev_estimate": self.rev_estimate,
            "price_estimate_high": self.price_estimate_high,
            "price_estimate_low": self.price_estimate_low,
            "target_price": self.target_price,
            "eps": self.eps,
            "type": self.type,
            "beta": self.beta,
            "fifty_two_wk_low": self.fifty_two_wk_low,
            "fifty_two_wk_high": self.fifty_two_wk_high,
            "de_ratio": self.de_ratio,
            "market_cap": self.market_cap,
            "ev_ebitda": self.ev_ebitda,
            "ev_sales": self.ev_sales,
            "ps_ratio": self.ps_ratio,
            "pe_ratio": self.pe_ratio,
            "pb_ratio": self.pb_ratio,
            "two_hundred_day_ma": self.two_hundred_day_ma,
            "fifty_day_ma": self.fifty_day_ma,
            "avg_volume": self.avg_volume,
            "avg_volume_10d": self.avg_volume_10d,
            "avg_growth": self.avg_growth,
            "avg_cogs": self.avg_cogs,
            "avg_opex": self.avg_opex,
            "avg_depreciation": self.avg_depreciation,
            "avg_other": self.avg_other,
            "avg_tax": self.avg_tax,
            "avg_dividend": self.avg_dividend,
            'cur_price': self.cur_price,
            'last_updated': self.last_updated
        }

    @classmethod
    def get_stock(cls, ticker):
        """Return the stock instance given ticker.

            If ticker does not exist, add it to the database

        """

        ticker = ticker.upper()
        stock = cls.query.get(ticker)
        if stock:
            return stock
        else:
            return cls.add_stock(ticker)

    def update_price(self):
        """Update the stock price."""

    def update_stock(self):
        """Update the stock with new stock information retrieved form API
        """
        stock_data = get_stock_data(self.ticker)
        self.ticker=stock_data['ticker'],
        self.shares_out=stock_data['shares_out'],
        self.rev_estimate=stock_data['rev_estimate'],
        self.price_estimate_high=stock_data['price_estimate_high'],
        self.price_estimate_low=stock_data['price_estimate_low'],
        self.target_price=stock_data['target_price'],
        self.type=stock_data['type'],
        self.eps=stock_data['eps'],
        self.beta=stock_data['beta'],
        self.fifty_two_wk_low=stock_data['fifty_two_wk_low'],
        self.fifty_two_wk_high=stock_data['fifty_two_wk_high'],
        self.de_ratio=stock_data['de_ratio'],
        self.market_cap=stock_data['market_cap'],
        self.ev_ebitda=stock_data['ev_ebitda'],
        self.ev_sales=stock_data['ev_sales'],
        self.ps_ratio=stock_data['ps_ratio'],
        self.pe_ratio=stock_data['pe_ratio'],
        self.pb_ratio=stock_data['pb_ratio'],
        self.two_hundred_day_ma=stock_data['two_hundred_day_ma'],
        self.fifty_day_ma=stock_data['fifty_day_ma'],
        self.avg_volume=stock_data['avg_volume'],
        self.avg_volume_10d=stock_data['avg_volume_10d'],
        self.avg_growth=stock_data['avg_growth'],
        self.avg_cogs=stock_data['avg_cogs'],
        self.avg_opex=stock_data['avg_opex'],
        self.avg_depreciation=stock_data['avg_depreciation'],
        self.avg_other=stock_data['avg_other'],
        self.avg_tax=stock_data['avg_tax'],
        self.avg_dividend=stock_data['avg_dividend'],
        self.cur_price=stock_data['current_price'],
        self.last_updated=datetime.today().replace(microsecond=0)
        for financial in self.financials:
            db.session.delete(financial)
        for i in range(len(stock_data['periods'])):
            financial = Financial(
                company_ticker=self.ticker, period=stock_data['periods'][i].year,
                revenue=stock_data['revenue'][i], cogs=stock_data['cogs'][i],
                opex=stock_data['opex'][i], depreciation=stock_data['depreciation'][i],
                other=stock_data['other'][i], tax=stock_data['tax'][i], net_income=stock_data['net_income'][i],
                dividend=-stock_data['dividend'][i])
            db.session.add(financial)
        db.session.add(self)
        db.session.commit()

    def get_forecast_data(self):
        """Return a summary of user forecasts"""

        count = 0
        summary = {
            'growth': 0,
            'target': 0,
            'cogs': 0,
            'opex': 0,
            'depreciation': 0,
            'other': 0,
            'tax': 0,
            'dividend': 0,
            'pe': 0,
            'ps': 0,
            'count': 0
        }

        for forecast in self.user_forecasts:
            count += 1
            summary['growth'] += forecast.growth
            summary['target'] += forecast.target
            summary['cogs'] += forecast.cogs
            summary['opex'] += forecast.opex
            summary['depreciation'] += forecast.depreciation
            summary['other'] += forecast.other
            summary['tax'] += forecast.tax
            summary['dividend'] += forecast.dividend
            if forecast.ps != -1:
                summary['ps'] += forecast.pe
            else:
                summary['pe'] += forecast.ps

        if count > 0:
            for k in summary.keys():
                summary[k] /= count
                if k != 'target':
                    summary[k] = summary[k] * 100
                summary[k] = format_num(summary[k])

            summary['count'] = count
        return summary


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
    dividend = db.Column(db.BigInteger)

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
            'net_income': self.net_income,
            'dividend': self.dividend
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

    def get_forecast_summary(self):
        """Get a summary of user forecasts by stock in a list"""

        user_forecasts = self.get_forecast()
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

            stock['target'] /= total_weight
            if stock['target'] < price['hist_30d_prices'][len(price['hist_30d_prices']) - 1]:
                recommendation = 'Sell'
            stock['recommendation'] = recommendation
            stock['ratings'] = count
            covered_stocks.append(stock)
        return covered_stocks


class Forecast(db.Model):
    __tablename__ = 'forecasts'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String, db.ForeignKey(
        'users.username'), nullable=False)
    ticker = db.Column(db.String, db.ForeignKey(
        'stocks.ticker'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String)
    description = db.Column(db.String)
    weight = db.Column(db.Float, default=1)

    # key stats about the forecast
    target = db.Column(db.Float)
    growth = db.Column(db.Float)
    cogs = db.Column(db.Float)
    opex = db.Column(db.Float)
    depreciation = db.Column(db.Float)
    other = db.Column(db.Float)
    tax = db.Column(db.Float)
    net_income = db.Column(db.Float)
    dividend = db.Column(db.Float)
    pe = db.Column(db.Float)
    ps = db.Column(db.Float)
    shares_out = db.Column(db.Float)

    user = db.relationship('User', backref='forecasts')
    stock = db.relationship('Stock', backref='user_forecasts')

    @classmethod
    def save_forecast(cls, forecasts, username):
        new_forecast = Forecast(
            username=username,
            ticker=forecasts['ticker'],
            target=forecasts['target'],
            name=forecasts['name'],
            description=forecasts['description'],
            growth=forecasts['avg-growth'],
            cogs=forecasts['avg-cogs'],
            opex=forecasts['avg-opex'],
            depreciation=forecasts['avg-depreciation'],
            other=forecasts['avg-other'],
            tax=forecasts['avg-tax'],
            dividend=forecasts['avg-dividend'],
            pe=forecasts['pe'],
            ps=forecasts['ps'],
            shares_out=forecasts['shares_out']
        )
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
                                                    net_income=forecasts['net-income'][i],
                                                    dividend=forecasts['dividend'][i])
            db.session.add(forecast_financial)
        db.session.commit()
        return new_forecast.serialize()

    def serialize(self):
        """Return a dictionary representation of the forecast"""
        financials = {
            'id': self.id,
            'ticker': self.ticker,
            'username': self.username,
            'description': self.description,
            'name': self.name,
            'date': self.date,
            'target': self.target,
            'weight': self.weight,
            'growth': self.growth,
            'cogs': self.cogs,
            'opex': self.opex,
            'depreciation': self.depreciation,
            'other': self.other,
            'tax': self.tax,
            'dividend:': self.dividend,
            'pe': self.pe,
            'ps': self.ps,
            'shares_out': self.shares_out,
            'period': [],
            'revenue': [],
            'cogs': [],
            'opex': [],
            'depreciation': [],
            'other': [],
            'tax': [],
            'net_income': [],
            'dividend': []
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
    dividend = db.Column(db.BigInteger)

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
            'net_income': self.net_income,
            'dividend': self.dividend
        }
