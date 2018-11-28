# coding: utf-8
import os
import time
import cloudbenchmark
from cloudbenchmark.deploy_manager import deploy_core


def test_deploy(instance_type='t2.micro'):

    deploy = {
        'instance_type': 't2.micro',
        'job_type': 'ec2-sysbench-cpu',
        'job_size': 'small',
        'key_name': 'aws-daisuke-tokyo',
        'local_key_path': '~/.ssh/aws-daisuke-tokyo.pem',
        'output_bucket_name': 'midaisuk-benchmarks',
        'region': 'ap-northeast-1'
    }
    deploy_core(deploy)
