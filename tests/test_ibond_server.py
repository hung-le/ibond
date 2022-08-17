import unittest


def test_request_hello(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert "Hello world!" == response.json['msg']


def test_request_rates(client):
    response = client.get("/api/rates")
    assert response.status_code == 200
    assert response.json["name"] == "rates"
    rates = response.json["rates"]
    assert len(rates) == 290

    expected_rate = {
        'composite_rate': 4.66,
        'date': '1998-09-01T00:00:00',
        'fixed_rate': 3.4,
        'inflation_rate': 0.62
    }

    test_case = unittest.TestCase()
    for rate in rates:
        if rate['date'] == expected_rate['date']:
            test_case.assertDictEqual(rate, expected_rate)
            # assert rate['composite_rate'] == expected_rate['composite_rate']
            # assert rate['fixed_rate'] == expected_rate['fixed_rate']
            # assert rate['inflation_rate'] == expected_rate['inflation_rate']


def test_request_rate(client):
    response = client.get("/api/rate/2001/1")
    assert response.status_code == 200
    assert response.json["name"] == "rate"
    rate = response.json["rate"]
    assert len(rate) == 4

    expected_rate = {
        "composite_rate": 6.49,
        "date": "2001-01-01T00:00:00",
        "fixed_rate": 3.4,
        "inflation_rate": 1.52
    }
    test_case = unittest.TestCase()
    test_case.assertDictEqual(rate, expected_rate)


def test_request_values(client):
    data = {
        "issue_year": "2000",
        "issue_month": "1",
        "end_year": "2020",
        "end_month": "1",
    }
    response = client.get("/api/values", query_string=data)
    assert response.status_code == 200
    assert response.json["name"] == "values"
    values = response.json["values"]
    assert len(values) == 241

    expected_first = {
        'composite_rate': 6.98,
        'date': '2000-02-01T00:00:00',
        'fixed_rate': 3.4,
        'inflation_rate': 1.76,
        'unit_value': 25.87,
        'value': 1005.6
    }
    expected_last = {
        'composite_rate': 5.45,
        'date': '2020-02-01T00:00:00',
        'fixed_rate': 3.4,
        'inflation_rate': 1.01,
        'unit_value': 78.53,
        'value': 3071.6
    }

    test_case = unittest.TestCase()

    # for value in values:
    #     print(value)
    test_case.assertDictEqual(values[0], expected_first)
    test_case.assertDictEqual(values[-1], expected_last)
