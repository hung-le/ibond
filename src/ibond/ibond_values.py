from dateutil import relativedelta
from marshmallow import Schema, fields

from ibond.ibond_rates import IBondRates, IBond


class IBondValue:

    def __init__(
            self, date, fixed_rate, inflation_rate, composite_rate, unit_value, value
    ):
        # ['2003/12', 1.1, 0.54, 2.19, 25.27, 1002.0, 1003.6, 1005.6, 1007.2, 1009.2, 1010.8]
        self.date = date
        self.fixed_rate = fixed_rate
        self.inflation_rate = inflation_rate
        self.composite_rate = composite_rate
        self.unit_value = unit_value
        self.value = value

    def __str__(self):
        return f"{self.date}, {self.fixed_rate}, {self.inflation_rate}, {self.composite_rate}, {self.unit_value}, {self.value}"


def create_ibond_value(cols, count, value):
    (date, fixed_rate, inflation_rate, composite_rate, unit_value) = cols
    date = date + relativedelta.relativedelta(months=count)
    ibond_value = IBondValue(
        date, fixed_rate, inflation_rate, composite_rate, unit_value, value
    )
    return ibond_value


def format_date(date):
    return date.strftime("%Y/%m")


class IBondValues:

    def __init__(self, ibond, to_date, ibond_rates, assume_inflation_rate=0.00):
        self.ibond = ibond
        self.to_date = to_date
        self.ibond_rates = ibond_rates
        self.assume_inflation_rate = assume_inflation_rate
        self.unit_value = 25
        self.units = self.ibond.denomination / self.unit_value
        self.fixed_rate = self.ibond_rates.get_fixed_rate(self.ibond.issue_date)
        self.table = []
        self.lookup_table = []

        self._calculate()

    def find(self, value_date):
        if value_date in self.lookup_table:
            return self.lookup_table[value_date]
        else:
            return None

    def get_value_for_units(self, count, composite_rate, unit_value):
        index = (count % 6) + 1
        # =IF($B11="","",ROUND($A$5*ROUND($D10*(1+$C11/2)^(E$6/6),2),2))
        base_value = 1 + (composite_rate / 100) / 2
        value = base_value
        exponent_value = index / 6
        # value = exponent_value
        value = pow(base_value, exponent_value)
        value = round((unit_value * value), 2)
        # value = round(value, 2)
        value = round((value * self.units), 2)
        # value = round(value, 2)
        return value

    def _calculate_on_rate_change_date(self, current_date, current_unit_value):
        inflation_rate = self.ibond_rates.get_inflation_rate(current_date)
        if not inflation_rate:
            inflation_rate = self.assume_inflation_rate
        composite_rate = self.ibond_rates.compute_composite_rate(
            self.fixed_rate, inflation_rate
        )

        current_unit_value = self.ibond_rates.compute_unit_value(
            current_unit_value, composite_rate
        )

        cols = (
            current_date,
            self.fixed_rate,
            inflation_rate,
            composite_rate,
            current_unit_value,
        )

        return current_unit_value, composite_rate, cols

    def _calculate(self):
        self.table = []
        self.lookup_table = {}

        issue_date = self.ibond.issue_date
        current_date = issue_date
        current_unit_value = self.unit_value
        prev_unit_value = current_unit_value

        row = []
        cols = []
        count = 0

        while current_date <= self.to_date:
            if (count % 6) == 0:
                if len(row) > 0:
                    self.table.append(row)
                    # print(row)
                    row = []
                prev_unit_value = current_unit_value
                (
                    current_unit_value,
                    composite_rate,
                    cols,
                ) = self._calculate_on_rate_change_date(
                    current_date, current_unit_value
                )
                row.extend(cols)

            value = self.get_value_for_units(count, composite_rate, prev_unit_value)
            row.append(value)
            ibond_value = create_ibond_value(cols, (count % 6) + 1, value)
            self.lookup_table[ibond_value.date] = ibond_value
            # print(ibond_value)

            # go on next month
            count = count + 1
            current_date = current_date + relativedelta.relativedelta(months=1)

        # print last row
        if len(row) > 0:
            self.table.append(row)
            # print(row)
            row = []


class IBondValueSchema(Schema):
    date = fields.DateTime()
    fixed_rate = fields.Float()
    inflation_rate = fields.Float()
    composite_rate = fields.Float()
    unit_value = fields.Float()
    value = fields.Float()


class IBondCalculator:

    def __init__(self, from_date, amount, to_date, assume_inflation_rate=0.00):
        self.from_date = from_date
        self.amount = amount
        self.to_date = to_date
        self.assume_inflation_rate = assume_inflation_rate

        ibond_rates = IBondRates()
        issue_date = self.from_date
        denomination = amount
        ibond = IBond(denomination, issue_date)
        value_as_of = to_date
        self.ibond_values = IBondValues(
            ibond, value_as_of, ibond_rates, assume_inflation_rate=assume_inflation_rate
        )

    def get_lookup_table(self):
        return self.ibond_values.lookup_table
