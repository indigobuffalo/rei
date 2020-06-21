Simple service for getting REI event data.

## Running

Run locally:

```
pipenv run flask run --port 5001
```

Run with Docker:

```
docker run --publish 5001:5001 rei:latest
```

## Sample usage: 

Get available endpoints:
```
➜  ~ curl localhost:5001/
[
  "/sales"
]
```

Get types of sales:
```
➜  ~ curl localhost:5001/sales
[
  "/garage"
]
```

Get garage sale details:
```
➜  ~ curl localhost:5001/sales/garage
[
  {
    "address": "1338 San Pablo Ave, Berkeley, Ca 94702",
    "date": "Saturday, February 8, 2020",
    "hours": "8:00AM-1:00PM",
    "phone": "1-800-426-4840"
  },
  {
    "address": "1975 Diamond Blvd Ste B100, Concord, Ca 94520",
    "date": "Saturday, March 14, 2020",
    "hours": "10:00AM-7:00PM",
    "phone": "1-800-426-4840"
  },
  {
    "address": "400 El Paseo De Saratoga, San Jose, Ca 95130",
    "date": null,
    "hours": null,
    "phone": "1-800-426-4840"
  },
  {
    "address": "840 Brannan St, San Francisco, Ca 94103",
    "date": "Saturday, March 14, 2020",
    "hours": "8:00AM-1:00PM",
    "phone": "1-800-426-4840"
  }
```

