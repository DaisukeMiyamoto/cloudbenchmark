import yaml
import pprint

test_set_list = {
    'test-cpu': {
        'instance_type_list': ['t2.micro'],
        'job_type': 'ec2-sysbench-cpu',
        'job_size': 'flex'
    },
    'all-cpu': {
        'instance_type_list': ['t2.micro', 'c3.large', 'c4.large', 'c5.large', 'm4.large', 'm5.large'],
        'job_type': 'ec2-sysbench-cpu',
        'job_size': 'flex'
    },
    'all-memory': {
        'instance_type_list': ['t2.micro', 'c3.large', 'c4.large', 'c5.large', 'm4.large', 'm5.large'],
        'job_type': 'ec2-sysbench-memory',
        'job_size': 'flex'
    }
}

condition_patterns = {
    's3-throughput': {
        'small': {
            'trial': [0],
            'file_size': [64, 256, 1024],
            'max_concurrency': [10],
            'max_io_queue': [1000],
            'num_process': [1],
            'random_data': [True],
        },
        'large': {
            'trial': [0, 1, 2],
            'file_size': [32, 64, 128, 256, 512, 1024, 2048, 4096],
            'max_concurrency': [10, 100],
            'max_io_queue': [1000, 10000],
            'num_process': [1, 2, 4, 8, 16, 32],
            'random_data': [True],
        }
    },
    'ec2-sysbench-cpu': {
        'small': {
            'trial': [0],
            'num_threads': [1, 2],
        },
        'large': {
            'trial': [0, 1, 2],
            'num_threads': [1, 2, 4, 8, 16, 32],
        },
        'flex': {
            'trial': [0, 1, 2],
            'num_threads': [1, 'HALF_MAX', 'MAX']
        }
    },
    'ec2-sysbench-memory': {
        'small': {
            'trial': [0],
            'num_threads': [1, 2],
        },
        'large': {
            'trial': [0, 1, 2],
            'num_threads': [1, 2, 4, 8, 16, 32],
        },
        'flex': {
            'trial': [0, 1, 2],
            'num_threads': [1, 'HALF_MAX', 'MAX']
        }
    }
}

# f = open('condition_patterns.yaml', 'w')
# f.write(yaml.dump(condition_patterns))
# f.close()

f = open('config/condition_patterns.yaml', 'r')
text = f.read()
data = yaml.load(text)
pprint.pprint(data)
