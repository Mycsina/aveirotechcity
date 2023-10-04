docker run -d --name influx -p 8086:8086 -v $PWD/influxdb:/var/lib/influxdb influxdb
poetry run python data_insertion.py
poetry run flask run