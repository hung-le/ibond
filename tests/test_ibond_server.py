import unittest


def test_request_hello(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert b"Hello, World!" in response.data


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


def test_request_values(client):
    response = client.get("/api/values")
    assert response.status_code == 200
    assert response.json["name"] == "values"
    values = response.json["values"]
    assert len(values) == 13
    # for value in values:
    #     print(value)
