import numpy as np
import json

# Add table position information to data.json

data = json.load(open("data.json"))
row_len = [2, 8, 8, 18, 18, 32, 32]
row_bounds = [sum(row_len[:i+1]) for i in range(len(row_len))]

for i in range(len(data)):
    # Which row?
    for row_i, b in enumerate(row_bounds):
        if i < b:
            break
    # What's its position?
    col_i = i - row_bounds[row_i]+row_len[row_i]
    # Now the effective position...
    if row_i > 4 and (17 > col_i > 2):
        data[i]['rowI'] = row_i-5
        data[i]['subTable'] = 'LantAct'
        data[i]['colI'] = col_i - 3
    else:
        data[i]['rowI'] = row_i
        data[i]['subTable'] = 'Main'
        if row_i == 0:
            data[i]['colI'] = 0 if col_i == 0 else 17
        elif row_i in (1,2):
            data[i]['colI'] = col_i if col_i < 2 else col_i+10
        elif row_i in (3,4):
            data[i]['colI'] = col_i
        else:
            data[i]['colI'] = col_i if col_i < 3 else col_i-14
    # Also fix the color
    if type(data[i]['cpkHexColor']) not in (str, unicode):
        if type(data[i]['cpkHexColor']) is int:
            data[i]['cpkHexColor'] = "{0:06d}".format(data[i]['cpkHexColor'])
    elif data[i]['cpkHexColor'] == "":
        data[i]['cpkHexColor'] = "dddddd"
    # Also fix the name
    data[i]['name'] = data[i]['name'].split()[0]


# Now save again
json.dump(data, open("data_tabulated.json", 'w'), indent=0)




