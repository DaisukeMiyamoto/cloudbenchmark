# coding: utf-8

import boto3
import json
import os
import sys
import time
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
        template_body = pkgutil.get_data('cloudbenchmark', 'template/'+filename)
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

