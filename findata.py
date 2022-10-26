from ast import Raise
from models import *
from helper import *
import yfinance as yf


def get_stock_data(ticker):
    """ This function get the relevant stock data from yfinance using the 
        ticker module. The data is returned in a dictionary.

        Return None if ticker is invalid.
    """
    stock = yf.Ticker(ticker)
    fin_data = stock.financials
    cf_data = stock.get_cashflow()
    stock_info = stock.get_info()
    stock_analysis = stock.get_analysis()
    if (stock_info['regularMarketPrice']):
        for i in range(0, len(fin_data.loc['Selling General Administrative'])):
            fin_data.loc['Selling General Administrative'][i] = fin_data.loc['Selling General Administrative'][i] - \
                cf_data.loc['Depreciation'][i] + \
                fin_data.loc['Research Development'][i]
        stock_data = {
            # basic info
            'ticker': ticker.upper(),
            'current_price': stock_info.get('regularMarketPrice', None),
            'target_price': stock_info.get('targetMeanPrice', None),
            'shares_out': stock_info.get('sharesOutstanding', None),
            'eps': stock_info.get('trailingEps', None),
            'beta': stock_info.get('beta', None),
            'fifty_two_wk_low': stock_info.get('fiftyTwoWeekLow', None),
            'fifty_two_wk_high': stock_info.get('fiftyTwoWeekHigh', None),
            'de_ratio': stock_info.get('debtToEquity', None),
            'market_cap': stock_info.get('marketCap', None),
            # valuations
            'ev_ebitda': stock_info.get('enterpriseToEbitda', None),
            'ev_sales': stock_info.get('enterpriseToRevenue', None),
            'pb_ratio': stock_info.get('priceToBook', None),
            'pe_ratio': stock_info.get('trailingPE', None),
            'ps_ratio': stock_info.get('priceToSalesTrailing12Months', None),
            'peg_ratio': stock_info.get('pegRatio', None),
            # technicals
            'two_hundred_day_ma': stock_info.get('twoHundredDayAverage', None),
            'fifty_day_ma': stock_info.get('fiftyDayAverage', None),
            'avg_volume': stock_info.get('averageVolume', None),
            'avg_volume_10d': stock_info.get('averageVolume10days', None),
            # financials
            'net_income': fin_data.loc['Net Income'][::-1],
            'revenue': fin_data.loc['Total Revenue'][::-1],
            'cogs': fin_data.loc['Cost Of Revenue'][::-1],
            'opex': fin_data.loc['Selling General Administrative'][::-1],
            'depreciation': cf_data.loc['Depreciation'][::-1],
            'other': fin_data.loc['Total Other Income Expense Net'][::-1],
            'tax': fin_data.loc['Income Tax Expense'][::-1],
            'eps_estimate': stock_analysis['Earnings Estimate Avg']['+1Y'],
            'rev_estimate': stock_analysis['Revenue Estimate Avg']['+1Y'],
            'price_estimate_low': stock_info['targetLowPrice'],
            'price_estimate_high': stock_info['targetHighPrice'],
            'periods': fin_data.columns[::-1],
        }
        netincome = stock_data['revenue'][0] - \
            stock_data['cogs'][0] - stock_data['depreciation'][0] - \
            stock_data['opex'][0] + \
            stock_data['other'][0] - stock_data['tax'][0]

        # stock information
        assert stock_data['net_income'][0] == netincome
        return stock_data
    else:
        return None


def get_price(symbol):
    """ This function get the current price of a stock .
        If the symbol is invalid, return None
    """
    ticker = yf.Ticker(symbol)

    # get the 30 day market data
    history = ticker.history(period="1mo", interval='1d')

    # if the data is empty, ticker does not exist, and return None
    if history.empty:
        return None
    # otherwise, return the most recent quote
    else:
        # transform the dataframe to a list of dates, prices, and volume
        hist_data = list(zip(history.index, history.Close, history.Volume))
        dates = [str(row[0])[0:10] for row in hist_data]
        prices = [row[1] for row in hist_data]
        volume = [row[2] for row in hist_data]
        return {
            'hist_30d_dates': dates,
            'hist_30d_prices': prices,
            'hist_30d_volumes': volume
        }
