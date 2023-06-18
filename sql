
docker run -it -d --rm -e MYSQL_ALLOW_EMPTY_PASSWORD=1 --name mysql_8 -p 3305:3306 -w /bases -v /home/mix/Desktop/bases:/bases mysql:debian

add alias "mysql" to .bashrc file
docker run -it --rm -e MYSQL_ALLOW_EMPTY_PASSWORD=1 --name mysql_8 -p 3305:3306 -w /bases -v /home/mix/Desktop/bases:/bases mysql:debian bash


CREATE DATABASE axia_branded;
CREATE USER 'axia_branded'@'*' IDENTIFIED BY '000';
GRANT GRANT ALL PRIVILEGES ON axia_branded.* TO 'axia_branded'@'*';
GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES, RELOAD on axia_branded.* TO 'axia_branded'@'*';

GRANT ALL PRIVILEGES ON *.* TO 'tolkien'@'%';


CREATE USER 'finley'@'%.example.com'
  IDENTIFIED BY 'password';
GRANT ALL
  ON *.*
  TO 'finley'@'%.example.com'
  WITH GRANT OPTION;

CREATE USER 'custom'@'host47.example.com'
  IDENTIFIED BY 'password';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP
  ON expenses.*
  TO 'custom'@'host47.example.com';

SHOW GRANTS FOR 'admin'@'localhost';


CREATE — Позволяет пользователям создавать базы данных/таблицы
SELECT — Разрешает делать выборку данных
INSERT — Право добавлять новые записи в таблицы
UPDATE — Позволяет изменять существующие записи в таблицах
DELETE — Даёт право удалять записи из таблиц
DROP — Возможность удалять записи в базе данных/таблицах

mysqldump -uprod_deloce_net -htest-wp-prod-sites.c7obndsddnto.eu-west-2.rds.amazonaws.com -p --set-gtid-purged=OFF prod_deloce_net > prod_deloce_net_dump.sql
mysql -umain -hcorp-company.mysql.database.azure.com -p prod_deloce_net < prod_deloce_net_dump.sql

mysqldump -u root -h 82.82.82.82 -p -A > all-databases.sql
mysqldump -u whd -p -c -e --single-transaction --skip-set-charset --add-drop-database -B whd > /data1/whdbackup.sql

mysqldump -u root -h 172.24.0.2 -p -B wordpress > databases.sql
mysql -u admin -h 172.24.0.2 -p wordpress < databases.sql