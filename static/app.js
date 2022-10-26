let viewType = 0; // 0 is dollar amount, 1 is percent growth, 2 is percentage of revenue
let forecastPeriod = 4; // default to 4 forecast periods
let histPeriod = 4; // default to 4 historic periods
let ticker = $('#stock-ticker').text();

const saveForm = $('#save-form');

const loginForm = $('#login-form');

const switchToLogin = $('#switch-to-login');
const switchToSignup = $('#switch-to-signup');

switchToLogin.on('click', ShowLogin);
switchToSignup.on('click', ShowSignup);

function ShowSignup(evt) {
    evt.preventDefault();
    $('#form-title').text('Sign up')
    $('#login').hide();
    $('#signup').show();
}

function ShowLogin(evt) {
    evt.preventDefault();
    $('#form-title').text('Log in')
    $('#login').show();
    $('#signup').hide();
}

loginForm.on('submit', async function(evt) {
    evt.preventDefault();
    const formData = loginForm.serializeArray();
    let loginData = {'api': true};
    let res = {};
    for (let i = 0; i < formData.length; i++) {
        loginData[formData[i].name] = formData[i].value;
    }
    if ($('#login').is(":visible")) {
        res = await axios.post('/login', loginData);
    } else {
        res = await axios.post('/signup', loginData);
    }
    if (res.data.includes('Invalid')) {
        Flash('Invalid credentials', 'danger', 'form-flash-msgs');
    } else if (res.data.includes('taken')) {
        Flash('Username taken', 'danger', 'form-flash-msgs');
    } else {
        UpdateNavBar(true, loginData.username);
        loginForm.hide();
        saveForm.show();
        Flash('Login success', 'success', 'form-flash-msgs');
    }
});

function UpdateNavBar(logged_in, username) {
    // update the navbar based on login status

    $('#navbar-left').empty();
    let homeNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
    $('<a>').attr('href', '/').attr('class', 'nav-link').text('Home').appendTo(homeNav);
    if (logged_in) {
        let userNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
        $('<a>').attr('href', `/user/${username}`).attr('class', 'nav-link').text(username).appendTo(userNav);
    } else {
        let loginNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
        $('<a>').attr('href', `/login`).attr('class', 'nav-link').text('Log in').appendTo(userNav);
        let signupNav = $('<li>').attr('class', 'nav-item').appendTo($('#navbar-left'));
        $('<a>').attr('href', `/signup`).attr('class', 'nav-link').text('Sign up').appendTo(userNav);
    }
    
}



saveForm.on('submit', async function(evt) {
    evt.preventDefault();
    const formData = saveForm.serializeArray();
    forecastFinancials['ticker'] = ticker;
    for (let i = 0; i < formData.length; i++) {
        forecastFinancials[formData[i].name] = formData[i].value;
    }
    console.log(forecastFinancials);
    const res = axios.post('/api/forecasts/save', forecastFinancials);
    console.log(res);
    Flash('Successfully saved', 'success', 'flash-messages');
    $('#save-forecast').modal('hide');
});

function Flash(msg, type, targetID) {
    // this function create flask flash messages from js

    $('.flash-msgs').remove();
    let flashMsg = $("<div>");
    flashMsg.appendTo($(`#${targetID}`));
    flashMsg.attr('class', `alert alert-${type} flash-msgs`);
    flashMsg.text(`${msg}`);
}





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
    'period':[0, 0, 0, 0],
    'pe': 20,
    'price': 0,
    'return': 0.0,
};
let finInfo = {}; // used to store stock financial data
let priceInfo = {}; // user to store historic prices

let historicFinancials = {};

const forecastTable = $('#forecast-table');
forecastTable.on("blur", ".table-input", UpdateFinancials);

const viewToggle = $('#view-toggle');
viewToggle.on('change', 'input', function (evt) {
    viewType = evt.target.value;
    console.log(viewType);
    RefreshView();
});

const peInput = $('#pe');
peInput.on("blur", function (evt) {
    forecastFinancials['pe'] = evt.target.value;
    RefreshView();
});

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
        console.log(`${input} / 100 = ${revenuePerc}, ${forecastFinancials['revenue'][period]}`);
        amt = revenuePerc * forecastFinancials['revenue'][period];
    }
    forecastFinancials[category][period] = amt;
    RefreshView();
}


