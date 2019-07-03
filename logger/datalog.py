import psycopg2
import time
import serial
import threading
import schedule
from datetime import datetime as dt
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s", handlers=[logging.FileHandler("combi.log")])  #logger (streamhandler: ,logging.StreamHandler())
ser = serial.Serial('/dev/ttyACM0', baudrate=19200, timeout=1)      #serial configuration
data = []
# timer = 0
state = 1



def insert_values(value):
        table = "sensordata"
        column = "wind_speed, wind_direction, air_temperature, air_relhumidity, smp10, pqsl, soil_moisture, soil_tempblue, soil_tempred, air_pressure, precipitation, created_at"
        sql = "INSERT INTO {} ({}) VALUES ({});".format(table, column, value)       #sql query including columns and data
        conn = None
        try:
            conn = psycopg2.connect(user = "pi",
                                    password = "********",
                                    host = "10.180.12.123",
                                    port = "5432",
                                    database = "test")
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.info(error)
            f = open("not_uploaded.txt", "a")       #save data to file in case an error occurs and data cannot be uploaded to database
            f.write(value+'\n')
            f.close
            global state
            state = 0
        finally:
            if conn is not None:
                conn.close()


def readser():          #reading serial response from datalogger after sending ascii telegram
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
    ser.write(req)      #send telegram to datalogger
    res=readser()
    tmp=res.decode()
    return tmp[1:-1]        #return formatted response


def sync_time():
    t=dt.now()
    tl = dt.strftime(t, "%y%m%d%H%M%S")
    time_str = '$01G'+tl+'\r'
    time_bytes = time_str.encode('utf-8')
    set_time = readdata(time_bytes)         #format time and synchronize with datalogger
    logging.info('time set to:')
    logging.info(tl)


def channel():
    # global timer
    data.clear()
    wind_speed = readdata(b'$01R01\r')          #ascii telegram for each sensor on datalogger
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

    time = dt.strptime(readtime, "%d%m%y%H%M%S")        #format time read from datalogger
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
    data.append(str_time)           #insert sensor values into list

    # col = "wind_speed, wind_direction, air_temperature, air_relhumidity, smp10, pqsl, soil_moisture, soil_tempblue, soil_tempred, air_pressure, precipitation, created_at"          #collumns in database
    val = str(data)[1:-1]           #convert list to string and remove brackets
    logging.info(val)
    insert_values(val)         #insert values into database
    # timer += 1                      #counter for synchronizing time


def run_threaded(fkt):
    reuploading_thread = threading.Thread(target=fkt)
    reuploading_thread.start()


def reupload_data():
    sync_time()
    global state
    counter = 0
    try:
        not_uploaded = open("not_uploaded.txt", "r+")
        not_uploaded_copy = open("not_uploaded_copy.txt", "a")
        for i in not_uploaded:
            if state is not 0:
                insert_values(i)
                counter += 1
        if counter > 1:
            not_uploaded.seek(0)
            for i in not_uploaded:
                not_uploaded_copy.write(i)
            not_uploaded.seek(0)
            not_uploaded.truncate()
            logging.info("not_uploaded deleted")
        not_uploaded.close()
        not_uploaded_copy.close()
        state = 1
    except:
        logging.info("error while reuploading")
        state = 1




if __name__ == "__main__":
    schedule.every(10).seconds.do(channel)
    schedule.every().monday.do(run_threaded, reupload_data)

    while True:
        schedule.run_pending()
        time.sleep(1)
