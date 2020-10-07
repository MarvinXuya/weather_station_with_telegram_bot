CREATE TABLE botdata (
  date_time DATETIME NOT NULL PRIMARY KEY,
  humedad FLOAT,
  presion FLOAT,
  temperatura FLOAT);


ALTER TABLE botdata
    ADD temperatura_DS18B20 FLOAT
      AFTER temperatura;
