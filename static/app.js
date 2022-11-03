let viewType = 0; // 0 is dollar amount, 1 is percent growth, 2 is percentage of revenue
let forecastPeriod = 4; // default to 4 forecast periods
let histPeriod = 4; // default to 4 historic periods
let ticker = $('#stock-ticker').text();
let multipleType = 0;

const signupForm = $('#signup-form');

const loginForm = $('#login-form');
const saveForm = $('#save-form');

const multipleSelector = $('#multiple-selector');
multipleSelector.on('change', 'input', function (evt) {
    multipleType = evt.target.value;
    RefreshView();
});

let forecastFinancials = {
    'revenue': [0, 0, 0, 0],
    'cogs': [0, 0, 0, 0],
    'gross-income': [0, 0, 0, 0],
    'opex': [0, 0, 0, 0],
    'ebitda': [0, 0, 0, 0],
    'depreciation': [0, 0, 0, 0],
    'operating-income': [0, 0, 0, 0],
    'other': [0, 0, 0, 0],
    'ebt': [0, 0, 0, 0],
    'tax': [0, 0, 0, 0],
    'net-income': [0, 0, 0, 0],
    'eps': [0, 0, 0, 0],
    'period': [0, 0, 0, 0],
    'dividend': [0, 0, 0, 0],
    'pe': 20,
    'price': 0,
    'target': 0,
    'return': 0.0,
    'divtot': 0
};
let finInfo = {}; // used to store stock financial data
let priceInfo = {}; // user to store historic prices

let historicFinancials = {};

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

const forecastTable = $('#forecast-table');
forecastTable.on("blur", ".table-input", UpdateFinancials);

const viewToggle = $('#view-toggle');
viewToggle.on('change', 'input', function (evt) {
    viewType = evt.target.value;
    RefreshView();
});

const peInput = $('#pe');
peInput.on("blur", function (evt) {
    forecastFinancials['pe'] = evt.target.value;
    RefreshView();
});


loginForm.on('submit', async function (evt) {
    evt.preventDefault();
    const formData = loginForm.serializeArray();
    let loginData = { 'api': true };
    for (let i = 0; i < formData.length; i++) {
        loginData[formData[i].name] = formData[i].value;
    }
    const res = await axios.post('/login', loginData);
    if (res.data.includes('Invalid')) {
        Flash('Invalid credentials', 'danger', 'login-flash-msgs');
    } else {
        UpdateNavBar(true, loginData.username);
        $('#login-modal').modal('hide');
        Flash('Login success', 'success', 'base-flash-msgs');
        $('#save-forecast').attr('data-bs-target', '#save-modal');
    }
});

signupForm.on('submit', async function (evt) {
    evt.preventDefault();
    const formData = loginForm.serializeArray();
    let loginData = { 'api': true };
    for (let i = 0; i < formData.length; i++) {
        loginData[formData[i].name] = formData[i].value;
    }
    const res = await axios.post('/signup', loginData);
    if (res.data.includes('taken')) {
        Flash('Username taken', 'danger', 'signup-flash-msgs');
    } else {
        UpdateNavBar(true, loginData.username);
        $('#signup-modal').modal('hide');
        Flash('Login success', 'success', 'base-flash-msgs');
        $('#save-forecast').attr('data-bs-target', '#save-modal');
    }
});

function UpdateNavBar(logged_in, username) {
    // update the navbar based on login status

    $('#navbar-left').empty();
    if (logged_in) {
        let userNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
        $('<a>').attr('href', `/user/${username}`).attr('class', 'nav-link').text(username).appendTo(userNav);
    } else {
        let loginNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
        $('<a>').attr('href', `/login`).attr('class', 'nav-link').text('Log in').appendTo(loginNav);
        let signupNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
        $('<a>').attr('href', `/signup`).attr('class', 'nav-link').text('Sign up').appendTo(signupNav);
    }
    RefreshView();

}



