# weatherstation

Datalogger and server for collecting data from a weatherstation.

Logger: 
A raspberry pi is used to get data from a Theodor Friedrichs Combilog datalogger.
It is connected to the serial port of the combilog and communicates via ascii telegrams.
After collecting, the data is sent to a local postgresql database.

Server: 
A second raspberry pi is set up as a server, hosting the postgresql database and a flask web application. 
The web apllication is used to display the data from the logger and to provide raw json data. 
Highcharts is used to visualize the data (https://www.highcharts.com/).


Please visit the Wiki for more detailled information.
