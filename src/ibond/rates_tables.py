import collections
import csv
# add comment
from pathlib import Path

import ibond.ibond_rates

INFLATION_RATES_FILE_NAME = "inflation_rates.csv"

FIXED_RATES_FILE_NAME = "fixed_rates.csv"


def main():
    table = collections.OrderedDict()

    file_name = FIXED_RATES_FILE_NAME
    p = Path(__file__).with_name(file_name)
    print("# reading %s" % (p.absolute()))
    with p.open('r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter="\t")
        for row in csv_reader:
            values = []
            for value in row.values():
                values.append(value)
            key = values[0]
            table[key] = values
            # print("fixed_rate - %s" % (values))

    file_name = INFLATION_RATES_FILE_NAME
    p = Path(__file__).with_name(file_name)
    print("# reading %s" % (p.absolute()))
    with p.open('r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter="\t")
        for row in csv_reader:
            values = []
            for value in row.values():
                values.append(value)
            key = values[0]
            inflation_rate = values[1]
            # print("inflation_rate - %s" % (values))
            if key in table:
                values = table[key]
                # print("FOUND fixed_rate - %s" % (values))
                values.append(inflation_rate)
                # print("ADDED inflation_rate - %s" % (values))
            else:
                print("WARN: cannot find key=%s" % (key))

    file_name = ibond.ibond_rates.IBOND_RATES_FILE_NAME
    p = Path(__file__).with_name(file_name)
    print("# writing %s" % (p.absolute()))
    col_names = ["date", "fixed_rate", "inflation_rate"]
    with p.open('w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(col_names)
        for rates in table.values():
            csv_writer.writerow(rates)


if __name__ == "__main__":
    main()
