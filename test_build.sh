source .env && make install && echo $DATABASE_URL && psql -a -d $DATABASE_URL -f database.sql
