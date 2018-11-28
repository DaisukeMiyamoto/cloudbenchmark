#!/usr/bin/env python
# coding: utf-8

import sys
import datetime
import argparse
import json
import multiprocessing
import yaml
import pkgutil
from cloudbenchmark import benchmark_jobs
from cloudbenchmark import utils


def job_executer(job, size, bucket, name, options, debug=False):

    print('[%s]' % job)
    condition_patterns = yaml.load(pkgutil.get_data('cloudbenchmark', 'config/condition_patterns.yaml'))
    result = None
    if 's3-throughput' in job:
        result = benchmark_jobs.s3_throughput(options['target_s3'], condition_patterns[job][size], debug=debug)
    elif 'ec2-sysbench-cpu' in job:
        result = benchmark_jobs.ec2_sysbench_cpu(condition_patterns[job][size], debug=debug)
    elif 'ec2-sysbench-memory' in job:
        result = benchmark_jobs.ec2_sysbench_memory(condition_patterns[job][size], debug=debug)
    elif 'ec2-unixbench' in job:
        result = benchmark_jobs.ec2_unixbench(condition_patterns[job][size], debug=debug)
    else:
        print('Error: invalid job')
        return False
    
    if result:
        print(result.df)
        if bucket:
            result.upload_to_s3('%s_%s_%s.csv.tmp' % (job, size, name), bucket, '%s-%s/%s.csv' % (job, size, name), file_type='csv')


def main():
    print('Cloud Benchmark')
    job_size = ['small', 'large', 'flex']
    default_job_name = str(datetime.date.today())+'-'+utils.get_random_str(10)
    condition_patterns = yaml.load(pkgutil.get_data('cloudbenchmark', 'config/condition_patterns.yaml'))

    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-j', '--job', dest='job', choices=condition_patterns.keys(), help='job type', required=True)
    parser.add_argument('-s', '--size', dest='size', choices=job_size, help='job size', required=True)
    parser.add_argument('-b', '--bucket', dest='bucket', help='S3 bucket to store result files')
    parser.add_argument('-n', '--name', dest='name', default=default_job_name, help='job name')
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