saveForm.on('submit', async function (evt) {
    evt.preventDefault();
    const formData = saveForm.serializeArray();
    forecastFinancials['ticker'] = ticker;
    for (let i = 0; i < formData.length; i++) {
        forecastFinancials[formData[i].name] = formData[i].value;
    }
    forecastFinancials['avg-growth'] = 0;
    for (let i = 0; i < forecastPeriod; i++) {
        if (i == 0) {
            forecastFinancials['avg-growth'] += forecastFinancials['revenue'][i] / historicFinancials['revenue'][histPeriod - 1] - 1;
        } else {
            forecastFinancials['avg-growth'] += forecastFinancials['revenue'][i] / forecastFinancials['revenue'][i - 1] - 1;
        }
    }
    if (multipleType == 0) {
        forecastFinancials['ps'] = forecastFinancials['pe'];
    } else {
        forecastFinancials['ps'] = -1;
    }
    forecastFinancials['avg-growth'] = forecastFinancials['avg-growth'] / forecastPeriod;
    forecastFinancials['avg-cogs'] = GetAvg(forecastFinancials['cogs'], forecastFinancials['revenue']);
    forecastFinancials['avg-opex'] = GetAvg(forecastFinancials['opex'], forecastFinancials['revenue']);
    forecastFinancials['avg-depreciation'] = GetAvg(forecastFinancials['depreciation'], forecastFinancials['revenue']);
    forecastFinancials['avg-other'] = GetAvg(forecastFinancials['other'], forecastFinancials['revenue']);
    forecastFinancials['avg-tax'] = GetAvg(forecastFinancials['tax'], forecastFinancials['revenue']);
    forecastFinancials['avg-dividend'] = GetAvg(forecastFinancials['dividend'], []);
    forecastFinancials['shares_out'] = finInfo['shares_out'];
    const res = axios.post('/api/forecasts/save', forecastFinancials);
    Flash('Successfully saved', 'success', 'base-flash-msgs');
    $('#save-modal').modal('hide');
});

function Flash(msg, type, targetID) {
    // this function create flask flash messages from js

    $('.flash-msgs').remove();
    let flashMsg = $("<div>");
    flashMsg.appendTo($(`#${targetID}`));
    flashMsg.attr('class', `alert alert-${type} flash-msgs`);
    flashMsg.text(`${msg}`);
}

function UpdateFinancials(evt) {
    // get the values from input fields, and store them in the forecastFinancial dictionary
    // The amount will beb ased on the input type (e.g. dollar amount or percentage)

    const input = StripNum(evt.target.value);
    const period = evt.target.id.charAt(evt.target.id.length - 1);
    const category = evt.target.id.slice(0, evt.target.id.length - 1);
    let amt = 0;
    if (viewType == 0) {
        amt = input * 1000000
    } else if (viewType == 1) {
        let growthPerc = input / 100;
        if (period == 0) {
            amt = (1 + growthPerc) * historicFinancials[category][histPeriod - 1];
        } else {
            amt = (1 + growthPerc) * forecastFinancials[category][period - 1];
        }
    } else {
        let revenuePerc = input / 100;
        amt = revenuePerc * forecastFinancials['revenue'][period];
    }
    forecastFinancials[category][period] = amt;
    RefreshView();
}



