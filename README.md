# weatherstation

Logger: python script to get data from a Theodor Friedrichs Combilog datalogger and send it to a local postgresql database.

Server: flask app to host a website that displays the data from the logger. It also provides access to raw json data from the postgresql database. Highcharts is used to visualize the data (https://www.highcharts.com/).
