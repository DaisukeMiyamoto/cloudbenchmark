# coding: utf-8

import json
import os
import sys
import subprocess
import string
import random
import time
import pkgutil
import cloudbenchmark
from blessings import Terminal


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
            return e.output.decode()
        
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
