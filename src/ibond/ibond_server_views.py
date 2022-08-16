import datetime
from os import abort

from dateutil import relativedelta
from flask import Blueprint, request
from marshmallow import Schema, fields

from ibond.ibond_rates import IBondRates, IBondRateSchema
from ibond.ibond_values import IBondCalculator, IBondValueSchema

api = Blueprint('api', __name__, url_prefix='/api')

rates_table = IBondRates()


# a simple page that says hello
@api.route('/hello')
def get_hello():
    return 'Hello, World!'


@api.route("/rates")
def get_rates():
    rates = rates_table.get_rates()
    schema = IBondRateSchema(many=True)
    result = schema.dump(rates)
    # print(result)
    response = {
        'name': 'rates',
        'rates': result
    }
    # response = result
    return response


def check_data(schema, data):
    try:
        return schema().load(data)
    except Exception as e:
        abort(400, exception=str(e))


def cmd_sim_min_purchase(denomination, assume_inflation_rate):
    today = datetime.date.today()
    issue_date = datetime.datetime(today.year, today.month, 1)

    value_as_of = issue_date + relativedelta.relativedelta(months=12)

    ibond_calculator = IBondCalculator(
        issue_date,
        denomination,
        value_as_of,
        assume_inflation_rate=assume_inflation_rate,
    )
    return ibond_calculator


class ValuesQuerySchema(Schema):
    denomination = fields.Float(missing=1000.00)
    assume_inflation_rate = fields.Float(missing=0.00)


@api.route("/values")
def get_values():
    parameters = check_data(ValuesQuerySchema, request.args)
    ibond_calculator = cmd_sim_min_purchase(
        parameters["denomination"], parameters["assume_inflation_rate"]
    )
    lookup_table = ibond_calculator.get_lookup_table()
    schema = IBondValueSchema(many=True)
    result = schema.dump(lookup_table.values())
    response = {
        'name': 'values',
        'values': result
    }
    # response = result
    return response
