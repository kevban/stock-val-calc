from random import *
from models import Forecast, Stock, User, db
from app import app

# This file is used to create some dummy data and perform full CRUD with a wide range of stocks
# to 1) have some dummy data when the app launches, and 2) test that the backend works.

with app.app_context():
    db.drop_all()
    db.create_all()


    most_traded_stock = []

    most_traded_stock.append('AMZN')
    most_traded_stock.append('AAPL')
    most_traded_stock.append('AMD')
    most_traded_stock.append('NIO')
    most_traded_stock.append('CCL')
    most_traded_stock.append('LUMN')
    most_traded_stock.append('GOOGL')
    most_traded_stock.append('META')
    most_traded_stock.append('GOLD')
    most_traded_stock.append('F')
    most_traded_stock.append('TSLA')
    most_traded_stock.append('ROKU')
    most_traded_stock.append('SOFI')
    most_traded_stock.append('VRAX')
    most_traded_stock.append('RIG')
    most_traded_stock.append('PBR')
    most_traded_stock.append('NVDA')
    most_traded_stock.append('GOOG')
    most_traded_stock.append('T')
    most_traded_stock.append('INTC')
    most_traded_stock.append('VALE')
    most_traded_stock.append('MSFT')
    most_traded_stock.append('PLTR')
    most_traded_stock.append('WBD')
    most_traded_stock.append('PTON')
    most_traded_stock.append('ITUB')
    most_traded_stock.append('BBD')
    most_traded_stock.append('NKLA')
    most_traded_stock.append('SNAP')
    most_traded_stock.append('NU')
    most_traded_stock.append('ABEV')
    most_traded_stock.append('BAC')
    most_traded_stock.append('OPEN')
    most_traded_stock.append('CMCSA')
    most_traded_stock.append('UBER')
    most_traded_stock.append('PYPL')
    most_traded_stock.append('FIS')
    most_traded_stock.append('NOK')
    most_traded_stock.append('AAL')
    most_traded_stock.append('QCOM')
    most_traded_stock.append('RUN')
    most_traded_stock.append('XPEV')
    most_traded_stock.append('ET')
    most_traded_stock.append('SHOP')
    most_traded_stock.append('BABA')
    most_traded_stock.append('NYCB')
    most_traded_stock.append('HOOD')
    most_traded_stock.append('NCLH')
    most_traded_stock.append('VZ')
    most_traded_stock.append('DKNG')
    most_traded_stock.append('SWN')
    most_traded_stock.append('SQ')
    most_traded_stock.append('PARA')
    most_traded_stock.append('UAA')
    most_traded_stock.append('STON')
    most_traded_stock.append('PFE')
    most_traded_stock.append('KGC')
    most_traded_stock.append('CSX')
    most_traded_stock.append('BTU')
    most_traded_stock.append('AUY')
    most_traded_stock.append('SIRI')
    most_traded_stock.append('PINS')
    most_traded_stock.append('LI')
    most_traded_stock.append('TLRY')
    most_traded_stock.append('TELL')
    most_traded_stock.append('DVN')
    most_traded_stock.append('CSCO')
    most_traded_stock.append('PCG')
    most_traded_stock.append('WFC')
    most_traded_stock.append('XOM')
    most_traded_stock.append('FTNT')
    most_traded_stock.append('MRVL')
    most_traded_stock.append('MRO')
    most_traded_stock.append('AMC')
    most_traded_stock.append('PRVB')
    most_traded_stock.append('GRAB')
    most_traded_stock.append('KMI')
    most_traded_stock.append('BA')
    most_traded_stock.append('CVNA')
    most_traded_stock.append('MARA')
    most_traded_stock.append('ATUS')
    most_traded_stock.append('C')
    most_traded_stock.append('PBR-A')
    most_traded_stock.append('SLB')
    most_traded_stock.append('DNA')
    most_traded_stock.append('NNDM')
    most_traded_stock.append('IQ')
    most_traded_stock.append('FCX')
    most_traded_stock.append('PLUG')
    most_traded_stock.append('EXC')
    most_traded_stock.append('RCL')
    most_traded_stock.append('CGC')
    most_traded_stock.append('MPW')
    most_traded_stock.append('MGM')
    most_traded_stock.append('COIN')
    most_traded_stock.append('LYFT')
    most_traded_stock.append('ERIC')
    most_traded_stock.append('EBAY')
    most_traded_stock.append('TEVA')
    most_traded_stock.append('HBAN')
    most_traded_stock.append('CLF')
    most_traded_stock.append('AGNC')
    most_traded_stock.append('RBLX')
    most_traded_stock.append('COMM')
    most_traded_stock.append('COP')
    most_traded_stock.append('CS')
    most_traded_stock.append('EW')
    most_traded_stock.append('ETSY')
    most_traded_stock.append('PDD')
    most_traded_stock.append('USB')
    most_traded_stock.append('BTG')
    most_traded_stock.append('OXY')
    most_traded_stock.append('MU')
    most_traded_stock.append('GFI')
    most_traded_stock.append('FTI')
    most_traded_stock.append('JPM')
    most_traded_stock.append('AUPH')
    most_traded_stock.append('IS')
    most_traded_stock.append('STNE')
    most_traded_stock.append('GM')
    most_traded_stock.append('SPR')
    most_traded_stock.append('DASH')
    most_traded_stock.append('CIG')
    most_traded_stock.append('STLA')
    most_traded_stock.append('NEM')
    most_traded_stock.append('KEY')
    most_traded_stock.append('RIOT')
    most_traded_stock.append('INFY')
    most_traded_stock.append('GSAT')
    most_traded_stock.append('FUBO')
    most_traded_stock.append('PANW')
    most_traded_stock.append('CVE')
    most_traded_stock.append('JD')
    most_traded_stock.append('HPE')
    most_traded_stock.append('TSM')
    most_traded_stock.append('AFRM')
    most_traded_stock.append('FCEL')
    most_traded_stock.append('LCID')
    most_traded_stock.append('DDOG')
    most_traded_stock.append('VMEO')
    most_traded_stock.append('HBI')
    most_traded_stock.append('DAL')
    most_traded_stock.append('ABNB')
    most_traded_stock.append('LAZR')
    most_traded_stock.append('JBLU')
    most_traded_stock.append('UMC')
    most_traded_stock.append('HST')
    most_traded_stock.append('RCM')
    most_traded_stock.append('MRK')
    most_traded_stock.append('KDP')
    most_traded_stock.append('AMCR')
    most_traded_stock.append('APA')
    most_traded_stock.append('LNC')
    most_traded_stock.append('SABR')
    most_traded_stock.append('BCS')
    most_traded_stock.append('BEKE')
    most_traded_stock.append('MRNA')
    most_traded_stock.append('KO')
    most_traded_stock.append('BMY')
    most_traded_stock.append('TSP')
    most_traded_stock.append('DIS')
    most_traded_stock.append('AXL')
    most_traded_stock.append('ACI')
    most_traded_stock.append('SBUX')
    most_traded_stock.append('NTR')
    most_traded_stock.append('CANO')
    most_traded_stock.append('GE')
    most_traded_stock.append('TFC')
    most_traded_stock.append('GPS')
    most_traded_stock.append('KD')
    most_traded_stock.append('HAL')
    most_traded_stock.append('U')
    most_traded_stock.append('X')
    most_traded_stock.append('ASX')
    most_traded_stock.append('CVS')
    most_traded_stock.append('ING')
    most_traded_stock.append('GGB')
    most_traded_stock.append('GILD')
    most_traded_stock.append('BBBY')
    most_traded_stock.append('BP')
    most_traded_stock.append('V')
    most_traded_stock.append('CTSH')
    most_traded_stock.append('K')
    most_traded_stock.append('MDLZ')
    most_traded_stock.append('W')
    most_traded_stock.append('ZING')
    most_traded_stock.append('RIVN')
    most_traded_stock.append('ZTS')
    most_traded_stock.append('MOS')
    most_traded_stock.append('VTRS')
    most_traded_stock.append('BILI')
    most_traded_stock.append('HLN')
    most_traded_stock.append('TV')
    most_traded_stock.append('JCI')
    most_traded_stock.append('UA')
    most_traded_stock.append('GPN')
    most_traded_stock.append('BKR')
    most_traded_stock.append('IBN')
    most_traded_stock.append('RITM')
    most_traded_stock.append('ZI')

    user = User.signup('seedfile', 'skqd123asd')
    db.session.commit()

    for i in range(len(most_traded_stock)):
        print(most_traded_stock[i])
        stock = Stock.get_stock(most_traded_stock[i])
        x = randint(1, 5)
        if i < 30:
            x = randint(40, 80)
        elif i < 60:
            x = randint(20, 50)
        elif i < 120:
            x = randint(5, 25)
        for k in range(x):
            rand_num = randint(-40, 60) / 100
            pe = -1
            ps = -1
            if stock.pe_ratio:
                pe = stock.pe_ratio * (1 + rand_num)
            elif stock.ps_ratio:   
                ps = stock.ps_ratio * (1 + rand_num)
            else:
                ps = 20 (1 + rand_num)
            
            forecast = {
                'ticker': stock.ticker,
                'target': (stock.target_price or stock.cur_price) * (1 + rand_num),
                'name': 'seeddata',
                'description': 'seeddata',
                'avg-growth': stock.avg_growth * (1 + rand_num),
                'avg-cogs': stock.avg_cogs * (1 - rand_num),
                'avg-opex': stock.avg_opex * (1 - rand_num),
                'avg-depreciation': stock.avg_depreciation * (1 - rand_num),
                'avg-other': stock.avg_other * (1 - rand_num),
                'avg-tax': stock.avg_tax * (1 - rand_num),
                'avg-dividend': stock.avg_dividend * (1 - rand_num),
                'pe-actual': pe,
                'ps': ps,
                'shares_out': stock.shares_out,
                'period': []
            }
            Forecast.save_forecast(forecast, user.username)