from setuptools import setup
import os


description='Benchmark suite for cloud environment'
long_description = description
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()


setup(
    name='cloudbenchmark',
    version='0.2.2',
    packages=['cloudbenchmark'],
    package_dir={'cloudbenchmark': 'cloudbenchmark'},
    package_data={'cloudbenchmark': ['template/*.yaml', 'playbook/*.yaml', 'config/*.yaml']},
    description=description,
    long_description=long_description,
    author='Daisuke Miyamoto',
    author_email='midaisuk@gmail.com',
    url='https://github.com/DaisukeMiyamoto/cloudbenchmark',
    setup_requires=['pytest-runner'],
    install_requires=['boto3', 'numpy', 'tqdm', 'pandas', 'requests', 'blessings', 'pyyaml'],
    tests_require=['pytest'],
    keywords=['aws', 'cloud', 'benchmark', 'performance', 'flops'],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    test_suite='tests',
    entry_points={
        'console_scripts':[
            'cloudbenchmark=cloudbenchmark.main:main',
            'cloudbenchmark-manager=cloudbenchmark.deploy_manager:main'
        ]
    },
)
