import datetime
from os import abort

from dateutil import relativedelta
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields

from ibond.ibond_rates import IBondRates, IBondRateSchema
from ibond.ibond_values import IBondCalculator, IBondValueSchema

api = Blueprint('api', __name__, url_prefix='/api')

rates_table = IBondRates()


@api.errorhandler(Exception)
def handle_exception(e):
    return jsonify(
        exception=type(e).__name__,
        message=str(e)
    ), 400


# a simple page that says hello
@api.route('/hello')
def get_hello():
    response = {
        'now': datetime.date.today(),
        'msg': "Hello world!"
    }
    return response


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


@api.route("/rate/<int:year>/<int:month>")
def get_rate_by_year_month(year, month):
    rate = rates_table.get_rate(year, month)
    if rate is None:
        raise Exception("Cannot find rate for year={}, month={}".format(year, month))

    schema = IBondRateSchema()
    result = schema.dump(rate)
    # print(result)
    parameters = {
        'year': year,
        'month': month
    }
    response = {
        'name': 'rate',
        'parameters': parameters,
        'rate': result
    }
    # response = result
    return response


def check_data(schema, data):
    try:
        return schema().load(data)
    except Exception as e:
        abort(400, exception=str(e))


def cmd_sim_min_purchase(issue_year, issue_month,
                         end_year, end_month,
                         denomination, assume_inflation_rate):
    # today = datetime.date.today()
    issue_date = datetime.datetime(issue_year, issue_month, 1)

    value_as_of = datetime.datetime(end_year, end_month, 1)

    ibond_calculator = IBondCalculator(
        issue_date,
        denomination,
        value_as_of,
        assume_inflation_rate=assume_inflation_rate,
    )
    return ibond_calculator


class ValuesQuerySchema(Schema):
    today = datetime.date.today()
    end_date = today + relativedelta.relativedelta(months=12)

    issue_year = fields.Int(missing=today.year)
    issue_month = fields.Int(missing=today.month)

    end_year = fields.Int(missing=end_date.year)
    end_month = fields.Int(missing=end_date.month)

    denomination = fields.Float(missing=1000.00)

    assume_inflation_rate = fields.Float(missing=0.00)


@api.route("/values", methods=['GET'])
def get_values():
    parameters = check_data(ValuesQuerySchema, request.args)
    ibond_calculator = cmd_sim_min_purchase(
        parameters["issue_year"],
        parameters["issue_month"],
        parameters["end_year"],
        parameters["end_month"],
        parameters["denomination"],
        parameters["assume_inflation_rate"]
    )
    lookup_table = ibond_calculator.get_lookup_table()
    schema = IBondValueSchema(many=True)
    result = schema.dump(lookup_table.values())
    response = {
        'name': 'values',
        'parameters': parameters,
        'values': result
    }
    # response = result
    return response