function RefreshView() {
    const histFields = $('.hist');
    const forecastFields = $('.table-input, .calc');
    CalculateFinancials();
    if (viewType == 0) {

        // Historic columns
        for (let field of histFields) {
            const id = field.id;
            const period = id.charAt(id.length - 1);

            // history field ids start with hist-, therefore start from index 5 to get category from id
            const category = id.slice(5, id.length - 1);
            const amt = historicFinancials[category][period];
            field.innerText = `${FormatNumber(amt, 1000000, 2, 0)}`;
        }

        // Forecast columns
        for (let field of forecastFields) {
            const id = field.id;
            const period = id.charAt(id.length - 1);
            const category = id.slice(0, id.length - 1);
            const amt = forecastFinancials[category][period];
            field.innerText = `${FormatNumber(amt, 1000000, 2, 0)}`;
            field.value = `${FormatNumber(amt, 1000000, 2, 0)}`;
        }
    } else if (viewType == 1) {
        for (let field of histFields) {
            const id = field.id;
            const period = id.charAt(id.length - 1);
            // history field ids start with hist-, therefore start from index 5 to get category from id
            const category = id.slice(5, id.length - 1);
            let amt = 0;
            if (period != 0) {
                const prevPeriod = historicFinancials[category][period - 1];
                const curPeriod = historicFinancials[category][period];
                amt = curPeriod / prevPeriod - 1;
                field.innerText = `${FormatNumber(amt, 0.01, 2, 1)}`;
            } else {
                field.innerText = 'N/A';
            }
        }
        for (let field of forecastFields) {
            const id = field.id;
            const period = id.charAt(id.length - 1);
            const category = id.slice(0, id.length - 1);
            let amt = 0;
            if (period != 0) {
                const prevPeriod = forecastFinancials[category][period - 1];
                const curPeriod = forecastFinancials[category][period];
                amt = curPeriod / prevPeriod - 1;
                field.innerText = `${FormatNumber(amt, 0.01, 2, 1)}`;
                field.value = `${FormatNumber(amt, 0.01, 2, 1)}`;
            } else {
                const prevPeriod = historicFinancials[category][histPeriod - 1];
                const curPeriod = forecastFinancials[category][period];
                amt = curPeriod / prevPeriod - 1;
                field.innerText = `${FormatNumber(amt, 0.01, 2, 1)}`;
                field.value = `${FormatNumber(amt, 0.01, 2, 1)}`;
            }
        }
    } else {
        for (let field of histFields) {
            const id = field.id;
            const period = id.charAt(id.length - 1);
            // history field ids start with hist-, therefore start from index 5 to get category from id
            const category = id.slice(5, id.length - 1);
            const revenue = historicFinancials['revenue'][period];
            let amt = historicFinancials[category][period] / revenue;
            field.innerText = `${FormatNumber(amt, 0.01, 2, 1)}`;
        }
        for (let field of forecastFields) {
            const id = field.id;
            const period = id.charAt(id.length - 1);
            const category = id.slice(0, id.length - 1);
            const revenue = forecastFinancials['revenue'][period];
            let amt = forecastFinancials[category][period] / revenue;

            field.innerText = `${FormatNumber(amt, 0.01, 2, 1)}`;
            field.value = `${FormatNumber(amt, 0.01, 2, 1)}`;

        }
    }
    peInput.val(`${FormatNumber(forecastFinancials['pe'], 1, 2, 2)}`);
    $('#eps3').text(`${FormatNumber(forecastFinancials['eps'][forecastPeriod - 1], 1, 2, 0)}`);
    $('#price').text(`${FormatNumber(forecastFinancials['price'], 1, 2, 0)}`);
    $('#return').text(`${FormatNumber(forecastFinancials['return'], 0.01, 2, 1)}`);
    $('#divtot').text(`${FormatNumber(forecastFinancials['divtot'], 1, 2, 0)}`);
    $('#target').text(`${FormatNumber(forecastFinancials['target'], 1, 2, 0)}`);
}

function CalculateFinancials() {
    // this function calculates all the subtotal fields (e.g. EBITDA)
    // and store them in dictionaries
    
    for (let i = 0; i < histPeriod; i++) {
        historicFinancials['gross-income'][i] = historicFinancials['revenue'][i] - historicFinancials['cogs'][i];
        historicFinancials['ebitda'][i] = historicFinancials['gross-income'][i] - historicFinancials['opex'][i];
        historicFinancials['operating-income'][i] = historicFinancials['ebitda'][i] - historicFinancials['depreciation'][i];
        historicFinancials['ebt'][i] = historicFinancials['operating-income'][i] + historicFinancials['other'][i];
        historicFinancials['net-income'][i] = historicFinancials['ebt'][i] - historicFinancials['tax'][i];
        historicFinancials['eps'][i] = historicFinancials['net-income'][i] / finInfo['shares_out'][i];
    }
    forecastFinancials['divtot'] = 0;
    for (let i = 0; i < forecastPeriod; i++) {
        forecastFinancials['gross-income'][i] = forecastFinancials['revenue'][i] - forecastFinancials['cogs'][i];
        forecastFinancials['ebitda'][i] = forecastFinancials['gross-income'][i] - forecastFinancials['opex'][i];
        forecastFinancials['operating-income'][i] = forecastFinancials['ebitda'][i] - forecastFinancials['depreciation'][i];
        forecastFinancials['ebt'][i] = forecastFinancials['operating-income'][i] + forecastFinancials['other'][i];
        forecastFinancials['net-income'][i] = forecastFinancials['ebt'][i] - forecastFinancials['tax'][i];
        forecastFinancials['eps'][i] = forecastFinancials['net-income'][i] / finInfo['shares_out'];
        forecastFinancials['divtot'] += forecastFinancials['dividend'][i];
    }
    if (multipleType == 0) {
        forecastFinancials['price'] = forecastFinancials['pe'] * forecastFinancials['eps'][forecastFinancials['eps'].length - 1];
    } else {
        forecastFinancials['price'] = forecastFinancials['pe'] * (forecastFinancials['revenue'][forecastFinancials['revenue'].length - 1] / (finInfo['shares_out']));
    }
    forecastFinancials['divtot'] = forecastFinancials['divtot'] / (finInfo['shares_out']);
    forecastFinancials['target'] = forecastFinancials['divtot'] + forecastFinancials['price'];
    forecastFinancials['return'] = (forecastFinancials['target'] / priceInfo['cur_price']) ** (1 / forecastPeriod) - 1;
}

