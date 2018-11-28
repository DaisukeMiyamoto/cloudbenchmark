import sys
import os
import boto3
import pandas as pd
import requests
import datetime


class BenchmarkRecorder:
    def __init__(self, col_names, add_metadata=True):
        metadata_col_names = ['instance_type', 'availability-zone', 'version', 'date', 'datetime']
        self.add_metadata = add_metadata
        self.col_names = list(col_names)
        if add_metadata:
            self.col_names.extend(metadata_col_names)

        self.df = pd.DataFrame(columns=self.col_names)

    def _get_metadata(self, key):
        response = requests.get('http://169.254.169.254/latest/meta-data/' + key)
        return response.text
        
    def _get_metadata_record(self):
        metadata = [
            self._get_metadata('instance-type'),
            self._get_metadata('placement/availability-zone'),
            '2018-11-20',
            str(datetime.date.today()),
            str(datetime.datetime.now())
        ]
        return metadata
        
    def add_record(self, record):
        if self.add_metadata:
            record.extend(self._get_metadata_record())

        s = pd.Series(record, index=self.col_names)
        self.df = self.df.append(s, ignore_index=True)

    def write(self, filename, file_type='csv'):
        if file_type == 'csv':
            self.df.to_csv(filename)
        elif file_type == 'json':
            self.df.to_json(filename)
        else:
            print('Error: wrong output type')

    def upload_to_s3(self, tmp_filename, bucket_name, key_name, file_type='csv'):
        self.write(tmp_filename, file_type)
        s3 = boto3.client('s3')
        s3.upload_file(tmp_filename, bucket_name, key_name)
        print('Results uploaded to s3://%s/%s' % (bucket_name, key_name))

