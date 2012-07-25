ssh bingo "sudo su - postgres -c 'dropdb qbuilder ; createdb -O auto qbuilder'"
psql -h bingo -U auto -d qbuilder -f database.sql
