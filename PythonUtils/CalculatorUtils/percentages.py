__author__ = 'dstrohl'



def generatePercentages(data_array, row_fieldname, data_fieldname, newfieldname=""):
    '''
    assumes data_array will be in the format of:
    [
    { 'row_fieldname' : [{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3},{field1:data1, field2,data2, field3:data3}]}

    ]
    if no newfieldname, fieldname is replaced with percentages
    if fieldnames are numeric, a set is assumed instead of a dict
    if new_fieldname is numeric, the data will be inserted at that position (zero based).

    '''

    for col in range(len(data_array[1][row_fieldname])):

        col_total = 0
        print('new col')
        for row in range(len(data_array)):
            rec = data_array[row][row_fieldname][col]
            # print( rec )
            col_total = col_total + rec[data_fieldname]
            print(col_total)

        for row in range(len(data_array)):
            rec = data_array[row][row_fieldname][col][data_fieldname]
            try:
                rec_perc = rec / col_total
            except ZeroDivisionError:
                rec_perc = 0

            if newfieldname:
                data_array[row][row_fieldname][col][newfieldname] = rec_perc
            else:
                data_array[row][row_fieldname][col][data_fieldname] = rec_perc


                # print( rec_perc )

    print(data_array)

    return data_array