async function Init() {
    const res = await axios.get(`/api/stocks/${ticker}`);
    finInfo = res.data.stock;
    priceInfo = res.data.price;
    historicFinancials = res.data.stock.financials;
    histPeriod = historicFinancials['revenue'].length;
    historicFinancials['gross-income'] = [];
    historicFinancials['ebitda'] = [];
    historicFinancials['operating-income'] = [];
    historicFinancials['ebt'] = [];
    historicFinancials['net-income'] = [];
    historicFinancials['eps'] = [];
    for (let i = 0; i < histPeriod; i++) {
        historicFinancials['gross-income'].push(0);
        historicFinancials['ebitda'].push(0);
        historicFinancials['operating-income'].push(0);
        historicFinancials['ebt'].push(0);
        historicFinancials['net-income'].push(0);
        historicFinancials['eps'].push(0);
    }
    const query = $('#query-data');
    if (query.attr('data-user') != 'None') {
        $('#save-forecast').attr('data-bs-target', '#save-modal');
    }
    const rates = {
        'revenue': finInfo['avg_growth'],
        'cogs': GetAvg(historicFinancials['cogs'], historicFinancials['revenue']),
        'opex': GetAvg(historicFinancials['opex'], historicFinancials['revenue']),
        'depreciation': GetAvg(historicFinancials['depreciation'], historicFinancials['revenue']),
        'other': GetAvg(historicFinancials['other'], historicFinancials['revenue']),
        'tax': GetAvg(historicFinancials['tax'], historicFinancials['revenue']),
        'dividend': 1
    }
    for (let i = 0; i < forecastPeriod; i++) {
        for (let key of Object.keys(rates)) {
            if (key == 'revenue') {
                if (i > 0) {
                    forecastFinancials['revenue'][i] = forecastFinancials['revenue'][i - 1] * (1 + rates['revenue']);
                } else {
                    forecastFinancials['revenue'][0] = historicFinancials['revenue'][histPeriod - 1] * (1 + rates['revenue']);
                }

            } else if (key == 'dividend') {
                forecastFinancials['dividend'][i] = historicFinancials['dividend'][histPeriod - 1];
            } else {
                forecastFinancials[key][i] = forecastFinancials['revenue'][i] * rates[key];
            }
        }
        forecastFinancials['period'][i] = historicFinancials['period'][histPeriod - 1] + i + 1;
    }

    if (typeof (finInfo['pe_ratio']) == 'number') {
        forecastFinancials['pe'] = finInfo['pe_ratio'];
        multipleType = 0;
    } else {
        forecastFinancials['pe'] = finInfo['ps_ratio'];
        multipleType = 1;
    }
    RefreshView();
}

function GetAvg(nums, rev) {
    // calculate the average growth rate given a list of nums
    // calculate the average percentage of revenue if rev is given

    let sum = 0.0;
    if (rev.length > 0) {
        for (let i = 0; i < nums.length; i++) {
            sum += nums[i] / rev[i];
        }
        return sum / nums.length;
    } else {
        for (let i = 1; i < nums.length; i++) {
            sum += nums[i] / nums[i - 1];
        }
        return sum / (nums.length - 1);
    }

}

function FormatNumber(num, div = 1000000, dec = 2, type) {
    // Return a string representation of num, rounded by round, with
    // dec decimal places.
    // if type is 0, present the item as $ amount (e.g. $1,234.56)
    // if type is 1, present the item as % amount (e.g. 11.23%)
    // if type is 2, present the item with no symbols attached (e.g. 11.23)

    let dividedNum = num / div; //rounding the number by round
    dividedNum = (Math.round(dividedNum * 100) / 100).toFixed(dec); // showing dec decimal points
    if (type == 1) {
        return (String(dividedNum) + '%');
    } else if (type == 0) {
        let dollarUSLocale = Intl.NumberFormat('en-US');
        return '$' + dollarUSLocale.format(dividedNum);
    } else {
        return String(dividedNum);
    }
}

function StripNum(str) {
    // get num in string format, return a number with all non-numeric characters
    // removed

    let new_str = '';
    for (let char of str) {
        if (!isNaN(char) || char == '.' || char == '-') {
            new_str = new_str + char;
        }
    }
    return Number(new_str);
}

Init();