from flask import render_template, jsonify, request
from app import app
import psycopg2
import json
from datetime import datetime as dt

DEC2FLOAT = psycopg2.extensions.new_type(
            psycopg2.extensions.DECIMAL.values,
            'DEC2FLOAT',
            lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

sensors = ["wind_speed", "wind_direction", "air_temperature", "air_relhumidity", "smp10", "pqsl", "soil_moisture", "soil_tempblue", "soil_tempred", "air_pressure", "precipitation"]
sensordata_dic = {}
datadict = {}
urlfix = 'http://10.180.12.123:5000/'



@app.route('/index')
def index():
    title1 = ('home')
    navhome = ('active')
    liveurl = ('livedata/air_temperature')
    return render_template('index_2.html',liveurl=liveurl, navhome=navhome, title1=title1)

@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    liveurl = (urlfix + '_json?_home=home')
    url = urlfix
    return render_template('home.html', url=url, liveurl=liveurl)


@app.route('/temperature')
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


@app.route('/json')
def select_json():
    url = urlfix
    navjsn = ('active')
    return render_template('json.html', navjsn=navjsn, url=url)


@app.route('/_livedata/<sensor>', methods=['GET'])
def livedata(sensor):
    sqls = create_sql_dat(sensor, 1)
    temp = read_db_sql(sqls)
    sqlt = create_sql_dat("extract(epoch from created_at)", 1)
    time = read_db_sql(sqlt)
    temp1 = temp[0]
    temp2 = temp1[0]
    time1 = (time[0])
    time2 = time1[0]
    time3 = round(time2)
    time4 = time3*1000
    result = [time4,temp2]
    print("livedata: ", result)
    return jsonify(result)


@app.route('/_multiple/<sensor>', methods=['GET'])
def mult(sensor):
    # print(values)
    li = []
    li2 = []
    li3 = []
    sql1 = "distinct on (date_trunc('hour', created_at)) " +sensor+ ", extract(epoch from created_at)"
    sql2 = "order by date_trunc('hour', created_at) desc limit 48;"

    sqlt = create_sql_req(sql1, sql2)
    print(sqlt)
    time = read_db_sql(sqlt)
    print(time)
    for i in time:
        li.append(i[0])
        li2.append(i[1])
    print("li:")
    print(li)
    print("li2")
    print(li2)
    for i in range(len(li2)):
        li3.append(round(int(li2[i]))*1000)


    #print("li3: ")
    #print(li3)

    #timer = list(reversed(time))
    #sqls = create_sql_dat(sensor, 30)
    #temp = read_db_sql(sqls)
    #temps = list(reversed(temp))

    #for data in temps:
        #li2.append(data[0])
    # print("li2= ")
    # print(li2)
    #for data in timer:
        #li.append(round(data[0])*1000)
    # print("li= ")
    # print(li)

    return jsonify(list(zip(li3, li)))


@app.route('/_json', methods=['GET'])
def dictdate2():
    # var2 = sensor
    # var="wind_speed, air_temperature, air_relhumidity, wind_direction"
    var = "wind_speed, wind_direction, air_temperature, air_relhumidity, smp10, pqsl, soil_moisture, soil_tempblue, soil_tempred, air_pressure, precipitation, created_at"

    sq = ''
    freq = request.args.get('freq')
    date = request.args.get('date')
    home = request.args.get('_home')

    if date:
        if ":" in date:
            ls=date.split(":")
            fromd=create_dateform_req(ls[0])
            till=create_dateform_req(ls[1])
            try:
                if freq == 'hourly':
                    var1 = "distinct on (date_trunc('hour', created_at)) " + var
                    date1="where created_at between symmetric '" +fromd+ "' and '" +till+ "' order by date_trunc('hour', created_at), created_at"
                    # date2="' and '"+till+"' order by date_trunc('hour', created_at), created_at"
                elif freq == 'all' or freq == None:
                    var1 = var
                    date1="where created_at between symmetric '" +fromd+ "' and '" +till+ "' order by created_at desc"
                    # date2="' and '"+till+"' order by created_at desc"
                    freq = "all"
                elif freq != None and freq != 'all' and freq != 'hourly':
                    return jsonify('check freq')
                    # date3=date1+date2

            except:
                return jsonify("date format error split")
            else:
                sq=create_sql_req(var1, date1)

        else:
            datens=create_dateform_req(date)
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
                sq=create_sql_req(var1, datestr)

    else:
        var1 = var
        date1 = "order by created_at desc limit 1;"
        sq=create_sql_req(var1, date1)

    # print("sq: ")
    # print(sq)
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
    data1=read_db_sql(sq)
    data=list(reversed(data1))
    sensordata_dic.clear()
    datadict.clear()

    print("len data: ")
    print(len(data))
    for i in data:
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


    for i in range(len(lis1)):
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
        return jsonify("no data found")

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
        return jsonify(datadict)

    jsondict["main"] = sensordata_dic.copy()
    return jsonify(jsondict)



@app.route('/_error')
def error():
    return render_template('db_error.html')


@app.errorhandler(404)
def page_not_found(e):
   return render_template('404.html'), 404



def create_dateform_req(date):
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
           print(date)
##           return ("check date format_split")
    try:
           daform=dt.strptime(date, dform)
           dform=dt.strftime(daform, "%Y%m%d")
    except:
           print("split_datetime format error")
##           return jsonify("check date format_split")
    else:
           return(dform)


def create_sql_req(sensor, date3):
##    yearsql="extract(year from created_at)={}".format(year)

    sql = "select {} from sensordata {};".format(sensor, date3)
    return(sql)

def create_sql_dat(sensor, limit):
    sql = "select {} from sensordata order by created_at desc limit {};".format(sensor, limit)
    return(sql)

def read_db_sql(query):
        sql = query
        print("sql: ")
        print(sql)
        conn = None
        dt1 = []

        try:
            conn = psycopg2.connect(user = "pi",
                                    password = "pwd123",
                                    host = "10.180.12.123",
                                    port = "5432",
                                    database = "test")
            cursor = conn.cursor()
            cursor.execute(sql)
            dt1 = cursor.fetchall()
            conn.commit()
            cursor.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            return dt1
