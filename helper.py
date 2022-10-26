import numbers


def format_num(num, symbol='$', front=True):
    """Get a number, return a string representation based on a format

        symbol is the symbol to be added to the string

        if front is True, symbol will be prepended
        otherwise, format will be appended

        if not a number, return "N/A" instead


    """

    # if num is a number, append or prepend the symbol and
    # return the string
    if isinstance(num, numbers.Number):
        num_rep = "{:0,.2f}".format(num)
        if front == True:
            return symbol + num_rep
        else:
            return num_rep + symbol
    # if num is not a number, return N/A
    else:
        return 'N/A'
