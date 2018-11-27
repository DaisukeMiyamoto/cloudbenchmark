# coding: utf-8

import boto3
import json
import os
import sys
import subprocess
import string
import random
import time
import pkgutil
# from pprint import pprint
import cloudbenchmark
from blessings import Terminal


class DeployManager():
    def __init__(self, template_filename, parameters, stack_name='CloudBenchmarkStack', region='ap-northeast-1', random_stack_name=False, wait=False, show_stack_events=False):
        self.cfn_client = boto3.client('cloudformation', region_name=region)
        self.stack_name = stack_name
        if random_stack_name:
            self.stack_name += ('-%s' % self._get_random_str(10))
        
        template_body = self._read_template(template_filename)
        response = self.cfn_client.create_stack(
            StackName = self.stack_name,
            TemplateBody = template_body,
            Parameters = self._convert_parameter_dict(parameters),
            # Capabilities = 'CAPABILITY_NAMED_IAM',
        )

        if wait:
            if show_stack_events:
                self._show_stack_events()
            else:
                self._use_waiter()

    def _get_random_str(self, n):
        random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
        return random_str


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
        print(d)
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
    def __init__(self, hostname, key):
        self.hostname = hostname
        self.key = key
        
    def ping(self):
        try:
            command = 'ansible -i %s, all -m ping --private-key=%s -u ec2-user --ssh-common-args="-o StrictHostKeyChecking=no"' % (self.hostname, self.key)
            output = subprocess.check_output(command, shell=True)
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(e.cmd)
            print(e.output)

    def run_playbook(self, playbook_name):
        pass

def deploy_main(instance_type='t2.micro', key_name='aws-daisuke-tokyo', local_key_path='~/.ssh/aws-daisuke-tokyo.pem'):
    parameters = {
        'EC2InstanceType': instance_type,
        'KeyName': key_name,
    }

    deploymanager = DeployManager(template_filename='ec2.yaml', parameters=parameters, random_stack_name=True, wait=True, show_stack_events=True)
    target_ip = deploymanager.get_output('PublicIP')
    # print(target_ip)
    
    ansiblemanager = AnsibleManager(target_ip, local_key_path)
    ansiblemanager.ping()

    deploymanager.delete()


if __name__=='__main__':
    deploy_main()
