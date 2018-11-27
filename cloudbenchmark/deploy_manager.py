# coding: utf-8

import boto3
import json
import os
import sys
import time
import argparse
import pkgutil
import yaml
from blessings import Terminal
import multiprocessing
import cloudbenchmark
from cloudbenchmark import utils
from cloudbenchmark.cloudformation_manager import CloudFormationManager
from cloudbenchmark.ansible_manager import AnsibleManager


class DeployManager():
    def __init__(self, key_name, local_key_path, output_bucket_name):
        self.template_filename = 'ec2.yaml'
        self.key_name = key_name
        self.local_key_path = local_key_path
        self.playbook_filename = str(cloudbenchmark.__path__[0]) + '/playbook/install.yaml'
        self.output_bucket_name = output_bucket_name
        self.ping_retry = 0
        self.ping_retry_max = 5
        self.show_stack_events = True
        self.test_set_list = yaml.load(pkgutil.get_data('cloudbenchmark', 'config/test_set_list.yaml'))
    
    def run_remote_benchmark(self, instance_type, job_type, job_size):
        self.parameters = {
            'EC2InstanceType': instance_type,
            'KeyName': self.key_name,
            'OutputS3': self.output_bucket_name
        }
        self.benchmark_command = '/usr/local/bin/cloudbenchmark -j %s -s %s -b %s' % (
            job_type,
            job_size,
            self.output_bucket_name
        )

        try:
            cfnmanager = CloudFormationManager(
                template_filename=self.template_filename,
                parameters=self.parameters,
                random_stack_name=True,
                wait=True,
                show_stack_events=self.show_stack_events
            )
            target_ip = cfnmanager.get_output('PublicIP')
            time.sleep(5)
            ansiblemanager = AnsibleManager(target_ip, self.local_key_path)
            
            while True:
                if ansiblemanager.ping():
                    break
                print('Warning: ping retry')
                time.sleep(5)
                
            ansiblemanager.run_playbook(playbook_filename=self.playbook_filename)
            ansiblemanager.run_command(self.benchmark_command)
    
        except Exception as e:
            print(e)
        finally:
            cfnmanager.delete()


def deploy_core(args):
    deploymanager = DeployManager(args['key_name'], args['local_key_path'], args['output_bucket_name'])
    print('Benchmarking: %s [%s %s]' % (args['instance_type'], args['job_type'], args['job_size']))
    deploymanager.run_remote_benchmark(args['instance_type'], args['job_type'], args['job_size'])


def main():
    print('Cloud Benchmark Manager')

    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-t', '--test-set', dest='test_set', choices=test_set_list.keys(), help='test set name', required=True)
    parser.add_argument('-m', '--multi-process', dest='multi', help='use multi process', default=1)
    args = parser.parse_args()

    # TODO: auto generate key-pair
    key_name = 'aws-daisuke-tokyo'
    local_key_path = '~/.ssh/aws-daisuke-tokyo.pem'
    output_bucket_name = 'midaisuk-benchmarks'
    test_set = test_set_list[args.test_set]

    deploy_list = []
    for instance_type in test_set['instance_type_list']:
        deploy = {
            'instance_type': instance_type,
            'job_type': test_set['job_type'],
            'job_size': test_set['job_size'],
            'key_name': key_name,
            'local_key_path': local_key_path,
            'output_bucket_name': output_bucket_name
        }
        deploy_list.append(deploy)

    pool = multiprocessing.Pool(args.multi)
    pool.map(deploy_core, deploy_list)
    pool.close()

if __name__=='__main__':
    main()
