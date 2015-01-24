__author__ = 'dstrohl'


def quarter_calc(*args):
    arg = []
    for a in args:
        arg.append(int(a))

    if len(args) == 1:
        response_item = {}
        if arg[0] % 1 == 0:
            qtr = arg[0] % 4
            yr = 2000 + ( ( arg[0] - qtr ) / 4 )
            qtr = qtr + 1
            response_item['year'] = yr
            response_item['quarter'] = qtr
            response_item['word'] = '{year}-Q{quarter}'.format(**response_item)

        return response_item


    elif ( len(args) ) == 2:
        response_item = 0
        if arg[0] > 4:
            yr = arg[0]
            qt = arg[1]
        else:
            yr = arg[1]
            qt = arg[0]

        return ( ( yr - 2000 ) * 4 ) + ( qt - 1 )

    return ""

