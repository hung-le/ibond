import datetime
import unittest

from dateutil import relativedelta

from ibond import ibond_rates
from ibond import ibond_values

COL_IBOND_VALUE = 1

COL_IBOND = 0


class Testing(unittest.TestCase):

    def test_calculate_ibond_values(self):
        # rates_filename = "ibond_rates.csv"
        rates_table = ibond_rates.IBondRates()

        today = datetime.date.today()
        value_as_of = datetime.datetime(today.year, today.month, 1)

        # expected values as of 'value_date'
        value_date = datetime.datetime(2022, 5, 1)
        expected_values = self.create_expected_values()

        for row in expected_values:
            ibond = row[COL_IBOND]
            expected_value = row[COL_IBOND_VALUE]

            values_table = ibond_values.IBondValues(ibond, value_as_of, rates_table)
            ibond_value = values_table.find(value_date)

            # json_dict = dict(ibond_value.__dict__)
            # json_dict["issue_date"] = issue_date
            # json_dict["denomination"] = denomination
            # json_dict['value_as_of'] = value_as_of
            # print(json.dumps(json_dict, indent=4, sort_keys=True, default=str))
            self.assertEqual(ibond_value.value, expected_value)

    def create_expected_values(self):
        expected_values = []
        expected_values.append((ibond_rates.IBond(500, datetime.datetime(2002, 1, 1)), 1174.60))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 2, 1)), 2331.6))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 3, 1)), 2314.40))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 4, 1)), 2297.20))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 5, 1)), 2333.20))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 6, 1)), 2316.00))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 7, 1)), 2298.80))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 8, 1)), 2281.60))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 9, 1)), 2264.40))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 10, 1)), 2247.60))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 11, 1)), 2137.20))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2002, 12, 1)), 2122.00))
        expected_values.append((ibond_rates.IBond(1000, datetime.datetime(2003, 1, 1)), 2106.80))
        return expected_values


if __name__ == "__main__":
    unittest.main()


def test_rates_if_purchase_now():
    today = datetime.date.today()
    issued_date = datetime.datetime(today.year, today.month, 1)

    ibond = ibond_rates.IBond(1000, issued_date)

    rates_table = ibond_rates.IBondRates()

    inflation_rate = rates_table.get_inflation_rate(issued_date)

    print("#")
    value_as_of = issued_date
    for i in range(0, 12):
        values_table = ibond_values.IBondValues(ibond, value_as_of, rates_table)

        ibond_value = values_table.find(value_as_of)
        if ibond_value:
            print(ibond_value)
        value_as_of = value_as_of + relativedelta.relativedelta(months=1)

    print("#")
    value_as_of = issued_date
    for i in range(0, 12):
        values_table = ibond_values.IBondValues(ibond, value_as_of, rates_table, assume_inflation_rate=inflation_rate)

        ibond_value = values_table.find(value_as_of)
        if ibond_value:
            print(ibond_value)
        value_as_of = value_as_of + relativedelta.relativedelta(months=1)

    print("#")
    value_as_of = issued_date
    for i in range(0, 12):
        values_table = ibond_values.IBondValues(ibond, value_as_of, rates_table,
                                                assume_inflation_rate=inflation_rate/2.0)

        ibond_value = values_table.find(value_as_of)
        if ibond_value:
            print(ibond_value)
        value_as_of = value_as_of + relativedelta.relativedelta(months=1)
