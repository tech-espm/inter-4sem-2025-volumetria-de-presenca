CREATE DATABASE IF NOT EXISTS volumetria DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- Todos os deltas estão em segundos

USE volumetria;

-- Sensores Milesight

-- topic v3/espm/devices/presence01/up
-- topic v3/espm/devices/presence02/up
-- topic v3/espm/devices/presence03/up
-- topic v3/espm/devices/presence04/up
-- topic v3/espm/devices/presence05/up
-- topic v3/espm/devices/presence06/up
-- topic v3/espm/devices/presence07/up
-- topic v3/espm/devices/presence08/up
-- { "end_device_ids": { "device_id": "presence01" }, "uplink_message": { "rx_metadata": [{ "timestamp": 2040934975 }], "decoded_payload": { "battery": 99, "occupancy": "vacant" } } }
CREATE TABLE presenca (
  id bigint NOT NULL,
  data datetime NOT NULL,
  id_sensor tinyint NOT NULL,
  delta int NOT NULL,
  bateria tinyint NOT NULL,
  ocupado tinyint NOT NULL,
  PRIMARY KEY (id),
  KEY presenca_data_id_sensor (data, id_sensor),
  KEY presenca_id_sensor (id_sensor)
);

-- topic v3/espm/devices/temperature01/up
-- { "end_device_ids": { "device_id": "temperature01" }, "uplink_message": { "rx_metadata": [{ "timestamp": 2040934975 }], "decoded_payload": { "humidity": 82, "temperature": 23.4 } } }
CREATE TABLE temperatura (
  id bigint NOT NULL,
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
  id bigint NOT NULL,
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

-- Query para monitorar as presenças em tempo real / colorir o digital twin
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 1 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 2 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 3 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 4 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 5 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 6 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 7 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 8 order by id desc limit 1)
;

-- Query para monitorar a umidade e a temperatura em tempo real
select umidade, temperatura from temperatura order by id desc limit 1;

-- Query para consolidar as entradas e saídas por dia por período de aula
select tmp1.dia, tmp1.total_entrada total_entrada1, tmp1.total_saida total_saida1, tmp2.total_entrada total_entrada2, tmp2.total_saida total_saida2, tmp3.total_entrada total_entrada3, tmp3.total_saida total_saida3
from (
	select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida
	from passagem
	where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59'
	and time(data) between '07:30:00' and '09:10:00'
	and id_sensor = 2 group by dia
) tmp1
inner join (
	select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida
	from passagem
	where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59'
	and time(data) between '09:30:00' and '11:10:00'
	and id_sensor = 2 group by dia
) tmp2 on tmp2.dia = tmp1.dia
inner join (
	select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida
	from passagem
	where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59'
	and time(data) between '11:20:00' and '13:00:00'
	and id_sensor = 2 group by dia
) tmp3 on tmp3.dia = tmp1.dia
;

-- https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html
