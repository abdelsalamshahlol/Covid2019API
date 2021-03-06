"""
FILE: router_api_v1.py
DESCRIPTION: all routes for API v1
AUTHOR: Nuttaphat Arunoprayoch
DATE: 04-April-2020
"""
from functools import wraps
from typing import Dict, Any

from . import v1
from utils.helper import lookup_country
from models.covid_model_api_v1 import NovelCoronaAPIv1


# Reload model (APIv1)
def reload_model_api_v1(func):
    """ Reload a model for each quest """
    @wraps(func)
    def wrapper(*args, **kwargs):
        global novel_corona_api, dt, ts
        novel_corona_api = NovelCoronaAPIv1()
        dt, ts = novel_corona_api.datetime_raw, novel_corona_api.timestamp
        return func(*args, **kwargs)
    return wrapper


@v1.get('/current')
@reload_model_api_v1
def current_status() -> Dict[str, int]:
    data = novel_corona_api.get_current_status()
    return data


@v1.get('/current_list')
@reload_model_api_v1
def current_status_list() -> Dict[str, Any]:
    """ Coutries are kept in a List """
    data = novel_corona_api.get_current_status(list_required=True)
    return data


@v1.get('/total')
@reload_model_api_v1
def total() -> Dict[str, Any]:
    data = novel_corona_api.get_total()
    return data


@v1.get('/confirmed')
@reload_model_api_v1
def confirmed_cases() -> Dict[str, int]:
    data = novel_corona_api.get_confirmed_cases()
    return data


@v1.get('/deaths')
@reload_model_api_v1
def deaths() -> Dict[str, int]:
    data = novel_corona_api.get_deaths()
    return data


@v1.get('/recovered')
@reload_model_api_v1
def recovered() -> Dict[str, int]:
    data = novel_corona_api.get_recovered()
    return data


@v1.get('/countries')
@reload_model_api_v1
def affected_countries() -> Dict[int, str]:
    data = novel_corona_api.get_affected_countries()
    return data


@v1.get('/country/{country_name}')
@reload_model_api_v1
def country(country_name: str) -> Dict[str, Any]:
    """ Search by name or ISO (alpha2) """
    raw_data = novel_corona_api.get_current_status() # Get all current data
    try:
        if country_name.lower() not in ['us', 'uk'] and len(country_name) in [2]:
            country_name = lookup_country(country_name)
            data = {k: v for k, v in raw_data.items() if country_name.lower() in k.lower()}
        else:
            data = {k: v for k, v in raw_data.items() if country_name.lower() == k.lower()}

        # Add dt and ts
        data['dt'] = raw_data['dt']
        data['ts'] = raw_data['ts']

    except:
        raise HTTPException(status_code=404, detail="Item not found")

    return data


@v1.get('/timeseries/{case}')
@reload_model_api_v1
def timeseries(case: str) -> Dict[str, Any]:
    """ Get the time series based on a given case: confirmed, deaths, recovered """
    raw_data = novel_corona_api.get_time_series()
    case = case.lower()

    if case in ['confirmed', 'deaths', 'recovered']:
        data = {case: raw_data[case]}
        data['dt'] = raw_data['dt']
        data['ts'] = raw_data['ts']

    else:
        raise HTTPException(status_code=404, detail="Item not found")

    return data