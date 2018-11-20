import sys
import os
import numpy
import boto3
from boto3.s3.transfer import TransferConfig
import random
import string
import time
import multiprocessing
import datetime


class S3Benchmark:
    def __init__(self, bucket_name, max_concurrency=10, max_io_queue=100, random_data=True, clean=True, debug=False):
        self.bucket_name = bucket_name
        self.local_tmp_file_list = []
        self.s3_tmp_file_list = []
        self.transfer_config = TransferConfig(max_concurrency=max_concurrency, max_io_queue=max_io_queue)
        self.random_data = random_data
        self.clean = clean
        self.debug = debug

    def _generate_random_str(self, num):
        random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(num)])
        return random_str
    
    def _generate_dummy_file(self, filename, megabyte, random_data=True):
        with open(filename, 'wb') as file:
            for i in range(10):
                if random_data:
                    file.write(numpy.random.bytes(megabyte * 1000 * 100))
                else:
                    file.write(numpy.zeros(megabyte * 1000 * 100 / 8))
        
    def _measure_upload_speed(self, file_name):
        s3 = boto3.client('s3')
        start = time.time()
        s3.upload_file(file_name, self.bucket_name, file_name, Config=self.transfer_config)
        process_time = time.time() - start
        return process_time

    def _measure_download_speed(self, file_name):
        s3 = boto3.client('s3')
        start = time.time()
        s3.download_file(self.bucket_name, file_name, 'down_' + file_name, Config=self.transfer_config)
        process_time = time.time() - start
        return process_time
        
    def _print_result(self, upload_speed, upload_time, download_speed, download_time):
        print(' * Upload    %.2f Mbps (%.4f [sec])' % (upload_speed, upload_time))
        print(' * Download  %.2f Mbps (%.4f [sec])' % (download_speed, download_time))
        
    def run(self, file_size_mb):
        if self.debug:
            print('Testing %d MB:' % file_size_mb)

        local_file_name = self._generate_random_str(8) + '_%dmb.tmp' % file_size_mb
        self.local_tmp_file_list.append(local_file_name)

        # if not os.path.exists(filename):
        self._generate_dummy_file(local_file_name, file_size_mb, random_data=self.random_data)

        upload_time = self._measure_upload_speed(local_file_name)
        download_time = self._measure_download_speed(local_file_name)

        if self.debug:
            self._print_result(file_size_mb / upload_time * 8, upload_time, file_size_mb / download_time * 8, download_time)

        if self.clean:
            self._clean()

        return upload_time, download_time

    def multi_run(self, num_threads, file_size_mb):
        if self.debug:
            print('Testing %d MB x %d Process:' % (file_size_mb, num_threads))

        random_str = self._generate_random_str(8)
        for i in range(num_threads):
            local_file_name = random_str + ('_%d_%dmb.tmp' % (i, file_size_mb))
            self.local_tmp_file_list.append(local_file_name)
            self.s3_tmp_file_list.append(local_file_name)
            self._generate_dummy_file(local_file_name, file_size_mb, random_data=self.random_data)

        pool = multiprocessing.Pool(num_threads)
        start = time.time()
        pool.map(self._measure_upload_speed, self.local_tmp_file_list)
        upload_time = time.time() - start
        pool.close()
        
        pool = multiprocessing.Pool(num_threads)
        start = time.time()
        pool.map(self._measure_download_speed, self.local_tmp_file_list)
        download_time = time.time() - start
        pool.close()
        
        if self.debug:
            self._print_result(file_size_mb * num_threads / upload_time * 8, upload_time, file_size_mb * num_threads  / download_time * 8, download_time)

        if self.clean:
            self._clean()

        return upload_time, download_time

    def _clean(self):
        s3 = boto3.client('s3')
        for tmp_file in self.local_tmp_file_list:
            os.remove(tmp_file)
            os.remove('down_' + tmp_file)
        
        for tmp_file in self.s3_tmp_file_list:
            s3.delete_object(Bucket=self.bucket_name, Key=tmp_file)

        self.local_tmp_file_list = []
        self.s3_tmp_file_list = []

