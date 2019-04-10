import psycopg2
import time
import serial
from datetime import datetime as dt
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s", handlers=[logging.FileHandler("combi.log"), logging.StreamHandler()])
ser = serial.Serial('/dev/ttyACM0', baudrate=19200, timeout=1)
data = []
timer = 0



def insert_values(column, value):
        table = "sensordata"
        sql = "INSERT INTO {} ({}) VALUES ({});".format(table, column, value)
        conn = None
        try:
            conn = psycopg2.connect(user = "pi",
                                    password = "pwd123",
                                    host = "10.180.12.123",
                                    port = "5432",
                                    database = "test")
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.info(error)
            f = open("not_uploaded.txt", "a")
            f.write(value+'\n')
            f.close
        finally:
            if conn is not None:
                conn.close()


def readser():
    eol = b'\r'
    leneol = len(eol)
    line = bytearray()
    while True:
        c = ser.read(1)
        if c:
            line += c
            if line[-leneol:] == eol:
                break
        else:
            break
    return bytes(line)


def readdata(req):
    ser.write(req)
    res=readser()
    tmp=res.decode()
    return tmp[1:-1]


def sync_time():
    t=dt.now()
    tl = dt.strftime(t, "%y%m%d%H%M%S")
    time_str = '$01G'+tl+'\r'
    time_bytes = time_str.encode('utf-8')
    set_time = readdata(time_bytes)
    logging.info('time set to:')
    logging.info(tl)


def channel():
    global timer
    data.clear()
    wind_speed = readdata(b'$01R01\r')
    wind_direction = readdata(b'$01R02\r')
    air_temperature = readdata(b'$01R03\r')
    air_relhumidity = readdata(b'$01R04\r')
    smp10 = readdata(b'$01R05\r')
    pqsl = readdata(b'$01R06\r')
    soil_moisture = readdata(b'$01R07\r')
    soil_tempblue = readdata(b'$01R08\r')
    soil_tempred = readdata(b'$01R09\r')
    air_pressure = readdata(b'$01R0A\r')
    precipitation = readdata(b'$01R0B\r')
    readtime = readdata(b'$01H\r')

    time = dt.strptime(readtime, "%d%m%y%H%M%S")
    str_time = dt.strftime(time,  "%d%m%y %H%M%S")

    data.append(wind_speed)
    data.append(wind_direction)
    data.append(air_temperature)
    data.append(air_relhumidity)
    data.append(smp10)
    data.append(pqsl)
    data.append(soil_moisture)
    data.append(soil_tempblue)
    data.append(soil_tempred)
    data.append(air_pressure)
    data.append(precipitation)
    data.append(str_time)

    col = "wind_speed, wind_direction, air_temperature, air_relhumidity, smp10, pqsl, soil_moisture, soil_tempblue, soil_tempred, air_pressure, precipitation, created_at"
    val = str(data)[1:-1]
    logging.info(val)
    insert_values(col, val)
    timer += 1


while True:
    try:
        channel()
        if timer == 8600:
            sync_time()
            timer = 0
    except:
        logging.info("error funct. channel")
        time.sleep(50)
    finally:
        time.sleep(10)
