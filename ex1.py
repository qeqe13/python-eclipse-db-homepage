#-*- coding:utf-8 -*-
'''
Created on 2018. 11. 30.

@author: qeqe
'''
import array
from flask import json
import sqlite3
import urllib.parse
import time

from astropy.wcs.docstrings import lng
from flask import Flask, render_template, request, session, redirect, url_for, g
from flask import _app_ctx_stack
from _ast import Str
from requests.api import get

import urllib.parse

from collections import Counter
DATABASE = 'HJ_DB.db'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def mergeNation(db_list):
    #nation, noc, area, pop, gdp, medal
    merge_nation = dict()
    for nation, noc, area, pop, gdp, medal in db_list:
        if medal is None:
            medal = 0

        if nation in merge_nation:
            merge_nation[nation][0].append(noc)
            merge_nation[nation][-1] += medal
        else:
            merge_nation.setdefault(nation, [[noc], area, pop, gdp, medal])

    result_list = []
    for key, value in merge_nation.items():
        result_list.append((key, ", ".join(value[0]), value[1], value[2], value[3], value[4]))

    return result_list

def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(DATABASE)
    return top.sqlite_db

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_connection(exception):
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

@app.route('/', methods = ['GET'])
def hello_world():

    statis11 = []
    statis_poppop = []
    statis_gdpgdp = []
    statis_areaarea = []
    statis1 = g.db.execute("select * from (select Country, NOC, Area, Population, GDP from countries_of_the_world join noc_regions where countries_of_the_world.Country = noc_regions.region) left natural join(select NOC, count(Medal) from athlete_events where athlete_events.Medal = 'Gold' or athlete_events.Medal = 'Silver' or athlete_events.Medal = 'Bronze' group by NOC)")
    statis11 = mergeNation(statis1)
    statis_medalmedal = [(a, b, c) for a, b, _, _, _, c in sorted(statis11, key=lambda x:x[5], reverse=True)[:3]]
    statis_poppop = [(a, b, c) for a, b, _, c, _, _ in sorted(statis11, key=lambda x:x[3], reverse=True)[:3]]
    statis_gdpgdp = [(a, b, c) for a, b, _, _, c, _ in sorted(statis11, key=lambda x:x[4], reverse=True)[:3]]
    statis_areaarea = [(a, b, c) for a, b, c, _, _, _ in sorted(statis11, key=lambda x:x[2], reverse=True)[:3]]
    # statis11 = [(a, b, c, d, e, f) if f is not None else (a, b, c, d, e, 0) for a, b, c, d, e, f in statis1.fetchall()]
    # statis_pop = g.db.execute("select Country, NOC, Population from countries_of_the_world join noc_regions where noc_regions.region = countries_of_the_world.Country order by Population desc limit 3")
    # statis_poppop = statis_pop.fetchall()
    # statis_gdp = g.db.execute("select Country, NOC, GDP from countries_of_the_world join noc_regions where noc_regions.region = countries_of_the_world.Country order by GDP desc limit 3")
    # statis_gdpgdp= statis_gdp.fetchall()
    # statis_area = g.db.execute("select Country, NOC, Area from countries_of_the_world join noc_regions where noc_regions.region = countries_of_the_world.Country order by Area desc limit 3")
    # statis_areaarea = statis_area.fetchall()

    # keyword = ["NOC=\"EUN\",  NOC=\"RUS\", NOC=\"URS\""]
    # keyword = p"NOC=\"AFG\""]
    #
    # query = "select * from athlete_events where {}".format(keyword)
    return render_template('Main.html', statis11 = statis11, statis_medalmedal=statis_medalmedal, statis_poppop = statis_poppop, statis_gdpgdp = statis_gdpgdp, statis_areaarea = statis_areaarea)

@app.route('/chart')
def chart_page():
    print("나 들어왔땅")
    '''
    key = urllib.parse.unquote_plus(request.args.get("keyword")) 
    
    keyword = "%"+key+"%"
    qu = g.db.execute("select Country from athlete_events where name LIKE '%s'" %keyword )
    '''
    return render_template('index2.html')

@app.route('/search', methods=['GET'])
def nation_search():
    if request.method == 'GET':
        q_nation = request.args.get('q_nation')
        q_noc = request.args.get('q_noc')
        q_nation = urllib.parse.unquote(q_nation)
        q_noc = urllib.parse.unquote(q_noc)

    print(q_nation)
    print(q_noc)

    keywords = q_noc.split(", ")    # ["EUN", "RUS", "URS"]
    query_keywords = []
    for keyword in keywords:
        query_keywords.append("NOC='{}'".format(keyword))
    #qurey_keywords = ['NOC=\"EUN\"', 'NOC=\"RUS"', 'NOC=\"URS"']

    query_keywords = " or ".join(query_keywords) #'NOC=\"EUN\" or NOC=\"RUS\" or NOC=\"URS\"'
    query_gold = "select NOC, year, count(Medal) from athlete_events where ({}) and Medal = 'Gold' group by year".format(query_keywords)
    # query_silver
    # query_bronze
    # query_total
    # pop, gdp,

    result_db = g.db.execute(query_gold)
    result_count_gold = {"labels":[], "data":[]}
    for _, year, count_gold in result_db:
        result_count_gold["labels"].append(str(year))
        result_count_gold["data"].append(count_gold)

    # print(result_db)
    #trophy_overview = g.db.execute("select Country, NOC from countries_of_the_world join noc_regions where countries_of_the_world.Country = noc_regions.regiont")
    #query 
    return render_template('nation_detail.html', gold_count_list=json.dumps(result_count_gold))

if __name__=='__main__':
    app.run(host = '127.0.0.1')
    