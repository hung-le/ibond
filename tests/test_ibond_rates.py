import csv
import math

import datetime
import unittest
from stringprep import in_table_c11_c12

import dateutil.parser

from ibond import ibond_rates

COL_INFLATION_RATE = 2

COL_FIXED_RATE = 1

COL_DATE = 0


class Testing(unittest.TestCase):

    def test_create(self):
        # rates_filename = "ibond_rates.csv"
        # rates_date_format = "%B %d, %Y"
        rates_table = ibond_rates.IBondRates()

        expected_values = []
        # Sep 1 1998,3.40%,0.62%,
        expected_values.append((datetime.datetime(1998, 9, 1), 3.4, 0.62))
        # May 1 2010,0.20%,0.77%,
        expected_values.append((datetime.datetime(2010, 5, 1), 0.20, 0.77))
        # May 1 2015,0.00%,-0.80%,
        expected_values.append((datetime.datetime(2015, 5, 1), 0.00, -0.80))
        # May 1 2022,0.00%,4.81%,
        expected_values.append((datetime.datetime(2022, 5, 1), 0.00, 4.81))

        for row in expected_values:
            fixed_rate = rates_table.get_fixed_rate(row[COL_DATE])
            self.assertEqual(fixed_rate, row[COL_FIXED_RATE])

            inflation_rate = rates_table.get_inflation_rate(row[COL_DATE])
            self.assertEqual(inflation_rate, row[COL_INFLATION_RATE])


if __name__ == "__main__":
    unittest.main()


def test_get_rates():
    # https://eyebonds.info/ibonds/rates.html
    rates_table = ibond_rates.IBondRates()

    issue_date = datetime.datetime(1998, 9, 1)
    current_date = issue_date
    fixed_rate = rates_table.get_fixed_rate(issue_date)
    inflation_rate = rates_table.get_inflation_rate(current_date)
    composite_rate = rates_table.compute_composite_rate(fixed_rate, inflation_rate)
    # print("%s, %s, %s" % (fixed_rate, inflation_rate, composite_rate))
    assert fixed_rate == 3.4
    assert inflation_rate == 0.62
    assert composite_rate == 4.66

    current_date = datetime.datetime(2009, 5, 1)
    inflation_rate = rates_table.get_inflation_rate(current_date)
    composite_rate = rates_table.compute_composite_rate(fixed_rate, inflation_rate)
    assert fixed_rate == 3.4
    assert inflation_rate == -2.78
    assert composite_rate == 0.00

    current_date = datetime.datetime(2014, 11, 1)
    inflation_rate = rates_table.get_inflation_rate(current_date)
    composite_rate = rates_table.compute_composite_rate(fixed_rate, inflation_rate)
    assert fixed_rate == 3.4
    assert inflation_rate == 0.74
    assert composite_rate == 4.91

    current_date = datetime.datetime(2022, 5, 1)
    inflation_rate = rates_table.get_inflation_rate(current_date)
    composite_rate = rates_table.compute_composite_rate(fixed_rate, inflation_rate)
    assert fixed_rate == 3.4
    assert inflation_rate == 4.81
    assert composite_rate == 13.18

    issue_date = datetime.datetime(1998, 11, 1)
    current_date = issue_date
    fixed_rate = rates_table.get_fixed_rate(issue_date)
    inflation_rate = rates_table.get_inflation_rate(current_date)
    composite_rate = rates_table.compute_composite_rate(fixed_rate, inflation_rate)
    # print("%s, %s, %s" % (fixed_rate, inflation_rate, composite_rate))
    assert fixed_rate == 3.30
    assert inflation_rate == 0.86
    assert composite_rate == 5.05


