# coding: utf-8

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
from cloudbenchmark.keypair_manager import KeyPairManager


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
        self.region = 'ap-northeast-1'
        self.debug = False
    
    def run_remote_benchmark(self, instance_type, job_type, job_size, ami_type='x86'):
        self.parameters = {
            'EC2InstanceType': instance_type,
            'KeyName': self.key_name,
            'AMIType': ami_type,
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
                show_stack_events=self.show_stack_events,
                region=self.region
            )
            target_ip = cfnmanager.get_output('PublicIP')
            time.sleep(5)
            ansiblemanager = AnsibleManager(target_ip, self.local_key_path)
            
            while True:
                if ansiblemanager.ping():
                    break
                print('Warning: ping retry')
                time.sleep(5)
                
            install_result = ansiblemanager.run_playbook(playbook_filename=self.playbook_filename)
            if self.debug:
                print(install_result)
            command_result = ansiblemanager.run_command(self.benchmark_command)
            if self.debug:
                print(command_result)
    
        except Exception as e:
            print(e)
        finally:
            cfnmanager.delete()


def deploy_core(args):
    deploymanager = DeployManager(args['key_name'], args['local_key_path'], args['output_bucket_name'])
    deploymanager.show_stack_events = False
    deploymanager.region = args['region']
    if args['debug']:
        deploymanager.debug = True

    print('Benchmarking: %s [%s %s %s]' % (args['instance_type'], args['job_type'], args['job_size'], args['ami_type']))
    deploymanager.run_remote_benchmark(args['instance_type'], args['job_type'], args['job_size'], args['ami_type'])


def deploy_multi(test_set_name, bucket, multi=1, region='us-west-2', debug=False):

    test_set_list = yaml.load(pkgutil.get_data('cloudbenchmark', 'config/test_set_list.yaml'))
    key_name = 'cloudbenchmark_key_' + utils.get_random_str(10) + '.tmp'
    local_key_path = key_name
    keypairmanager = KeyPairManager(key_name, region)
    keypairmanager.create_key_pair()
    keypairmanager.store_key(local_key_path)
    test_set = test_set_list[test_set_name]

    # prepare parameter list for multi processing
    deploy_list = []
    for instance_type in test_set['instance_type_list']:
        if not 'ami_type' in test_set:
            test_set['ami_type'] = 'x86'

        deploy = {
            'instance_type': instance_type,
            'job_type': test_set['job_type'],
            'job_size': test_set['job_size'],
            'ami_type': test_set['ami_type'],
            'key_name': key_name,
            'local_key_path': local_key_path,
            'output_bucket_name': bucket,
            'region': region,
            'debug': debug
        }
        deploy_list.append(deploy)

    # run deploy
    pool = multiprocessing.Pool(multi)
    pool.map(deploy_core, deploy_list)
    pool.close()
    
    # clean up
    keypairmanager.delete_key_pair()
    os.remove(local_key_path)


def main():
    print('Cloud Benchmark Manager')
    test_set_list = yaml.load(pkgutil.get_data('cloudbenchmark', 'config/test_set_list.yaml'))
    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-t', '--test-set', dest='test_set', choices=test_set_list.keys(), help='test set name', required=True)
    parser.add_argument('-m', '--multi-process', dest='multi', help='use multi process', default=1)
    parser.add_argument('-r', '--region', dest='region', help='AWS region', default='us-west-2')
    parser.add_argument('-b', '--bucket', dest='bucket', help='S3 bucket to store result files', required=True)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='show debug info')
    args = parser.parse_args()

    deploy_multi(args.test_set, args.bucket, int(args.multi), args.region, args.debug)
    
    
if __name__=='__main__':
    main()
