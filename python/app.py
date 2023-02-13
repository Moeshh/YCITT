from flask import Flask
from urllib.parse import urlparse
from urllib.parse import parse_qs
import functie
import pokemon
import sqltest
import pandas as pd

import urllib.request
from html_table_parser import HTMLTableParser

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'

@app.route('/test/<zoekterm>')
def test(zoekterm):
    return functie.returnwaarde(zoekterm)

@app.route('/getpok/<poke>')
def getpok(poke):
    return pokemon.getpokemons(poke)

@app.route('/sql/<querytype>')
def getquery(querytype):
    query = querytype.split('=')
    match query[0]:
        case 'select':
            return sqltest.selectquery()
        case 'insert':
            return sqltest.insertquery()
        case 'query':
            return sqltest.wherequery(query[1])

@app.route('/rooster/')
def rooster():
    xhtml = url_get_contents('http://p.codefounders.nl/p').decode('utf-8')
    p = HTMLTableParser()
    p.feed(xhtml)
    df = pd.DataFrame(p.tables[0])
    
    #remove indexed headers 0-1-2-3-4 and use top row as headers datum tijd etc.
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    #merge dag and datum into 1 row
    df['Datum'] = df.apply(merge_columns, axis=1)
    #rearrange columns
    columns_titles = ['Datum','Tijd','Training','Les info','Trainer(s)','Locatie','Status']
    df=df.reindex(columns=columns_titles)
    #only show rows relevant to class yc2302
    df.drop(df[df['Training'] != 'YC2302'].index, inplace=True)
    #dchange time format
    df['Tijd'] = df['Tijd'].apply(convert_time_range)
    html_string = '<html><head><title>Rooster</title><style>body { background-color: linen; } table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #d8d8d8; padding: 8px; text-align: left; } th { background-color: #d8d8d8; }tr:nth-child(even) { background-color: #f8f8f8;}tr:nth-child(odd) { background-color: #f0f0f0;}</style></head><body>'

    return html_string + df.to_html(index=False)
    
def url_get_contents(url):
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)
    return f.read()

def merge_columns(row):
    return str(row['Dag']) + ' ' + row['Datum']

def convert_time_range(time_range):
    start, end = time_range.split('-')
    start = start.zfill(2)
    end = end.zfill(2)
    return f"{start}:00-{end}:00"