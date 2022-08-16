import collections
import csv
import datetime
import io
from pathlib import Path

from dateutil import relativedelta
from marshmallow import Schema, fields

IBOND_RATES_FILE_NAME = "ibond_rates.csv"


class IBond:

    def __init__(self, denomination, issue_date):
        self.denomination = denomination
        self.issue_date = issue_date


class IBondRate:

    # col_names = ["date", "fixed_rate", "inflation_rate", "composite_rate"]
    def __init__(self, date, fixed_rate, inflation_rate, composite_rate):
        self.date = date
        self.fixed_rate = fixed_rate
        self.inflation_rate = inflation_rate
        self.composite_rate = composite_rate


class IBondRateSchema(Schema):
    date = fields.DateTime()
    fixed_rate = fields.Float()
    inflation_rate = fields.Float()
    composite_rate = fields.Float()


# Class to hold the rates table
class IBondRates:

    def __init__(self, rates_filename=IBOND_RATES_FILE_NAME, date_format="%B %d, %Y"):
        self.date_format = date_format
        self.rates_list = self._read_rates_file(rates_filename)
        self.rates_map = self._create_rates_map(self.rates_list)

    def _read_rates_file(self, file_name):
        # print("_read_rates_file, file_name=%s" % file_name)
        p = Path(__file__).with_name(file_name)
        with p.open('r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            # Date,Fixed Rate,Inflation Rate,
            rates_list = []
            for row in csv_reader:
                value_as_of_str = row["date"].strip()
                if len(value_as_of_str) <= 0:
                    continue
                date = datetime.datetime.strptime(value_as_of_str, self.date_format)
                fixed_rate = float(row["fixed_rate"].strip().strip("%"))
                inflation_rate = float(row["inflation_rate"].strip().strip("%"))
                rate = IBondRate(date, fixed_rate, inflation_rate, None)
                rates_list.append(rate)
        return rates_list

    def _get_map_key(self, date):
        key = str(date.year) + str(date.month)
        return key

    def _create_rates_map(self, rates_list):
        rates_map = collections.OrderedDict()
        rates_list.sort(key=lambda x: x.date)
        for rate in rates_list:
            fixed_rate = rate.fixed_rate
            inflation_rate = rate.inflation_rate
            composite_rate = self.compute_composite_rate(fixed_rate, inflation_rate)

            for i in range(0, 6):
                if i == 0:
                    date = rate.date
                    # print("##")
                else:
                    date = date + relativedelta.relativedelta(months=1)
                rate.composite_rate = composite_rate
                key = self._get_map_key(date)
                rates_map[key] = rate

        return rates_map

    def get_fixed_rate(self, issue_date):
        fixed_rate = None
        rate = self._get_rate(issue_date, self.rates_map)
        if rate:
            fixed_rate = rate.fixed_rate
        return fixed_rate

    def get_inflation_rate(self, current_date):
        inflation_rate = None
        rate = self._get_rate(current_date, self.rates_map)
        if rate:
            inflation_rate = rate.inflation_rate
        return inflation_rate

    def get_composite_rate(self, current_date):
        composite_rate = None
        rate = self._get_rate(current_date, self.rates_map)
        if rate:
            composite_rate = rate.composite_rate
        return composite_rate

    def _get_rate(self, date, rates_map):
        # key = str(date.year) + str(date.month)
        key = self._get_map_key(date)
        if key in rates_map:
            rate = rates_map[key]
        else:
            rate = None
        return rate

    def write_csv_to_string(self):
        col_names = ["date", "fixed_rate", "inflation_rate", "composite_rate"]
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(col_names)
        for rate in self.rates_map.values():
            writer.writerow(rate)

        return output.getvalue()

    def get_rates(self):
        # data = []
        # for rate in self.rates_map.values():
        #    json_dict = dict()
        #    json_dict["date"] = rate.date
        #    json_dict["fixed_rate"] = rate.fixed_rate
        #    json_dict["inflation_rate"] = rate.inflation_rate
        #    json_dict["composite_rate"] = rate.composite_rate
        #    data.append(json_dict)

        # return data
        return self.rates_map.values()

    def write_json_to_string(self):
        MySchema = Schema.from_dict(
            {
                "type": fields.Str(),
                "rates": fields.List(fields.Nested(IBondRateSchema())),
            }
        )
        data = {}
        data["type"] = "rates_table"
        data["rates"] = self.rates_map.values()
        result = MySchema().dumps(data)
        return result

    def compute_composite_rate(self, fixed_rate, inflation_rate):
        # Composite rate = [fixed rate + (2 x semiannual inflation rate)
        #                    + (fixed rate x semiannual inflation rate)]
        # [0.0000 + (2 x 0.0481) + (0.0000 x 0.0481)]
        # [0.0000 + 0.0962 + 0.0000000]
        # =L13+2*M13+L13*M13
        fixed_rate = fixed_rate / 100.00
        inflation_rate = inflation_rate / 100.00

        # composite_rate_1 = 2 * inflation_rate
        # composite_rate_2 = fixed_rate * inflation_rate
        # composite_rate = fixed_rate + composite_rate_1 + composite_rate_2
        composite_rate = fixed_rate + 2 * inflation_rate + fixed_rate * inflation_rate

        composite_rate = composite_rate * 100.00

        if composite_rate < 0.00:
            composite_rate = 0.00

        composite_rate = round(composite_rate, 2)
        return composite_rate

    def compute_unit_value(self, unit_value, composite_rate):
        value = unit_value * (1 + (composite_rate / 100.0) / 2)
        unit_value = round(value, 2)
        return unit_value


def main():
    pass


if __name__ == "__main__":
    main()
