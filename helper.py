import numbers


def format_num(num):
    """Get a number, format it to 2 decimal points and return it.

        if not a number, return "N/A" instead


    """

    # if num is a number, append or prepend the symbol and
    # return the string
    if isinstance(num, numbers.Number):
        num_rep = "{:0,.2f}".format(num)
        return num_rep
    # if num is not a number, return N/A
    else:
        return 'N/A'