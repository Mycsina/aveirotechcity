poetry install
docker run -d --name influx -p 8086:8086 -v $PWD/influxdb:/var/lib/influxdb influxdb
docker exec -it influx influx setup -b "sensor" -o "hack" -u "mycsina" -p "test1234" -r 0 -f -t "eb2kn5YQql-0vgBZkaoMEBGEemvVxRjQ-fv98RX5Og3ikY2p84BEpCgWVf4kn1OY5o1YbEU5cHM7zLJKNiuX1A=="
poetry run python data_insertion.py
poetry run flask run