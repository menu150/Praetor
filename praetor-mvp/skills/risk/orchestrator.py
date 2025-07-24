import datetime
from skills.drivers.news    import fetch as news_fetch
from skills.drivers.finance import fetch as finance_fetch
from skills.drivers.geo     import fetch as geo_fetch

def run(region: str, weights: dict = None) -> dict:
    if weights is None:
        weights = {'news':0.4,'finance':0.3,'geo':0.3}

    drivers = {
        'news':    news_fetch(region),
        'finance': finance_fetch(region),
        'geo':     geo_fetch(region),
    }

    score = sum(drivers[k]*weights[k] for k in drivers)
    score = max(0.0, min(1.0, score))

    return {
      'region':      region,
      'risk_score':  round(score,3),
      'drivers':     {k: round(v,3) for k,v in drivers.items()},
      'weights':     weights,
      'timestamp':   datetime.datetime.utcnow().isoformat()+'Z'
    }
