import csv

def write_dicts(file, lines):
    lines_iter = iter(lines)
    first_line = next(lines_iter)
    writer = csv.DictWriter(file, first_line.keys())
    writer.writeheader()
    writer.writerow(first_line)
    for line in lines_iter:
        writer.writerow(line)
