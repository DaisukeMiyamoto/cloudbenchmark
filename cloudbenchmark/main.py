import sys
import datetime
import argparse
from tqdm import tqdm
import s3benchmark
import benchmarkrecorder


def s3_throughput(s3_bucket_name, trial=1, filesize_list=[32, 64], max_concurrency_list=[10], max_io_queue_list=[1000], num_process_list=[1], random_data=True):
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
    for max_concurrency in max_concurrency_list:
        for max_io_queue in max_io_queue_list:
            for num_process in num_process_list:
                for filesize in filesize_list:
                    for i in range(trial):
                        condition = {
                            'trial': trial,
                            'file_size': filesize,
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
            random_data=condition['random_data']
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
                filesize * num_process / upload_time * 8,
                filesize * num_process  / download_time * 8,
            ]
        )

    return recorder
    
    
def main():
    print('Cloud Benchmark')
    job_list = ['s3-throughput-small', 's3-throughput-large']

    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-j', '--job', dest='job', choices=job_list, help='job type', required=True)
    parser.add_argument('-b', '--bucket', dest='bucket', help='S3 bucket to store result files')
    parser.add_argument('--target-s3', dest='target_s3', help='S3 bucket for benchmark target')
    args = parser.parse_args()

    if args.job == 's3-throughput-small':
        if args.target_s3:
            result = s3_throughput(args.target_s3)
            print(result.df)
            if args.bucket:
                result.upload_to_s3('result.tmp', args.bucket, args.job + '/' + str(datetime.date.today()) + '.csv', file_type='csv')
        else:
            print('Error: use --target-s3 option')
            return False
            
    elif args.job == 's3-throughput-large':
        if args.target_s3:
            result = s3_throughput(
                args.target_s3,
                trial=3,
                filesize_list=[32, 64, 128, 256, 512, 1024, 2048, 4096],
                max_concurrency_list=[10, 100],
                max_io_queue_list=[1000, 10000],
                num_process_list = [1, 2, 4, 8, 16, 32]
            )
            print(result.df)
            if args.bucket:
                result.upload_to_s3('result.tmp', args.bucket, args.job + '/' + str(datetime.date.today()) + '.csv', file_type='csv')
        else:
            print('Error: use --target-s3 option')
            return False
    
    else:
        print('Error: invalid job')
        return False
        
    
if __name__=='__main__':
    main()
