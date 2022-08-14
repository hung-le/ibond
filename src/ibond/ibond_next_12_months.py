import datetime

from dateutil import relativedelta

from ibond import ibond_rates, ibond_values


def find_rates_if_purchase_now():
    today = datetime.date.today()
    issued_date = datetime.datetime(today.year, today.month, 1)

    ibond = ibond_rates.IBond(1000, issued_date)

    rates_table = ibond_rates.IBondRates()

    inflation_rate = rates_table.get_inflation_rate(issued_date)

    value_as_of = issued_date
    assume_inflation_rate = 0.00
    values = method_name(ibond, value_as_of, rates_table, assume_inflation_rate)
    print("#")
    for value in values:
        print(value)

    value_as_of = issued_date
    assume_inflation_rate = inflation_rate
    values = method_name(ibond, value_as_of, rates_table, assume_inflation_rate)
    print("#")
    for value in values:
        print(value)

    value_as_of = issued_date
    assume_inflation_rate = inflation_rate / 2.0
    values = method_name(ibond, value_as_of, rates_table, assume_inflation_rate)
    print("#")
    for value in values:
        print(value)


def method_name(ibond, value_as_of, rates_table, assume_inflation_rate):
    result = []
    for i in range(0, 12):
        values_table = ibond_values.IBondValues(ibond, value_as_of, rates_table,
                                                assume_inflation_rate=assume_inflation_rate)

        ibond_value = values_table.find(value_as_of)
        if ibond_value:
            result.append(ibond_value)
        value_as_of = value_as_of + relativedelta.relativedelta(months=1)

    return result


def main():
    find_rates_if_purchase_now()


if __name__ == "__main__":
    main()
