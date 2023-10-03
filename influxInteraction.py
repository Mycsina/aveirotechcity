import influxdb_client
from dotenv import load_dotenv
from influxdb_client.client.flux_table import TableList
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()


def unpack(results: TableList, fields="_value"):
    for table in results:
        for record in table.records:
            yield record.values[fields]


class InfluxSession:
    def __init__(self, bucket, org, token, url):
        self.bucket = bucket
        self.org = org
        self.token = token
        self.url = url
        self.client = influxdb_client.InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write(self, df, measurement, tag_columns):
        self.write_api.write(bucket=self.bucket, org=self.org, record=df, data_frame_measurement_name=measurement,
                             data_frame_tag_columns=tag_columns)

    def query(self, query):
        return self.query_api.query(query=query)

