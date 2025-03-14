CREATE DATABASE IF NOT EXISTS volumetria DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- Todos os deltas estão em segundos

USE volumetria;

-- Sensores Milesight

-- topic v3/espm/devices/temperature01/up
-- { "end_device_ids": { "device_id": "temperature01" }, "uplink_message": { "rx_metadata": [{ "timestamp": 2040934975 }], "decoded_payload": { "humidity": 82, "temperature": 23.4 } } }
CREATE TABLE temperatura (
  id bigint NOT NULL AUTO_INCREMENT,
  data datetime NOT NULL,
  id_sensor tinyint NOT NULL,
  delta int NOT NULL,
  umidade float NOT NULL,
  temperatura float NOT NULL,
  PRIMARY KEY (id),
  KEY temperatura_data_id_sensor (data, id_sensor),
  KEY temperatura_id_sensor (id_sensor)
);

-- topic v3/espm/devices/passage01/up
-- topic v3/espm/devices/passage02/up
-- { "end_device_ids": { "device_id": "passage01" }, "uplink_message": { "rx_metadata": [{ "timestamp": 2040934975 }], "decoded_payload": { "battery": 0, "period_in": 0, "period_out": 0 } } }
CREATE TABLE passagem (
  id bigint NOT NULL AUTO_INCREMENT,
  data datetime NOT NULL,
  id_sensor tinyint NOT NULL,
  delta int NOT NULL,
  bateria tinyint NOT NULL,
  entrada int NOT NULL,
  saida int NOT NULL,
  PRIMARY KEY (id),
  KEY passagem_data_id_sensor (data, id_sensor),
  KEY passagem_id_sensor (id_sensor)
);

-- Query de consolidação por aula
select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida from passagem where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59' and weekday(data) in (2, 3) and time(data) between '08:00:00' and '10:00:00' and id_sensor = 2 group by dia;

-- https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html