def test_read_rates_test_data():
    rate_change_dates = []
    inflation_rates = []
    issued_dates = []

    row_number = 0
    header_row = -1
    with open('test_rates_data.csv', 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            row_number = row_number + 1

            # Fixed\n↓ Rates ↓
            if row[0].startswith("Fixed"):
                header_row = row_number
                rate_change_dates = parse_rate_change_dates(row)

                # row_number = row_number + 1
                # print("PARSED rate_change_dates row=%s, rate_change_dates=%s" % (len(row), len(rate_change_dates)))
                continue

            # print(header_row, row_number)
            if (header_row != -1) and (row_number == (header_row + 1)):
                inflation_rates = parse_inflation_rates(row)

                # row_number = row_number + 1
                # print("PARSED inflation_rates row=%s, inflation_rates=%s" % (len(row), len(inflation_rates)))
                continue

            # print(row)
            # 09 1998
            month_year = row[0]
            if len(month_year) <= 0:
                row_number = row_number + 1
                # print("SKIP row=%s" % row)
                # row_number = row_number + 1
                continue

            try:
                issued_date = dateutil.parser.parse("{}-{}-01".format(month_year[3:], month_year[0:2]))
            except ValueError:
                # print("SKIP bad issue_date - row=%s" % row)
                # row_number = row_number + 1
                continue
            # print("my=%s, d=%s" % (month_year, issued_date))

            # 3.40
            try:
                fixed_rate = float(row[1])
            except ValueError:
                fixed_rate = None

            composite_rates = parse_composite_rates(row)
            # print("PARSED composite_rates row=%s, composite_rates=%s" % (len(row), len(composite_rates)))

            # print(composite_rates)
            issued_dates.append((issued_date, fixed_rate, composite_rates))

            # row_number = row_number + 1

    # print(current_dates)
    # print(issued_dates)

    check_rates_test_data(rate_change_dates, inflation_rates, issued_dates)

    check_computed_rates(rate_change_dates, inflation_rates, issued_dates)


def check_computed_rates(rate_change_dates, inflation_rates, issued_dates):
    rates_table = ibond_rates.IBondRates()
    for row in issued_dates:
        issued_date = row[0]
        fixed_rate = row[1]
        composite_rates = row[2]
        assert rates_table.get_fixed_rate(issued_date) == fixed_rate

        for i in range(0, len(composite_rates)):
            current_date = rate_change_dates[i]
            inflation_rate = inflation_rates[i]
            composite_rate = composite_rates[i]

            if inflation_rate is not None:
                assert rates_table.get_inflation_rate(current_date) == inflation_rate
            if composite_rate is not None:
                computed_composite_rate = rates_table.compute_composite_rate(fixed_rate, inflation_rate)
                if computed_composite_rate != composite_rate:
                    print("WARN: composite_rate check not same %s != %s" % (computed_composite_rate, composite_rate))
                assert math.isclose(
                    computed_composite_rate, composite_rate, rel_tol=1e-2)


def check_rates_test_data(rate_change_dates, inflation_rates, issued_dates):
    assert len(rate_change_dates) == len(inflation_rates)
    assert len(rate_change_dates) == 49
    assert len(rate_change_dates) == len(issued_dates)
    assert len(issued_dates) == 49

    column_count = 49
    for row in issued_dates:
        issued_date = row[0]
        fixed_rate = row[1]
        composite_rates = row[2]

        # print(issued_date)
        for i in range(0, len(composite_rates)):
            current_date = rate_change_dates[i]
            inflation_rate = inflation_rates[i]
            composite_rate = composite_rates[i]
            # print("%s %s %s" % (current_date, inflation_rate, composite_rate))
        assert len(composite_rates) == column_count
        # print(len(composite_rates))
        # column_count = column_count - 1

    # 08 1998
    # 3.40
    d = dateutil.parser.parse("1998-09-01")
    for row in issued_dates:
        issued_date = row[0]
        if d == issued_date:
            fixed_rate = row[1]
            assert fixed_rate == 3.4

            # 522
            # 4.81
            # 13.18
            d2 = dateutil.parser.parse("2022-05-01")
            for i in range(0, len(rate_change_dates)):
                if rate_change_dates[i] == d2:
                    inflation_rate = inflation_rates[i]
                    assert inflation_rate == 4.81

                    composite_rates = row[2]
                    composite_rate = composite_rates[i]
                    assert composite_rate == 13.18

            # 509
            # -2.78
            # 0.00
            d2 = dateutil.parser.parse("2009-05-01")
            for i in range(0, len(rate_change_dates)):
                if rate_change_dates[i] == d2:
                    inflation_rate = inflation_rates[i]
                    assert inflation_rate == -2.78

                    composite_rates = row[2]
                    composite_rate = composite_rates[i]
                    assert composite_rate == 0.0

            # 1117
            # 1.24
            # 5.92
            d2 = dateutil.parser.parse("2017-11-01")
            for i in range(0, len(rate_change_dates)):
                if rate_change_dates[i] == d2:
                    inflation_rate = inflation_rates[i]
                    assert inflation_rate == 1.24

                    composite_rates = row[2]
                    composite_rate = composite_rates[i]
                    assert composite_rate == 5.92


def parse_composite_rates(row):
    rates = []
    for i in range(2, len(row)):
        try:
            col = row[i]
            composite_rate = float(col)
            # print("%s %s" % (col, composite_rate))
        except ValueError:
            composite_rate = None
            pass
        rates.append(composite_rate)
    return rates


def parse_inflation_rates(row):
    inflation_rates = []

    for i in range(2, len(row)):
        col = row[i]
        try:
            inflation_rate = float(col)
        except ValueError:
            inflation_rate = None

        inflation_rates.append(inflation_rate)

    return inflation_rates


def parse_rate_change_dates(row):
    dates = []

    for i in range(2, len(row)):
        col = row[i]

        try:
            if len(col) == 3:
                month = col[0: 1]
                year = col[1:]
            else:
                month = col[0: 2]
                year = col[2:]
            if year.startswith("9"):
                year = "19" + year
            else:
                year = "20" + year
            # 2012-01-19
            current_date = dateutil.parser.parse("{}-{}-01".format(year, month))
        except ValueError:
            current_date = None
            pass
        dates.append(current_date)

    return dates
