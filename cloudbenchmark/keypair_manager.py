# coding: utf-8

import boto3
import os

class KeyPairManager():
    def __init__(self, key_name, region):
        self.key_name = key_name
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=self.region)

    def create_key_pair(self):
        self.key = self.ec2.create_key_pair(KeyName=self.key_name)
        return self.key
        
    def store_key(self, filename):
        with open(filename, 'wt') as f:
            f.write(self.key['KeyMaterial'])
            
        os.chmod(filename, 0o600)
        
    def delete_key_pair(self):
        self.ec2.delete_key_pair(KeyName=self.key_name)


if __name__=='__main__':
    keypairmanager = KeyPairManager('test-key', 'ap-northeast-1')
    keypairmanager.create_key_pair()
    keypairmanager.store_key('test_key.tmp')
    