# Stock Valuation Calculator
A web app that allows user to quickly calculate intrinsic value of publically traded stocks through a fundamental analysis in less than a minute!

[Click here to launch the app](https://stock-val-calc-production.up.railway.app)

## What does it do?
By searching any stock ticker, the app will quickly pull up historical financial information from prior period financial statements, and populate a financial forecast model with some default assumptions. From here, the user can adjust the model assumptions, and calculate the intrinsic value of a stock. The user can also reference other user's forecasts to compare with their assumptions.
## How to use?
1. Begin by searching a publically traded stock ticker (e.g. MSFT)
2. Click 'Start Valuation'  
![screenshot](/docs/sceenshot2.JPG)
3. Adjust inputs if needed.
4. The target price and return will be automatically calculated at the bottom of the page.  
![screenshot](/docs/screenshot3.JPG)
5. Signup and save your forecast for future reference!
## Key features
- Quickly generating a financial model with historic financial statements.
- Provide guidance on assumptions using data from other user's forecasts.  
![screenshot](/docs/screenshot4.JPG)
- Saving and sharing financial models.
- Building multiple models to reflect different scenarios for one stock.  
![screenshot](/docs/screenshot5.JPG)
## Tech stack
- Frontend - JavaScript, HTML, CSS, Bootstrap.
- Backend - Python Flask.
- Database - PostgreSQL
- FinanceAPI - [yfinance](https://github.com/ranaroussi/yfinance)
## Other
- This project was made for Springboard Capstone project 1
- For questions related to the valuation methodology, please refer to [FAQ](/docs/faq.md)
- [Database schema](/docs/crows-foot-diagram.png)
