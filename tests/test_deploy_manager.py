# coding: utf-8
import os
import time
import cloudbenchmark
from cloudbenchmark.deploy_manager import deploy_multi


def test_deploy(instance_type='t2.micro'):
    deploy_multi('test-cpu', 'midaisuk-benchmarks', 1, 'ap-northeast-1')

def test_deploy_multi(instance_type='t2.micro'):
    deploy_multi('ec2-sysbench-cpu-small', 'midaisuk-benchmarks', 2, 'ap-northeast-1')
