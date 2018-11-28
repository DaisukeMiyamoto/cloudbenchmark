# -*- coding: utf-8 -*-

import sys
import os
import datetime
import json
from tqdm import tqdm
import subprocess
import multiprocessing
import pandas as pd
from cloudbenchmark import s3benchmark
from cloudbenchmark import benchmarkrecorder
from cloudbenchmark import utils


def convert_process_num(num):
    print(num)
    if num == 'MAX':
        result = int(multiprocessing.cpu_count())
    elif num == 'HALF_MAX':
        result = int(multiprocessing.cpu_count() / 2)
    else:
        result = num
    
    if result >= 1:
        return result
    else:
        return 1


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


def ec2_sysbench_cpu(condition_pattern, debug=False):
    recorder = benchmarkrecorder.BenchmarkRecorder([
        'trial',
        'num_threads',
        'score'
    ])
    
    condition_list = []
    for num_threads in condition_pattern['num_threads']:
        for trial in condition_pattern['trial']:
            condition = {'num_threads': convert_process_num(num_threads), 'trial': trial}
            condition_list.append(condition)

    for condition in tqdm(condition_list):
        try:
            command = 'sysbench --threads=%d cpu run' % (condition['num_threads'])
            if debug:
                print(command)
            output = subprocess.check_output(command, shell=True)
            
        except subprocess.CalledProcessError as e:
            print('Error: sysbench is required')
            print(e.cmd)
            print(e.output)
            return False

        score = 0
        output_lines = output.decode().split()
        for i, text in enumerate(output_lines):
            if text == 'second:':
                score = float(output_lines[i+1])
                break

        recorder.add_record([
            condition['trial'],
            condition['num_threads'],
            score,
        ])

        if debug:
            print('CPU score %f' % score)

    return recorder


def ec2_sysbench_memory(condition_pattern, debug=False):
    recorder = benchmarkrecorder.BenchmarkRecorder([
        'trial',
        'num_threads',
        'throughput_mbyte_per_sec'
    ])
    
    condition_list = []
    for num_threads in condition_pattern['num_threads']:
        for trial in condition_pattern['trial']:
            condition = {'num_threads': convert_process_num(num_threads), 'trial': trial}
            condition_list.append(condition)

    for condition in tqdm(condition_list):
        try:
            command = 'sysbench --threads=%d memory run' % (condition['num_threads'])
            if debug:
                print(command)
            output = subprocess.check_output(command, shell=True)

        except subprocess.CalledProcessError as e:
            print('Error: sysbench is required')
            print(e.cmd)
            print(e.output)
            return False

        score = 0
        output_lines = output.decode().split()
        for i, text in enumerate(output_lines):
            if text == 'MiB':
                score = float(output_lines[i-1])
                break

        recorder.add_record([
            condition['trial'],
            condition['num_threads'],
            score,
        ])

        if debug:
            print('Memory score %f' % score)

    return recorder


def ec2_unixbench(condition_pattern, debug=False):
    unixbench_path = 'byte-unixbench/UnixBench/'
    unixbench_result_file = 'unixbench_result_' + utils.get_random_str(5)
    # test_target = condition['test_target']
    
    condition_list = []
    for num_threads in condition_pattern['num_threads']:
        for trial in condition_pattern['trial']:
            condition = {
                'trial': trial,
                'num_threads': convert_process_num(num_threads),
                'iteration': condition_pattern['iteration'],
                'test_target': condition_pattern['test_target']
            }
            if condition['test_target'] == 'index':
                test_target = ''
            else:
                test_target = condition['test_target']

            condition_list.append(condition)

    results = []
    for condition in tqdm(condition_list):
        try:
            command = 'export UB_OUTPUT_CSV=true; export UB_OUTPUT_FILE_NAME=%s; cd %s; ./Run -c %d -i %d %s' % (unixbench_result_file, unixbench_path, condition['num_threads'], condition['iteration'], condition['test_target'])
            if debug:
                print(command)
            output = subprocess.check_output(command, shell=True)
            
        except subprocess.CalledProcessError as e:
            print('Error: UnixBench is required')
            print(e.cmd)
            print(e.output)
            return False

        output_lines = output.decode().split('\n')
        df = pd.read_csv(unixbench_path + 'results/' + unixbench_result_file + '.csv')

        results.append(df)

    column_name_list = [
        'trial',
        'num_threads',
        'iteration',
    ]
    for column_name in results[0]:
        column_name_list.append(column_name)

    recorder = benchmarkrecorder.BenchmarkRecorder(column_name_list)

    for i, df in enumerate(results):
        result = [
            condition_list[i]['trial'],
            condition_list[i]['num_threads'],
            condition_list[i]['iteration'],
        ]
        for column_name in column_name_list[3:]:
            for data in df[column_name]:
                result.append(data)

        recorder.add_record(result)

    return recorder
