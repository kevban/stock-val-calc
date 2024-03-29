import yfinance as yf
from currency_converter import CurrencyConverter
from helper import *


c = CurrencyConverter()


def get_stock_data(ticker):
    """ This function get the relevant stock data from yfinance using the 
        ticker module. The data is returned in a dictionary.

        Return None if ticker is invalid.
    """

    stock = yf.Ticker(ticker)
    fin_data = stock.financials
    cf_data = stock.get_cashflow()
    stock_info = stock.get_info()
    stock_fastinfo = stock.fast_info
    rev_forecast = stock.get_rev_forecast()
    # Checking if stock exist by seeing if it is actively quoted
    if (stock_info and stock_fastinfo['last_price']):
        # Removing DepreciationAndAmortization from SG&A, combining SG&A with R&D to simplify this line item.
        if ('Selling General And Administration' in fin_data.index):
            for i in range(0, len(fin_data.loc['Selling General And Administration'])):
                fin_data.loc['Selling General And Administration'][i] = (fin_data.loc['Gross Profit'][i] or 0) -\
                    (cf_data.loc['DepreciationAndAmortization'][i] or 0) -\
                    (fin_data.loc['Operating Income'][i] or 0)
        if ('Other Income Expense' in fin_data.index):
            for i in range(0, len(fin_data.loc['Other Income Expense'])):
                fin_data.loc['Other Income Expense'][i] = (fin_data.loc['Pretax Income'][i] or 0) -\
                    (fin_data.loc['Operating Income'][i] or 0)
        # Getting stock data
        stock_data = {
            # basic info
            'ticker': ticker.upper(),
            'current_price': stock_fastinfo.get('last_price', None),
            'target_price': stock_info.get('targetMeanPrice', None),
            'shares_out': stock_info.get('sharesOutstanding', None),
            'eps': stock_info.get('trailingEps', None),
            'beta': stock_info.get('beta', None),
            'fifty_two_wk_low': stock_fastinfo.get('yearLow', None),
            'fifty_two_wk_high': stock_fastinfo.get('yearHigh', None),
            'de_ratio': stock_info.get('debtToEquity', None),
            'market_cap': stock_fastinfo.get('marketCap', None),
            'type': stock_fastinfo.get('quoteType', None),
            # valuations
            'ev_ebitda': stock_info.get('enterpriseToEbitda', None),
            'ev_sales': stock_info.get('enterpriseToRevenue', None),
            'pb_ratio': stock_info.get('priceToBook', None),
            'pe_ratio': stock_info.get('trailingPE', None),
            'ps_ratio': stock_info.get('priceToSalesTrailing12Months', None),
            'peg_ratio': stock_info.get('pegRatio', None),
            # technicals
            'two_hundred_day_ma': stock_fastinfo.get('twoHundredDayAverage', None),
            'fifty_day_ma': stock_fastinfo.get('fiftyDayAverage', None),
            'avg_volume': stock_fastinfo.get('threeMonthAverageVolume', None),
            'avg_volume_10d': stock_fastinfo.get('tenDayAverageVolume', None),
            # financials, initialize them as 0 for now, add values later for Null amounts
            'net_income': [0] * len(fin_data.columns),
            'revenue': [0] * len(fin_data.columns),
            'cogs': [0] * len(fin_data.columns),
            'opex': [0] * len(fin_data.columns),
            'depreciation': [0] * len(fin_data.columns),
            'other': [0] * len(fin_data.columns),
            'tax': [0] * len(fin_data.columns),
            'periods': [],
            'dividend': [0] * len(fin_data.columns),
            # estimates
            'rev_estimate': 0,
            'price_estimate_low': stock_info.get('targetLowPrice', None),
            'price_estimate_high': stock_info.get('targetHighPrice', None)

        }
        # Getting financial info, check if they exist before storing them.
        if 'Net Income' in fin_data.index:
            stock_data['net_income'] = convert(
                fin_data.loc['Net Income'][::-1], stock_info['financialCurrency'])
        if 'Total Revenue' in fin_data.index:
            stock_data['revenue'] = convert(
                fin_data.loc['Total Revenue'][::-1], stock_info['financialCurrency'])
        if 'Cost Of Revenue' in fin_data.index:
            stock_data['cogs'] = convert(
                fin_data.loc['Cost Of Revenue'][::-1], stock_info['financialCurrency'])
        if 'Selling General And Administration' in fin_data.index:
            stock_data['opex'] = convert(
                fin_data.loc['Selling General And Administration'][::-1], stock_info['financialCurrency'])
        if 'DepreciationAndAmortization' in cf_data.index:
            stock_data['depreciation'] = convert(
                cf_data.loc['DepreciationAndAmortization'][::-1], stock_info['financialCurrency'])
        if 'Other Income Expense' in fin_data.index:
            stock_data['other'] = convert(
                fin_data.loc['Other Income Expense'][::-1], stock_info['financialCurrency'])
        if 'Tax Provision' in fin_data.index:
            stock_data['tax'] = convert(
                fin_data.loc['Tax Provision'][::-1], stock_info['financialCurrency'])
        if 'CashDividendsPaid' in cf_data.index:
            stock_data['dividend'] = convert(
                cf_data.loc['CashDividendsPaid'][::-1], stock_info['financialCurrency'])
        if not fin_data.empty:
            stock_data['periods'] = fin_data.columns[::-1]
        if stock_data['type'] == 'EQUITY' and rev_forecast is not None:
            if fin_data.loc['Total Revenue'][0] != 0:
                stock_data['rev_estimate'] = rev_forecast['growth'].mean()
            else:
                stock_data['rev_estimate'] = 1

        # Getting vertical analysis
        stock_data['avg_growth'] = get_avg(stock_data['revenue'], [])
        stock_data['avg_cogs'] = get_avg(
            stock_data['cogs'], stock_data['revenue'])
        stock_data['avg_opex'] = get_avg(
            stock_data['opex'], stock_data['revenue'])
        stock_data['avg_depreciation'] = get_avg(
            stock_data['depreciation'], stock_data['revenue'])
        stock_data['avg_other'] = get_avg(
            stock_data['other'], stock_data['revenue'])
        stock_data['avg_tax'] = get_avg(
            stock_data['tax'], stock_data['revenue'])
        stock_data['avg_dividend'] = get_avg(stock_data['dividend'], [])
        # Bellow checks if the calculation resulted the same amount as yahoo finance.
        # However, due to limitation of API, the final stock data may not be accurate for certain stocks
        # Therefore, they are commented out for the time being

        # netincome = stock_data['revenue'][0] - \
        #     stock_data['cogs'][0] - stock_data['DepreciationAndAmortization'][0] - \
        #     stock_data['opex'][0] + \
        #     stock_data['other'][0] - stock_data['tax'][0]
        # assert stock_data['net_income'][0] == netincome
        return stock_data
    else:
        return None


