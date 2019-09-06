from flask import Flask, render_template, jsonify, request
import psycopg2
import json
from datetime import datetime as dt
import logging

DEC2FLOAT = psycopg2.extensions.new_type(
            psycopg2.extensions.DECIMAL.values,
            'DEC2FLOAT',
            lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)                                                        ##get values from database as float


logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s", handlers=[logging.FileHandler("server.log")])           ##configure logger
sensors = ["wind_speed", "wind_direction", "air_temperature", "air_relhumidity", "smp10", "pqsl", "soil_moisture", "soil_tempblue", "soil_tempred", "air_pressure", "precipitation"]        ##sensors (collumns in database)
sensordata_dic = {}
datadict = {}
urlfix = 'http://10.180.12.123:5000/'

app = Flask(__name__)



####################### Routes ##########################
@app.route('/index')
@app.route('/')                                                                 ##route to homepage
@app.route('/home', methods=['GET'])
def home():
    liveurl = (urlfix + '_json?_home=home')
    url = urlfix
    return render_template('home.html', url=url, liveurl=liveurl)


@app.route('/temperature')                                                      ##routes for website with link to data and informations for graph
def temp():
    title = ('temperature')
    liveurl = (urlfix + '_livedata/air_temperature')
    url = (urlfix + '_multiple/air_temperature')
    chart = ('minRange: 15,')
    var = ('°C')
    navtemp = ('active')
    return render_template('json_graph.html', navtemp=navtemp, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/humidity')
def humidity():
    title = ('humidity')
    liveurl = (urlfix + '_livedata/air_relhumidity')
    url = (urlfix + '_multiple/air_relhumidity')
    chart = ('minRange: 15,')
    var = ("%")
    navhum = ('active')
    return render_template('json_graph.html', navhum=navhum, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/windspeed')
def windspeed():
    title = ('windspeed')
    liveurl = (urlfix + '_livedata/wind_speed')
    url = (urlfix + '_multiple/wind_speed')
    chart = ('min: 0, minPadding: 10,')
    var = ('m/s')
    navws = ('active')
    return render_template('json_graph.html', navws=navws, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/air_pressure')
def air_pressure():
    title = ('air pressure')
    liveurl = (urlfix + '_livedata/air_pressure')
    url = (urlfix + '_multiple/air_pressure')
    chart = ('minRange: 15,')
    var = ('hPa')
    navap = ('active')
    return render_template('json_graph.html', navap=navap, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/irradiance_ghi')
def smp10():
    title = ('irradiance (GHI)')
    liveurl = (urlfix + '_livedata/smp10')
    url = (urlfix + '_multiple/smp10')
    chart = ('min: -5, minPadding: 10,')
    var = ('W/m^2')
    navghi = ('active')
    return render_template('json_graph.html', navghi=navghi, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/irradiance_par')
def pqsl():
    title = ('irradiance (PAR)')
    liveurl = (urlfix + '_livedata/pqsl')
    url = (urlfix + '_multiple/pqsl')
    chart = ('minRange: 15,')
    var = ('µmol/(s*m^2)')
    navpar = ('active')
    return render_template('json_graph.html', navpar=navpar, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/soil_moisture')
def soil_moisture():
    title = ('soil moisture')
    liveurl = (urlfix + '_livedata/soil_moisture')
    url = (urlfix + '_multiple/soil_moisture')
    chart = ('minRange: 15,')
    var = ('%')
    navsm = ('active')
    return render_template('json_graph.html', navsm=navsm, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/soil_tempblue')
def soil_tempblue():
    title = ('soil temperature')
    liveurl = (urlfix + '_livedata/soil_tempblue')
    url = (urlfix + '_multiple/soil_tempblue')
    chart = ('minRange: 10,')
    var = ('°C')
    navst = ('active')
    return render_template('json_graph.html', navst=navst, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/precipitation')
def precipitaion():
    title = ('precipitation')
    liveurl = (urlfix + '_livedata/precipitation')
    url = (urlfix + '_multiple/precipitation')
    chart = ('min: 0, minPadding: 10,')
    var = ('mm')
    navpre = ('active')
    return render_template('json_graph.html', navpre=navpre, liveurl=liveurl, url=url, chart=chart, var=var, title=title)


@app.route('/json')                                                             ##route to json page
def select_json():
    url = urlfix
    navjsn = ('active')
    return render_template('json.html', navjsn=navjsn, url=url)


@app.route('/_livedata/<sensor>', methods=['GET'])                              ##livedata for graph
def livedata(sensor):
    sqls = create_sql_dat(sensor, 1)
    temp = read_db_sql(sqls)
    sqlt = create_sql_dat("extract(epoch from created_at)", 1)                  ##create sql with requested sensor and time in eopch
    time = read_db_sql(sqlt)                                                    ##get data from database
    temp1 = temp[0]
    temp2 = temp1[0]
    time1 = (time[0])
    time2 = time1[0]
    time3 = round(time2)
    time4 = time3*1000                                                          ##format data for javascript
    result = [time4,temp2]
    return jsonify(result)                                                      ##return data to website for ajax


@app.route('/_multiple/<sensor>', methods=['GET'])                              ##get data from database for graph
def mult(sensor):
    li = []
    li2 = []
    li3 = []
    sql1 = "distinct on (date_trunc('hour', created_at)) " +sensor+ ", extract(epoch from created_at)"
    sql2 = "order by date_trunc('hour', created_at) desc limit 48;"
    sqlt = create_sql_req(sql1, sql2)                                           ##creeate sql to get one value of requested sensors per hour for the last 48 hours
    time = read_db_sql(sqlt)
    for i in time:
        li.append(i[0])
        li2.append(i[1])

    for i in range(len(li2)):
        li3.append(round(int(li2[i]))*1000)                                     ##format data for javascript

    return jsonify(list(zip(li3, li)))


@app.route('/_json', methods=['GET'])                                           ##route to provide raw json data for user
def dictdate2():
    var = "wind_speed, wind_direction, air_temperature, air_relhumidity, smp10, pqsl, soil_moisture, soil_tempblue, soil_tempred, air_pressure, precipitation, created_at"

    sq = ''
    freq = request.args.get('freq')                                             ##get user requests for date and frequency
    date = request.args.get('date')
    home = request.args.get('_home')                                            ##request for data displayed on homepage

    if date:
        if ":" in date:                                                         ##check if one or two dates are provided
            ls=date.split(":")
            fromd=create_dateform_req(ls[0])
            till=create_dateform_req(ls[1])                                     ##if two dates are provided: split and format each one for sql query
            try:
                if freq == 'hourly':                                                            ##check requested frequency
                    var1 = "distinct on (date_trunc('hour', created_at)) " + var
                    date1="where created_at between symmetric '" +fromd+ "' and '" +till+ "' order by date_trunc('hour', created_at), created_at"
                elif freq == 'all' or freq == None:
                    var1 = var
                    date1="where created_at between symmetric '" +fromd+ "' and '" +till+ "' order by created_at desc"
                    freq = "all"
                elif freq != None and freq != 'all' and freq != 'hourly':
                    return jsonify('check freq')

            except:
                return jsonify("date format error split")
            else:
                sq=create_sql_req(var1, date1)                                  ##create sql depending on provided informations

        else:
            datens=create_dateform_req(date)                                    ##if only one date is provided: format for sql query and check requested frequency
            try:
                if freq == 'hourly':
                    var1 = "distinct on (date_trunc('hour', created_at)) " + var
                    datestr = ("where created_at::date = '"+datens+"' order by date_trunc('hour', created_at), created_at")
                    # datestr = ("created_at::date = '"+datens+"' and extract(second from created_at)>=0 and extract(second from created_at)<8")
                elif freq == 'all' or freq == None:
                    var1 = var
                    datestr = ("where created_at::date = '"+datens+"' order by created_at desc")
                    freq = "all"
                elif freq != None and freq != 'all' and freq != 'hourly':
                    return jsonify("check freq")

            except:
                return jsonify("date format error")
            else:
                sq=create_sql_req(var1, datestr)                                ##create sql depending on provided informations

    else:
        var1 = var
        date1 = "order by created_at desc limit 1;"
        sq=create_sql_req(var1, date1)                                          ##if no date is provided: create sql to get latest data on database

    lis1=[]
    lis2=[]
    lis3=[]
    lis4=[]
    lis5=[]
    lis6=[]
    lis7=[]
    lis8=[]
    lis9=[]
    lis10=[]
    lis11=[]
    lidate=[]
    data1=read_db_sql(sq)                                                       ##send previously created sql to database and read response
    data=list(reversed(data1))
    sensordata_dic.clear()
    datadict.clear()

    for i in data:                                                              ##sort data from database
        lis1.append(i[0])
        lis2.append(i[1])
        lis3.append(i[2])
        lis4.append(i[3])
        lis5.append(i[4])
        lis6.append(i[5])
        lis7.append(i[6])
        lis8.append(i[7])
        lis9.append(i[8])
        lis10.append(i[9])
        lis11.append(i[10])
        # lis11.append(i[11])
        # tl = dt.strftime(i[11], "%y%m%d%H%M%S")
        # ti = dt.strptime(tl, "%y%m%d%H%M%S")
        # lidate.append(str(ti))

        lidate.append(str(i[11]))

       # lidate.append(round(i[11].timestamp()))   ##time in epoch


    for i in range(len(lis1)):                                                  ##insert data into dictionary
        datadict["ws"]=lis1[i]
        datadict["wd"]=lis2[i]
        datadict["at"]=lis3[i]
        datadict["ar"]=lis4[i]
        datadict["smp10"]=lis5[i]
        datadict["pqsl"]=lis6[i]
        datadict["sm"]=lis7[i]
        datadict["stb"]=lis8[i]
        datadict["str"]=lis9[i]
        datadict["ap"]=lis10[i]
        datadict["pre"]=lis11[i]
        sensordata_dic[lidate[i]] = datadict.copy()

    if not sensordata_dic:
        return jsonify("no data found")                                         ##return error if there is no data for requested date

    units = {
    "wind speed": "m/s",
    "wind direction": "degrees",
    "airtemp": "Celsius",
    "humidity": "%",
    "irradiance (GHI)": "W/m^2",
    "irradiance (PAR)": "µmol/(s*m^2)",
    "soil moisture": "%",
    "soil_tempblue???": "C",
    "soil_tempred???": "C",
    "air_pressure": "hPa",
    "precipitaion": "mm",
    }

    jsondict = {
    "timezone": "UTC",
    "frequency": freq,
    "location": "Kamp-Lintfort",
    "units": units,
    "main": "0"
    }

    if home == 'home':
        return jsonify(datadict)                                                ##return requested data for homepage

    jsondict["main"] = sensordata_dic.copy()
    return jsonify(jsondict)                                                    ##return json data to website



@app.route('/_error')                                                           ##route if database error occurs
def error():
    return render_template('db_error.html')


@app.errorhandler(404)                                                          ##route if requested page not found
def page_not_found(e):
   return render_template('404.html'), 404



def create_dateform_req(date):                                                  ##function to format date into right format for sql query
    dateform={"y":"%y",
        "m":"%y%m",
        "d":"%y%m%d"
              }
    if len(date)==6:
           dform=dateform["d"]
    elif len(date)==4:
           dform=dateform["m"]
    elif len(date)==2:
           dfomr=dateform["y"]
    else:
           logging.info(date)
    try:
           daform=dt.strptime(date, dform)
           dform=dt.strftime(daform, "%Y%m%d")
    except:
           logging.info("split_datetime format error")
    else:
           return(dform)


def create_sql_req(sensor, date3):                                              ##sql template
    sql = "select {} from sensordata {};".format(sensor, date3)
    return(sql)

def create_sql_dat(sensor, limit):                                              ##sql template
    sql = "select {} from sensordata order by created_at desc limit {};".format(sensor, limit)
    return(sql)

def read_db_sql(query):                                                         ##read data from datebase
        sql = query
        conn = None
        dt1 = []
        try:
            conn = psycopg2.connect(user = "pi",
                                    password = "********",
                                    host = "10.180.12.123",
                                    port = "5432",
                                    database = "test")
            cursor = conn.cursor()                                              ##connect to database
            cursor.execute(sql)                                                 ##execute sql query
            dt1 = cursor.fetchall()
            conn.commit()
            cursor.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logging.info(error)
        finally:
            if conn is not None:
                conn.close()
            return dt1                                                          ##return data to function


if __name__ == "__main__":
    app.run(host='0.0.0.0')                                                     ##run flask app
