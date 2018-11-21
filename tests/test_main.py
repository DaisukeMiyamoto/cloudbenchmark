# coding: utf-8

from cloudbenchmark.main import job_executer


def test_s3_throughput_small():
    options = dict()
    options['target_s3'] = 'midaisuk-s3-test'
    job_executer('s3-throughput', 'small', None, 'test_job', options)


def test_ec2_sysbench_cpu_small():
    job_executer('ec2-sysbench-cpu', 'small', None, 'test_job', None)


def test_ec2_sysbench_memory_small():
    job_executer('ec2-sysbench-memory', 'small', None, 'test_job', None)
