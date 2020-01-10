import base64
import os
import time
import atexit
import json
import datetime
from helpers import figs, flickr
from pymongo import MongoClient
import pandas as pd
from fastapi import FastAPI, Query, Form
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from typing import List

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, Response

app = FastAPI()

origins = [
    "https://www.kk6gpv.net",
    "https://api.kk6gpv.net",
    "https://idpgis.ncep.noaa.gov",
    "https://nowcoast.noaa.gov",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sid = os.environ['SID']

times = dict(m_5='5m', h_1='1h', h_6='6h', d_1='1d',
             d_2='2d', d_7='7d', d_30='30d')


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@app.get("/")
def main():
    return {"api": "kk6gpv.net"}


@app.get('/aprs/map')
def aprs_map(type_aprs: str, prop_aprs: str, time_int: str):
    map_aprs, plot_speed, plot_alt, plot_course, rows = figs.create_map_aprs(
        type_aprs, prop_aprs, time_int)
    data = {}
    data['map_aprs'] = json.loads(map_aprs)
    data['plot_speed'] = json.loads(plot_speed)
    data['plot_alt'] = json.loads(plot_alt)
    data['plot_course'] = json.loads(plot_course)
    data['rows'] = rows
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/aprs/igate_range')
def aprs_range_analysis(time_int: str):
    range_aprs = figs.create_range_aprs(time_int)
    data = {}
    data['range_aprs'] = json.loads(range_aprs)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/iot/graph')
def iot_graphs(time_int: str, sensor_iot: List[str] = Query(None)):
    graphJSON = figs.create_graph_iot(sensor_iot, time_int)
    return Response(graphJSON)


@app.get('/oilgas/details/graphs')
def oilgas_graphs(api: str):
    graph_oilgas, header = figs.get_graph_oilgas(str(api))
    graph_cyclic_jobs = figs.get_cyclic_jobs(header)
    graph_offset_oil, graph_offset_stm, graph_offset_wtr, graph_offset_oil_ci, graph_offset_stm_ci, graph_offset_wtr_ci, map_offsets, offsets = figs.get_offsets_oilgas(
        header, 0.1)
    try:
        header.pop('_id')
    except:
        pass
    try:
        header.pop('prodinj')
    except:
        pass
    try:
        header.pop('crm')
    except:
        pass
    try:
        header.pop('cyclic_jobs')
    except:
        pass
    data = {}
    try:
        data['header'] = header
    except:
        pass
    try:
        data['graph_oilgas'] = json.loads(graph_oilgas)
    except:
        pass
    try:
        data['graph_offset_oil'] = json.loads(graph_offset_oil)
    except:
        pass
    try:
        data['graph_offset_stm'] = json.loads(graph_offset_stm)
    except:
        pass
    try:
        data['graph_offset_wtr'] = json.loads(graph_offset_wtr)
    except:
        pass
    try:
        data['graph_offset_oil_ci'] = json.loads(graph_offset_oil_ci)
    except:
        pass
    try:
        data['graph_offset_stm_ci'] = json.loads(graph_offset_stm_ci)
    except:
        pass
    try:
        data['graph_offset_wtr_ci'] = json.loads(graph_offset_wtr_ci)
    except:
        pass
    try:
        data['graph_cyclic_jobs'] = json.loads(graph_cyclic_jobs)
    except:
        pass
    # data['map_offsets'] = map_offsets
    # data['offsets'] = offsets
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/galleries')
def galleries():
    rows = flickr.get_gal_rows(5)
    data = {}
    data['rows'] = rows
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/gallery')
def gallery_images(id: str):
    rows, map_gal, title, count_photos, count_views = flickr.get_photo_rows(
        id, 5)
    data = {}
    data['title'] = title
    data['count_photos'] = count_photos
    data['count_views'] = count_views
    data['rows'] = rows
    data['map'] = json.loads(map_gal)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/photos/photo')
def photos(id: str):
    image, map_photo = flickr.get_photo(id)
    data = {}
    data['image'] = image
    data['map'] = map_photo
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/station/history/graphs')
def station_historical_graphs(time_int: str):
    fig_td, fig_pr, fig_cb, fig_pc, fig_wd, fig_su, fig_wr, fig_thp = figs.create_wx_figs(
        time_int, sid)
    data = {}
    data['fig_td'] = json.loads(fig_td)
    data['fig_pr'] = json.loads(fig_pr)
    data['fig_cb'] = json.loads(fig_cb)
    data['fig_pc'] = json.loads(fig_pc)
    data['fig_wd'] = json.loads(fig_wd)
    data['fig_su'] = json.loads(fig_su)
    data['fig_wr'] = json.loads(fig_wr)
    data['fig_thp'] = json.loads(fig_thp)
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/station/live/data')
def station_live_data():
    wx = figs.get_wx_latest(sid)
    data = {}
    data['wx'] = wx
    json_compatible_item_data = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/weather/aviation/map')
def aviation_weather_map(prop_awc: str, lat: float, lon: float, zoom: int, infrared: str, radar: str, analysis: str, lightning: str, precip: str, watchwarn: str, temp: str, visible: str):
    graphJSON = figs.create_map_awc(
        prop_awc, lat, lon, zoom, infrared, radar, lightning, analysis, precip, watchwarn, temp, visible)
    return Response(graphJSON)


@app.get('/weather/soundings/image')
def sounding_plots(sid: str):
    img = figs.get_image(sid)
    json_compatible_item_data = jsonable_encoder(img.decode('unicode_escape'))
    return JSONResponse(content=json_compatible_item_data)
