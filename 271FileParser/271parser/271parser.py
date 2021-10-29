import os
import csv
import time

__OUTFILE_PREFIX = "Parsed271Results"
__OUTFILE_HEADERS = ['FILENAME', 'LASTNAME', 'FIRSTNAME', 'MIDINITIAL',
                     'SUBSCRIBERID', 'INSTYPECODE']
__DEFAULT_FILE_PATTERN = "*271*"


def write_to_csv(*args):
    """Appends input args to outfile."""
    with open(__outfile_path, newline='', mode='a') as outcsv:
        csv_writer = csv.writer(outcsv, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data = []
        for x in args:
            data.append(x)
        csv_writer.writerow(data)


def parse_271(full_file_path, filename):
    with open(full_file_path, 'r') as file:
        file_data = file.readlines()
        num_lines_in_file = len(file_data)
        if num_lines_in_file == 1:
            file_content = file_data[0].split(sep="\n")
        else:
            file_content = file_data
        for line in file_content:
            lname, fname, midin, subid, plantype = "", "", "", "", ""
            idxA1 = ("EB", line.find("EB*R**30*"))
            idxB1 = ("SUB", line.find("NM1*IL*1*"))
            indexes = sorted([idxA1, idxB1])
            for start_index in indexes:
                idx_white_space = line[start_index[1]:].find(" ")
                data = line[start_index[1]:start_index[1] + idx_white_space]
                if start_index[0] == "SUB":
                    lname = data.split('*')[3]
                    fname = data.split('*')[4]
                    midin = data.split('*')[7]
                    subid = data.split('*')[9]
                elif start_index[0] == "EB":
                    plantype = data.split('*')[4]
            parsed_line = [filename, lname, fname, midin, subid, plantype]
            # print(parsed_line)
            write_to_csv(*parsed_line)


def process_271s(file_pattern, source_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_pattern) or (file_pattern in file):
                print(f'Reading file: {file}')
                full_file_path = os.path.abspath(os.path.join(source_dir, file))
                parse_271(full_file_path, file)


def begin_processing(source_dir):
    with open(__outfile_path, newline='', mode='a') as outcsv:
        csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        if not __file_exists:
            csv_writer.writerow(__OUTFILE_HEADERS)
    print('Beginning processing...')
    print(f'Parsing with file pattern: {__file_pattern}')
    process_271s(__file_pattern, source_dir)
    print(f'\nCompleted stripping 835s in: {source_dir}')
    print(f'Results saved to: {__outfile_path}')


if __name__ == '__main__':
    timestr = time.strftime("%Y.%m.%d-%H%M%S")
    __outfile_name = __OUTFILE_PREFIX + " " + timestr + ".csv"
    __file_pattern = ".txt"  # __DEFAULT_FILE_PATTERN
    __source_dir = os.path.dirname(os.path.abspath(__file__))
    __outfile_path = __outfile_name  # os.path.join(__source_dir, __outfile_name)
    __traverse_subdir = False
    __file_exists = os.path.isfile(__outfile_name)
    begin_processing(__source_dir)