function RefreshView() {
    const histFields = $('.hist');
    const forecastFields = $('.table-input, .calc');
    const valFields = $('.val');
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
            if (category == 'cogs') {
                console.log(`${category}: ${forecastFinancials[category][period]} / ${revenue} = ${amt}`);
            }

            field.innerText = `${FormatNumber(amt, 0.01, 2, 1)}`;
            field.value = `${FormatNumber(amt, 0.01, 2, 1)}`;

        }
    }
    peInput.val(`${FormatNumber(forecastFinancials['pe'], 1, 2, 2)}`);
    $('#eps3').text(`${FormatNumber(forecastFinancials['eps'][forecastPeriod - 1], 1, 2, 0)}`);
    $('#price').text(`${FormatNumber(forecastFinancials['price'], 1, 2, 0)}`);
    $('#return').text(`${FormatNumber(forecastFinancials['return'], 0.01, 2, 1)}`)
}

function CalculateFinancials() {
    // this function calculates all the subtotal fields (e.g. EBITDA)
    // and store them in dictionaries

    for (let i = 0; i < histPeriod; i++) {
        historicFinancials['gross-income'][i] = historicFinancials['revenue'][i] - historicFinancials['cogs'][i];
        historicFinancials['ebitda'][i] = historicFinancials['gross-income'][i] - historicFinancials['opex'][i];
        historicFinancials['operating-income'][i] = historicFinancials['ebitda'][i] - historicFinancials['depreciation'][i];
        historicFinancials['ebt'][i] = historicFinancials['operating-income'][i] - historicFinancials['other'][i];
        historicFinancials['net-income'][i] = historicFinancials['ebt'][i] - historicFinancials['tax'][i];
        historicFinancials['eps'][i] = historicFinancials['net-income'][i] / finInfo['shares_out'][i];
    }
    for (let i = 0; i < forecastPeriod; i++) {
        forecastFinancials['gross-income'][i] = forecastFinancials['revenue'][i] - forecastFinancials['cogs'][i];
        forecastFinancials['ebitda'][i] = forecastFinancials['gross-income'][i] - forecastFinancials['opex'][i];
        forecastFinancials['operating-income'][i] = forecastFinancials['ebitda'][i] - forecastFinancials['depreciation'][i];
        forecastFinancials['ebt'][i] = forecastFinancials['operating-income'][i] - forecastFinancials['other'][i];
        forecastFinancials['net-income'][i] = forecastFinancials['ebt'][i] - forecastFinancials['tax'][i];
        forecastFinancials['eps'][i] = forecastFinancials['net-income'][i] / finInfo['shares_out'];
    }
    forecastFinancials['price'] = forecastFinancials['pe'] * forecastFinancials['eps'][forecastFinancials['eps'].length - 1];
    forecastFinancials['return'] = (forecastFinancials['price'] / priceInfo['hist_30d_prices'][priceInfo['hist_30d_prices'].length - 1]) ** (1 / forecastFinancials['eps'].length) - 1;

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
    console.log(`hey, ${query.attr('data-user')}`);
    if (query.attr('data-user') == 'None') {
        loginForm.show();
        $('#signup').hide();
        saveForm.hide();
        $('#form-title').text('Log in');
    } else {
        loginForm.hide();
        saveForm.show();
        $('#form-title').text('Save Forecast');
    }
    const rates = {
        'revenue': Number(query.attr('data-growth')) / 100,
        'cogs': (1 - Number(query.attr('data-margin') / 100)),
        'opex': GetAvg(historicFinancials['opex'], historicFinancials['revenue']),
        'depreciation': GetAvg(historicFinancials['depreciation'], historicFinancials['revenue']),
        'other': GetAvg(historicFinancials['other'], historicFinancials['revenue']),
        'tax': GetAvg(historicFinancials['tax'], historicFinancials['revenue'])
    }
    for (let i = 0; i < forecastPeriod; i++) {
        for (let key of Object.keys(rates)) {
            if (key != 'revenue') {
                forecastFinancials[key][i] = forecastFinancials['revenue'][i] * rates[key];
            } else {
                if (i > 0) {
                    forecastFinancials['revenue'][i] = forecastFinancials['revenue'][i - 1] * (1 + rates['revenue']);
                } else {
                    forecastFinancials['revenue'][0] = historicFinancials['revenue'][histPeriod - 1] * (1 + rates['revenue']);
                }
            }
        }
        forecastFinancials['period'][i] = historicFinancials['period'][histPeriod - 1] + i + 1;
    }
    forecastFinancials['pe'] = Number(query.attr('data-pe'));
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
            sum += nums[i] / nums[i - 1] - 1;
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
        if (!isNaN(char) || char == '.') {
            new_str = new_str + char;
        }
    }
    return Number(new_str);
}

Init();