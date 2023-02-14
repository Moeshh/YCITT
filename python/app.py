from flask import Flask
from urllib.parse import urlparse
from urllib.parse import parse_qs
import functie
import pokemon
import sqltest
import pandas as pd
import mysql.connector
import urllib.request
import locale
import datetime
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
        case 'insertrooster':
            return insertrooster()

@app.route('/newrooster/')
def newrooster():
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
    df.drop(df[df['Training'] == 'Weekend'].index, inplace=True)
    df.drop(df[df['Training'] == ''].index, inplace=True)
    #df.drop(df[df['Training'] != 'YC2302'].index, inplace=True)
    #dchange time format
    df['Datum'] = df['Datum'].str.replace('ma ', '').str.replace('di ', '').str.replace('wo ', '').str.replace('do ', '').str.replace('vr ', '').str.replace('-jan.', '-01').str.replace('-feb.', '-02').str.replace('-mrt.', '-03').str.replace('-apr.', '-04').str.replace('-mei.', '-05').str.replace('-jun.', '-06').str.replace('-jul.', '-07').str.replace('-aug.', '-08').str.replace('-sep.', '-09').str.replace('-okt.', '-10').str.replace('-nov.', '-11').str.replace('-dec.', '-12')
    df['Tijd'] = df['Tijd'].apply(convert_time_range)

    html_string = '<html><head><title>Rooster</title><style>body { background-color: linen; } table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #d8d8d8; padding: 8px; text-align: left; } th { background-color: #d8d8d8; }tr:nth-child(even) { background-color: #f8f8f8;}tr:nth-child(odd) { background-color: #f0f0f0;}</style></head><body>'

    return html_string + df.to_html(index=False)

@app.route('/rooster/')
def roosterall():
    return rooster('all')

@app.route('/rooster/<group>')
def rooster(group):
    dbconnect = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='',
        database='ycitt'
    )
    query = "SELECT * FROM rooster"
    df = pd.read_sql_query(query, dbconnect)
    dbconnect.close()
    #set language so I can use name of day %a
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
    #create columns for date and time 
    df["Datum"] = pd.to_datetime(df["starttime"]).dt.strftime("%a %d-%m")
    df["Tijd"] = pd.to_datetime(df["starttime"]).dt.strftime("%H:%M") + " tot " + pd.to_datetime(df["endtime"]).dt.strftime("%H:%M")
    #sort by datetime
    df = df.sort_values(by=['starttime'])
    #rename headers and sort the headers
    df = df.rename(columns={'id':'ID', 'starttime':'starttime', 'endtime':'endtime', 'class':'Groep', 'training':'Training', 'trainer':'Trainer(s)', 'location':'Locatie', 'info':'Info', 'source':'Source'})
    columns_titles = ['Datum','Tijd', 'Groep', 'Training','Info','Trainer(s)','Locatie','Source']
    df=df.reindex(columns=columns_titles)
    print(df)
    #drop everything but group, if group value is passed
    if group != 'all':
        df.drop(df[df['Groep'] != group].index, inplace=True)
    #highlight rows fo current day
    df = df.style.apply(highlight_rows, axis=1)
    df = df.set_table_styles([{'selector': '.col_heading','props': 'background-color: #d8d8d8; color: black;'}])
    #create thml and return dataframe as table
    html_string = '<html><head><title>Rooster</title><style>body { background-color: linen; } table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #d8d8d8; padding: 8px; text-align: left; } th { background-color: #d8d8d8; }tr:nth-child(even) { background-color: #f8f8f8;}tr:nth-child(odd) { background-color: #f0f0f0;}.today {background-color: yellow;}</style></head><body>'
    html = df.to_html(index=False)
    html_end = '</body></html>'
    return html_string + html + html_end

def highlight_rows(row):
    today = datetime.datetime.now().strftime('%a %d-%m')
    value = row.loc['Datum']
    if value == today:
        return ['background-color: #BAFFC9; border-color: #6ACD60' for r in row]
    else:
        return ['' for r in row]

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

def insertrooster():
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
    columns_titles = ['Datum','Tijd','Training','Les info','Trainer(s)','Locatie','Status','Les notities']
    df=df.reindex(columns=columns_titles)
    #only show rows relevant to class yc2302
    df.drop(df[df['Training'] == 'Weekend'].index, inplace=True)
    df.drop(df[df['Training'] == ''].index, inplace=True)
    #df.drop(df[df['Training'] != 'YC2302'].index, inplace=True)
    #dchange time format
    df['Datum'] = df['Datum'].str.replace('ma ', '').str.replace('di ', '').str.replace('wo ', '').str.replace('do ', '').str.replace('vr ', '').str.replace('-jan.', '-01').str.replace('-feb.', '-02').str.replace('-mrt.', '-03').str.replace('-apr.', '-04').str.replace('-mei.', '-05').str.replace('-mei', '-05').str.replace('-jun.', '-06').str.replace('-jul.', '-07').str.replace('-aug.', '-08').str.replace('-sep.', '-09').str.replace('-okt.', '-10').str.replace('-nov.', '-11').str.replace('-dec.', '-12')
    df['Tijd'] = df['Tijd'].apply(convert_time_range)
    
    dbconnect = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='',
        database='ycitt'
    )

    mycursor = dbconnect.cursor()
    for row in df.iterrows():
        training = row[1]['Les info']
        group = row[1]['Training']
        trainer = row[1]['Trainer(s)']
        location = row[1]['Locatie']
        source = row[1]['Status']
        datum = row[1]['Datum']+'-2023'
        notes = row[1]['Les notities']
        start_time, end_time = row[1]['Tijd'].split('-')
        start_datetime = pd.to_datetime(datum + start_time, format='%d-%m-%Y%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        end_datetime = pd.to_datetime(datum + end_time, format='%d-%m-%Y%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO rooster (starttime, endtime, class, training, trainer, location, info, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (start_datetime, end_datetime, group, training, trainer, location, notes, source)
        mycursor.execute(query, values)
    dbconnect.commit()
    return "rooster values inserted in database"