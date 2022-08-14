import collections
import csv


# add comment
def main():
    table = collections.OrderedDict()

    file_name = "fixed_rates.csv"
    print("# reading %s" % (file_name))
    with open(file_name) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter="\t")
        for row in csv_reader:
            values = []
            for value in row.values():
                values.append(value)
            key = values[0]
            table[key] = values
            # print("fixed_rate - %s" % (values))

    file_name = "inflation_rates.csv"
    print("# reading %s" % (file_name))
    with open(file_name) as csv_file:
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

    file_name = "ibond_rates.csv"
    print("# writing %s" % (file_name))
    col_names = ["date", "fixed_rate", "inflation_rate"]
    with open(file_name, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(col_names)
        for rates in table.values():
            csv_writer.writerow(rates)


if __name__ == "__main__":
    main()
