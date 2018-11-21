import sys
import datetime
import argparse
import json
from tqdm import tqdm
import itertools
# import intertools
# from cloudbenchmark import s3benchmark
# from cloudbenchmark import benchmarkrecorder
import s3benchmark
import benchmarkrecorder


def s3_throughput(s3_bucket_name, condition_pattern, clean=True, debug=False):
    recorder = benchmarkrecorder.BenchmarkRecorder([
        'trial',
        'file_size',
        'max_concurrency',
        'max_io_queue',
        'random_data',
        'num_process',
        'upload_time_sec',
        'download_time_sec',
        'upload_speed_mbps',
        'download_speed_mbps',
    ])

    condition_list = []
    for max_concurrency in condition_pattern['max_concurrency']:
        for max_io_queue in condition_pattern['max_io_queue']:
            for random_data in condition_pattern['random_data']:
                for num_process in condition_pattern['num_process']:
                    for file_size in condition_pattern['file_size']:
                        for i in condition_pattern['trial']:
                            condition = {
                                'trial': i,
                                'file_size': file_size,
                                'max_concurrency': max_concurrency,
                                'max_io_queue': max_io_queue,
                                'random_data': random_data,
                                'num_process': num_process,
                            }
                            condition_list.append(condition)

    for condition in tqdm(condition_list):                    
        s3bench = s3benchmark.S3Benchmark(s3_bucket_name,
            max_concurrency=condition['max_concurrency'],
            max_io_queue=condition['max_io_queue'],
            random_data=condition['random_data'],
            clean=clean,
            debug=debug
        )
        
        upload_time, download_time = s3bench.multi_run(
            condition['num_process'], 
            condition['file_size']
        )

        recorder.add_record([
                condition['trial'],
                condition['file_size'],
                condition['max_concurrency'],
                condition['max_io_queue'],
                condition['random_data'],
                condition['num_process'],
                upload_time,
                download_time,
                condition['file_size'] * condition['num_process'] / upload_time * 8,
                condition['file_size'] * condition['num_process'] / download_time * 8,
            ]
        )

    return recorder
    
    
def main():
    print('Cloud Benchmark')
    job_list = ['s3-throughput-small', 's3-throughput-large']

    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-j', '--job', dest='job', choices=job_list, help='job type', required=True)
    parser.add_argument('-b', '--bucket', dest='bucket', help='S3 bucket to store result files')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='show debug info')
    parser.add_argument('-n', '--name', dest='name', default=str(datetime.date.today()), help='job name')
    parser.add_argument('--target-s3', dest='target_s3', help='S3 bucket for benchmark target')
    args = parser.parse_args()
    if 's3-' in args.job:
        if not args.target_s3:
            print('Error: use --target-s3 option')
            return False

    print('[%s]' % args.job)
    if 's3-throughput-' in args.job:
        if 's3-throughput-small' in args.job:
            condition_pattern = {
                'trial': [0],
                'file_size': [64, 256, 1024],
                'max_concurrency': [10],
                'max_io_queue': [1000],
                'num_process': [1],
                'random_data': [True],
            }
        elif 's3-throughput-large' in args.job:
            condition_pattern = {
                'trial': [0, 1, 2],
                'file_size': [32, 64, 128, 256, 512, 1024, 2048, 4096],
                'max_concurrency': [10, 100],
                'max_io_queue': [1000, 10000],
                'num_process': [1, 2, 4, 8, 16, 32],
                'random_data': [True],
            }
        else:
            print('Error: invalid job size')
            return False

        result = s3_throughput(args.target_s3, condition_pattern, debug=args.debug)
        print(result.df)
        if args.bucket:
            result.upload_to_s3('result.tmp', args.bucket, args.job + '/' + args.name + '.csv', file_type='csv')

    else:
        print('Error: invalid job')
        return False
        
    
if __name__=='__main__':
    main()
