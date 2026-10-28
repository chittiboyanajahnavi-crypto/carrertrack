FROM mysql:8.0

# Initialize the hosted demo schema and sample rows once on a fresh MySQL data volume.
COPY 02_schema.sql /docker-entrypoint-initdb.d/01-schema.sql
COPY 03_seed_data.sql /docker-entrypoint-initdb.d/02-seed-data.sql