def get_price(symbol):
    """ This function get the current price of a stock.

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
        cur_price = prices[-1]
        # returning information in a dict format
        return {
            'hist_30d_dates': dates,
            'hist_30d_prices': prices,
            'hist_30d_volumes': volume,
            'cur_price': cur_price
        }


def convert(fin, cur):
    """Takes a dataframe, convert its rows to USD"""

    new_df = fin.fillna(0)
    # Hard coding TWD currency, as currency converter does not support it
    if cur == 'TWD':
        for i in range(len(new_df)):
            new_df[i] = new_df[i] * 0.031
    else:
        for i in range(len(new_df)):
            new_df[i] = c.convert(new_df[i], cur, 'USD')
    # casting the type to float, as sometimes type can change after conversion
    return new_df.astype(float)


def get_avg(item, rev):
    """Given a line item, calculate its average percentage of rev
        if rev is not given, calculate the growth rate instead
    """

    sum = 0.0
    # Calculating the % of revenue for each item, if rev is given
    if len(rev) > 0:
        for i in range(len(item)):
            if rev[i] == 0:
                sum += 1
            else:
                sum += item[i] / rev[i]
        return sum / len(item)
    # calculating the year over year growth of item, if rev is empty.
    else:
        for i in range(len(item)):
            if (item[i] != 0):
                sum = (item[-1] / item[i]) ** (1 / len(item)) - 1
                return sum
        return sum
