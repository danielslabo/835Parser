# Note this non-GUI version is deprecated
import csv
import os
import re
import time

timestr = time.strftime("%Y.%m.%d-%H%M%S")
outfile_name = "Parsed835Goodies" + " " + timestr + ".csv"
outfile_headers = ['FILENAME', 'TRN02', 'TRN03',
                   'PAYER', 'PAYEE', 'NPI', 'CLAIM', 'CLP02']
file_pattern = ".835"

source_dir = os.path.dirname(os.path.abspath(__file__))
file_exists = os.path.isfile(outfile_name)


def write_to_csv(*args):
    with open(outfile_name, newline='', mode='a') as outcsv:
        csv_writer = csv.writer(
            outcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data = []
        for x in args:
            data.append(x)
        csv_writer.writerow(data)


# Write out Headers if output file is being newly created in current directory
with open(outfile_name, newline='', mode='a') as outcsv:
    csv_writer = csv.writer(
        outcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    if not file_exists:
        csv_writer.writerow(outfile_headers)

# Iterate through each '835' file in current directory and parse out desired
# values. Consider if file is split across lines (standard) or all in 1 line
# (uncommon). Write desired values out as each CLP segment is found.
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith(file_pattern) or (file_pattern in file):
            print(f'Reading file: {file}')
            file_trn02 = file_trn03 = file_payer = file_payee = file_npi = ""
            num_lines_in_file = len(open(file).readlines())
            if num_lines_in_file == 1:
                for line in open(file, 'r'):
                    one_line_data = line.split(sep="~")
                    for i in range(len(one_line_data)):
                        if one_line_data[i].startswith("TRN"):
                            file_trn02 = re.sub('~', '', one_line_data[i].split('*')[2])           # TRN;02
                            file_trn03 = re.sub('~', '', one_line_data[i].split('*')[3])           # TRN;03
                        if one_line_data[i].startswith("N1*PR"):
                            file_payer = re.sub('~', '', one_line_data[i].split('*')[2]).rstrip()  # N1;02
                        if one_line_data[i].startswith("N1*PE"):
                            file_payee = re.sub('~', '', one_line_data[i].split('*')[2]).rstrip()  # N1;02
                            file_npi = re.sub('~', '', one_line_data[i].split('*')[4])             # N1;04
                        if one_line_data[i].startswith("CLP"):
                            claim = re.sub('~', '', one_line_data[i].split('*')[1])                # CLP;01
                            clp02 = re.sub('~', '', one_line_data[i].split('*')[2])                # CLP;02
                            write_to_csv(
                                file, file_trn02, file_trn03, file_payer, 
                                file_payee, file_npi, claim, clp02)
            else:
                for line in open(file, 'r'):
                    if line.startswith("TRN"):
                        file_trn02 = re.sub('~', '', line.split('*')[2])           # TRN;02
                        file_trn03 = re.sub('~', '', line.split('*')[3])           # TRN;03
                    if line.startswith("N1*PR"):
                        file_payer = re.sub('~', '', line.split('*')[2]).rstrip()  # N1;02
                    if line.startswith("N1*PE"):
                        file_payee = re.sub('~', '', line.split('*')[2]).rstrip()  # N1;02
                        file_npi = re.sub('~', '', line.split('*')[4])             # N1;04
                    if line.startswith("CLP"):
                        claim = re.sub('~', '', line.split('*')[1])                # CLP;01
                        clp02 = re.sub('~', '', line.split('*')[2])                # CLP;02
                        write_to_csv(
                            file, file_trn02, file_trn03, file_payer, 
                            file_payee, file_npi, claim, clp02)
print(f"Completed stripping 835s in: {source_dir} to {outfile_name}\n")
