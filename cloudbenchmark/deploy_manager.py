# coding: utf-8

import boto3
import json
import subprocess
import string
import random
import time
from pprint import pprint


class DeployManager():
    def __init__(self, template_filename, stack_name='CloudBenchmarkStack', region='ap-northeast-1', random_stack_name=False, wait=False, show_stack_events=False):
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

    def _show_stack_events(self):
        while True:
            time.sleep(5)
            response = self.cfn_client.describe_stack_events(StackName=self.stack_name)
            for event in response['StackEvents']:
                print('------------------------------------------------')
                pprint(event)
            
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
        with open(filename) as f:
            template_body = f.read()
        return template_body

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


if __name__=='__main__':
    parameters = {
        'EC2InstanceType': 't2.micro',
        'KeyName': 'aws-daisuke-tokyo',
    }

    deploymanager = DeployManager(template_filename='ec2.yaml', random_stack_name=True, wait=True, show_stack_events=True)
    target_ip = deploymanager.get_output('PublicIP')
    print(target_ip)
    
    ansiblemanager = AnsibleManager(target_ip, '~/.ssh/aws-daisuke-tokyo.pem')
    ansiblemanager.ping()

    deploymanager.delete()

    