"""Made for converting the RESULTS.dat file into a .csv file for better importing into Excel. Is specific to the
parameters used for the WLM model, but changes are easy enough. """

import re

with open('RESULT.DAT', 'r') as results:
    alldata = [line.strip() for line in results]

sepdata = []
names = []

for i, line in enumerate(alldata):
    if line.startswith('FINAL'):
        # Change the indexes here to select the region of interest of the parameters
        sepdata.append(alldata[i+4:i+17])
        names.append(alldata[i-2][:14])
        # Truncates the filename to 14. Sometimes a bunch of x00 appears in the file without this

par_val_err = []

# columns = ['scale', 'd_head', 'rad_core','rho_rel', 'sigma', 'bck', 'l_cont', 'b_kuhn', 'eps_xs', 'd_cq', 'nu_rpa', 'sc_pow', 'exp']
columns_err = ['scale', 'err', 'd_head', 'err','rad_core','err','rho_rel', 'err', 'sigma','err', 'bck', 'err',
               'l_cont','err', 'b_kuhn', 'err', 'eps_xs','err', 'd_cq','err', 'nu_rpa','err', 'sc_pow', 'err',
               'exp','err']

columns_err_joined = ";".join(columns_err)

for data in sepdata:
    temp_join = []
    for i, line in enumerate(data):
        Int, beg, end, err, name = re.split('\s+', line)
        temp_join.append(end)
        temp_join.append(err)
    par_val_err.append(temp_join)

lines_to_write = []
lines_to_write.append('name;' + columns_err_joined + '\n')
for name, group in zip(names, par_val_err):
    string = name.rstrip() + ";" + ";".join(group) + '\n'
    # string = name[0:12] + ";".join(group)
    lines_to_write.append(string)

with open('results.csv', 'w') as fhand:
    for line in lines_to_write:
        fhand.write(line)