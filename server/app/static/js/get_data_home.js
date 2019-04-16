
function requesthomeData() {    //get latest data from server
  $.ajax({
      url: url,
      success: function(point) {

          var obj = point;                                                      //assign names and units to data
          console.log(point);
          wind_speed="wind speed: "+obj.ws+"m/s";
          temp="temperature: "+obj.at+"°C";
          wind_direction="wind direction: "+obj.wd+"°";
          air_relhumidity="humidity: "+obj.ar+"%";
          air_pressure="air pressure: "+obj.ap+"hPa"
          smp10="irradiance (GHI): "+obj.smp10+"W/m^2";
          pqsl = "irradiance (PAR): "+obj.pqsl+"µmol/(s*m^2)";
          soil_moisture = "soil moisture: "+obj.sm+"%";
          soil_tempblue = "soil temperature: "+obj.stb+"°C";
          precipitation = "precipitation: "+obj.pre+"mm";


          // console.log(typeof(air_relhumidty))
          document.getElementById("air_temperature").innerText = (temp);              //display data on homepage
          document.getElementById("air_relhumidity").innerText = (air_relhumidity);
          document.getElementById("wind_speed").innerText = (wind_speed);
          document.getElementById("wind_direction").innerText = (wind_direction);
          document.getElementById("air_pressure").innerText = (air_pressure);
          document.getElementById("smp10").innerText = (smp10);
          document.getElementById("pqsl").innerText = (pqsl);
          document.getElementById("soil_moisture").innerText = (soil_moisture);
          document.getElementById("soil_tempblue").innerText = (soil_tempblue);
          document.getElementById("precipitation").innerText = (precipitation);




      },
      error: function(){
        console.log('failure');
    },
  });
}
var url;
requesthomeData();
