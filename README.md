# ibond

REST call for ibond rate (https://www.treasurydirect.gov/indiv/products/prod_ibonds_glance.htm)

## GET rate
```
curl -s https://stark-sea-90016.herokuapp.com/api/rate/2000/1
...
{
    "name": "rate",
    "parameters": {
        "month": 1,
        "year": 2000
    },
    "rate": {
        "composite_rate": 6.98,
        "date": "2000-01-01T00:00:00",
        "fixed_rate": 3.4,
        "inflation_rate": 1.76
    }
}
```

## GET rates
```
curl -s https://stark-sea-90016.herokuapp.com/api/rates
...
{
    "name": "rates",
    "rates": [
        {
            "composite_rate": 4.66,
            "date": "1998-09-01T00:00:00",
            "fixed_rate": 3.4,
            "inflation_rate": 0.62
        },
        {
            "composite_rate": 4.66,
            "date": "1998-10-01T00:00:00",
            "fixed_rate": 3.4,
            "inflation_rate": 0.62
        },
...
        {
            "composite_rate": 9.62,
            "date": "2022-08-01T00:00:00",
            "fixed_rate": 0.0,
            "inflation_rate": 4.81
        },
        {
            "composite_rate": 9.62,
            "date": "2022-09-01T00:00:00",
            "fixed_rate": 0.0,
            "inflation_rate": 4.81
        },
        {
            "composite_rate": 9.62,
            "date": "2022-10-01T00:00:00",
            "fixed_rate": 0.0,
            "inflation_rate": 4.81
        }
    ]
}
```

## GET values

Get values for ibond issued on issue_year/issue_month until end_year/end_month

* denomination: ibond denomination. Default: 1000
* issue_year: list ibond value for that were issued on issue_year. Default: today's year
* issue_month: list ibond value for that were issued on issue_month. Default: today's month
* end_year: list ibond value from issue year/month until end year/month. Defaut: 12-months from issue_year/issue_month
* end_month: list ibond value from issue year/month until end year/month. Defaut: 12-months from issue_year/issue_month

```
curl -s https://stark-sea-90016.herokuapp.com/api/values -G \
  -d denomination=2000 -d issue_year=2010 -d issue_month=1 -d end_year=2010 -d end_month=6
...
{
    "name": "values",
    "parameters": {
        "assume_inflation_rate": 0.0,
        "denomination": 2000.0,
        "end_month": 6,
        "end_year": 2010,
        "issue_month": 1,
        "issue_year": 2010
    },
    "values": [
        {
            "composite_rate": 3.36,
            "date": "2010-02-01T00:00:00",
            "fixed_rate": 0.3,
            "inflation_rate": 1.53,
            "unit_value": 25.42,
            "value": 2005.6
        },
...
        {
            "composite_rate": 3.36,
            "date": "2010-06-01T00:00:00",
            "fixed_rate": 0.3,
            "inflation_rate": 1.53,
            "unit_value": 25.42,
            "value": 2028.0
        },
        {
            "composite_rate": 3.36,
            "date": "2010-07-01T00:00:00",
            "fixed_rate": 0.3,
            "inflation_rate": 1.53,
            "unit_value": 25.42,
            "value": 2033.6
        }
    ]
}
```



```
