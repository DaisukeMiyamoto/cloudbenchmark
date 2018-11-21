#!/usr/bin/env python
# coding: utf-8

import sys
import datetime
import argparse
import json
from cloudbenchmark import benchmark_jobs


condition_patterns = {
    's3-throughput': {
        'small': {
            'trial': [0],
            'file_size': [64, 256, 1024],
            'max_concurrency': [10],
            'max_io_queue': [1000],
            'num_process': [1],
            'random_data': [True],
        },
        'large': {
            'trial': [0, 1, 2],
            'file_size': [32, 64, 128, 256, 512, 1024, 2048, 4096],
            'max_concurrency': [10, 100],
            'max_io_queue': [1000, 10000],
            'num_process': [1, 2, 4, 8, 16, 32],
            'random_data': [True],
        }
    },
    'ec2-sysbench-cpu': {
        'small': {
            'trial': [0],
            'num_threads': [1, 2],
        },
        'large': {
            'trial': [0, 1, 2],
            'num_threads': [1, 2, 4, 8, 16, 32],
        }        
    },
    'ec2-sysbench-memory': {
        'small': {
            'trial': [0],
            'num_threads': [1, 2],
        },
        'large': {
            'trial': [0, 1, 2],
            'num_threads': [1, 2, 4, 8, 16, 32],
        }
    }
}


def job_executer(job, size, bucket, name, options, debug=False):

    print('[%s]' % job)
    result = None
    if 's3-throughput' in job:
        result = benchmark_jobs.s3_throughput(options['target_s3'], condition_patterns[job][size], debug=debug)
    elif 'ec2-sysbench-cpu' in job:
        result = benchmark_jobs.ec2_sysbench_cpu(condition_patterns[job][size], debug=debug)
    elif 'ec2-sysbench-memory' in job:
        result = benchmark_jobs.ec2_sysbench_memory(condition_patterns[job][size], debug=debug)
    else:
        print('Error: invalid job')
        return False
    
    if result:
        print(result.df)
        if bucket:
            result.upload_to_s3('%s_%s_%s.csv.tmp' % (job, size, name), bucket, '%s-%s/%s.csv' % (job, size, name), file_type='csv')


def main():
    print('Cloud Benchmark')
    job_list = [
        's3-throughput',
        'ec2-sysbench-cpu',
        'ec2-sysbench-memory',
    ]
    job_size = ['small', 'large']

    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-j', '--job', dest='job', choices=job_list, help='job type', required=True)
    parser.add_argument('-s', '--size', dest='size', choices=job_size, help='job size', required=True)
    parser.add_argument('-b', '--bucket', dest='bucket', help='S3 bucket to store result files')
    parser.add_argument('-n', '--name', dest='name', default=str(datetime.date.today()), help='job name')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='show debug info')
    parser.add_argument('--target-s3', dest='target_s3', help='S3 bucket for benchmark target')

    args = parser.parse_args()
    
    options = dict()
    if 's3-' in args.job:
        if args.target_s3:
            options['target-s3'] = args.target_s3
        else:
            print('Error: use --target-s3 option')
            return False

    job_executer(args.job, args.size, args.bucket, args.name, options, args.debug)
    

if __name__=='__main__':
    main()
