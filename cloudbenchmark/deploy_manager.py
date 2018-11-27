# coding: utf-8

import boto3
import json
import os
import sys
import subprocess
import string
import random
import time
import argparse
import pkgutil
import cloudbenchmark
from blessings import Terminal
from cloudbenchmark import utils


class CloudFormationManager():
    def __init__(self, template_filename, parameters, stack_name='CloudBenchmarkStack', region='ap-northeast-1', random_stack_name=False, wait=False, show_stack_events=False):
        self.cfn_client = boto3.client('cloudformation', region_name=region)
        self.stack_name = stack_name
        if random_stack_name:
            self.stack_name += ('-%s' % utils.get_random_str(10))
        
        template_body = self._read_template(template_filename)
        response = self.cfn_client.create_stack(
            StackName = self.stack_name,
            TemplateBody = template_body,
            Parameters = self._convert_parameter_dict(parameters),
            Capabilities = ['CAPABILITY_NAMED_IAM'],
        )

        if wait:
            if show_stack_events:
                self._show_stack_events()
            else:
                self._use_waiter()

    def _show_stack_events(self, pooling_time=5):
        last_id = 0
        term = Terminal()

        while True:
            time.sleep(pooling_time)
            response = self.cfn_client.describe_stack_events(StackName=self.stack_name)
            event_list = list(reversed(response['StackEvents']))
            for event in event_list[last_id:]:
                if event['ResourceStatus'] == 'CREATE_IN_PROGRESS':
                    pre_tcode = term.yellow
                elif event['ResourceStatus'] == 'CREATE_COMPLETE':
                    pre_tcode = term.green
                else:
                    pre_tcode = term.red
                print('%s%s | %s | %s | %s%s' % (
                    pre_tcode,
                    event['LogicalResourceId'].ljust(30),
                    event['ResourceType'].ljust(30),
                    event['ResourceStatus'].ljust(20),
                    event['Timestamp'],
                    term.normal
                ))
            last_id = len(event_list)

            response = self.cfn_client.describe_stacks(StackName=self.stack_name)
            if response['Stacks'][0]['StackStatus'] != 'CREATE_IN_PROGRESS':
                break

    def _use_waiter(self):
        waiter = self.cfn_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=self.stack_name)
        
    def _convert_parameter_dict(self, parameters):
        cfn_parameter_list = []
        for k, v in parameters.items():
            cfn_parameter = {
                'ParameterKey': k,
                'ParameterValue': v
            }
            cfn_parameter_list.append(cfn_parameter)
        
        return cfn_parameter_list
    
    def _read_template(self, filename):
        d = os.path.dirname(sys.modules['cloudbenchmark'].__file__)
        template_body = pkgutil.get_data('cloudbenchmark', 'template/'+filename)
        # with open(filename) as f:
        #     template_body = f.read()
        return template_body.decode()

    def get_output(self, key):
        value = None
        response = self.cfn_client.describe_stacks(StackName=self.stack_name)
        for output in response['Stacks'][0]['Outputs']:
            if output['OutputKey'] == key:
                value = output['OutputValue']

        return value

    def delete(self):
        self.cfn_client.delete_stack(StackName=self.stack_name)


class AnsibleManager():
    def __init__(self, hostname, key, debug=False):
        self.hostname = hostname
        self.key = key
        self.debug = debug
    
    def _run_local_command(self, command):
        try:
            output = subprocess.check_output(command, shell=True)
            output_str = output.decode()
            if self.debug:
                print(output_str)
            return output_str
        except subprocess.CalledProcessError as e:
            print(e.cmd)
            print(e.output.decode())
        
    def ping(self):
        command = 'ansible -i %s, all -m ping --private-key=%s -u ec2-user --ssh-common-args="-o StrictHostKeyChecking=no"' % (self.hostname, self.key)
        result = self._run_local_command(command)
        if 'pong' in result:
            return True
        else:
            return False

    def run_playbook(self, playbook_filename):
        command = 'ansible-playbook -i %s, --private-key=%s -u ec2-user --ssh-common-args="-o StrictHostKeyChecking=no" %s' % (self.hostname, self.key, playbook_filename)
        return self._run_local_command(command)
        
    def run_command(self, command):
        command = 'ansible -i %s, all --private-key=%s -u ec2-user --ssh-common-args="-o StrictHostKeyChecking=no" -a "%s"' % (self.hostname, self.key, command)
        return self._run_local_command(command)


class DeployManager():
    def __init__(self, key_name, local_key_path, output_bucket_name):
        self.template_filename = 'ec2.yaml'
        self.key_name = key_name
        self.local_key_path = local_key_path
        self.playbook_filename = str(cloudbenchmark.__path__[0]) + '/playbook/install.yaml'
        self.output_bucket_name = output_bucket_name
        self.ping_retry = 0
        self.ping_retry_max = 5
    
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
                show_stack_events=True
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


def main():
    print('Cloud Benchmark Manager')
    test_set_list = {
        'test_cpu': {
            'instance_type_list': ['t2.micro'],
            'job_type': 'ec2-sysbench-cpu',
            'job_size': 'small'
        },
        'all_cpu': {
            'instance_type_list': ['t2.micro', 'c3.large', 'c4.large', 'c5.large'],
            'job_type': 'ec2-sysbench-cpu',
            'job_size': 'small'
        }
    }
    parser = argparse.ArgumentParser(description='Cloud Benchmark Suite.')
    parser.add_argument('-t', '--test-set', dest='test_set', choices=test_set_list.keys(), help='test set name', required=True)
    args = parser.parse_args()

    # TODO: auto generate key-pair
    deploymanager = DeployManager(key_name='aws-daisuke-tokyo',
        local_key_path='~/.ssh/aws-daisuke-tokyo.pem',
        output_bucket_name='midaisuk-benchmarks'
    )

    test_set = test_set_list[args.test_set]
    for instance_type in test_set['instance_type_list']:
        print('Benchmarking: %s [%s %s]' % (instance_type, test_set['job_type'], test_set['job_size']))
        deploymanager.run_remote_benchmark(instance_type, test_set['job_type'], test_set['job_size'])


if __name__=='__main__':
    main()
