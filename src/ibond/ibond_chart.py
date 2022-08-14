import datetime

import dateutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from dateutil import relativedelta

import ibond_rates
from ibond import ibond_values


def main():

    my_ibonds = {
        'date': [],
        'fixed_rate': [],
        'inflation_rate': [],
        'composite_rate': [],
        'unit_value': [],
        'value': []
    }
    issued_date = datetime.datetime(1998, 9, 1)
    ibond = ibond_rates.IBond(1000, issued_date)

    today = datetime.date.today()
    until_date = datetime.datetime(today.year, today.month, 1)

    value_as_of = issued_date

    # value_as_of = datetime.datetime(2022, 1, 1)

    rates_table = ibond_rates.IBondRates()

    while value_as_of < until_date:
        values_table = ibond_values.IBondValues(ibond, value_as_of, rates_table)
        ibond_value = values_table.find(value_as_of)
        #         date, fixed_rate, inflation_rate, composite_rate, unit_value, value
        if ibond_value:
            my_ibonds['date'].append(ibond_value.date)
            my_ibonds['fixed_rate'].append(ibond_value.fixed_rate)
            my_ibonds['inflation_rate'].append(ibond_value.inflation_rate)
            my_ibonds['composite_rate'].append(ibond_value.composite_rate)
            my_ibonds['unit_value'].append(ibond_value.unit_value)
            my_ibonds['value'].append(ibond_value.value)
        value_as_of = value_as_of + relativedelta.relativedelta(months=1)

    df = pd.DataFrame(my_ibonds)
    # print(df)
    # df.plot('date', 'composite_rate')
    # plt.savefig("mygraph.png")
    fig, ax = plt.subplots()
    # define colors to use
    col1 = 'steelblue'
    col2 = 'red'

    # define subplots
    fig, ax = plt.subplots(figsize=(16, 8))

    # add first line to plot
    ax.plot(df.date, df.composite_rate, color=col1)
    # add x-axis label
    ax.set_xlabel('Date', fontsize=14)

    # add y-axis label
    ax.set_ylabel('Rate', color=col1, fontsize=16)

    # define second y-axis that shares x-axis with current plot
    ax2 = ax.twinx()

    # add second line to plot
    ax2.plot(df.date, df.value, color=col2)

    # add second y-axis label
    ax2.set_ylabel('Value', color=col2, fontsize=16)

    plt.suptitle("ibond - issued_date={}".format(issued_date))
    plt.savefig("mygraph.png")


if __name__ == "__main__":
    main()
