# cloudbenchmark

![badge](https://codebuild.ap-northeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiend3MnZvR1NEcEwwNnp5dXg5T3ZsRUVVRFNTcUJWb2hOaTd2WDNtLzNPT0dtaXpmOVNiV2UzYmV3WXZHK0UxMEFEQnJxcUJkaTBaWkZXSHZMS3BhbGtBPSIsIml2UGFyYW1ldGVyU3BlYyI6Ik1EdmF5V0x0RmEwckppZXEiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

Benchmark suite for cloud environment

## Supported benchmark targets

- Amazon EC2
  - sysbench: CPU, memory
- Amazon S3
  - throughput


## Prepare

- install ansible
- install sysbench
- set up aws credentials

## Install

```
$ sudo pip3 install cloudbenchmark
```

## Usage: local mode


```
$ cloudbenchmark -j [JOB_TYPE] -s [JOB_SIZE] -b [RESULT_BUCKET]
```

### job list

- `s3-throughput`
  - `--target-s3 [TARGET_BUCKET]`
- `ec2-sysbench-cpu`
- `ec2-sysbench-memory`

### job size

- `small`
- `large`
- `flex`

## Usage: remote (CloudFormation) mode

```
$ cloudbenchmark-manager -t [TEST_SET] -m [CONCURRENT_NUMBER] -b [RESULT_BUCKET]
```

### test set

- `test-cpu`
- `ec2-sysbench-cpu-small`
- `ec2-sysbench-cpu-large`
- `ec2-sysbench-memory-large`

### instance list


- large
  - t2.micro
  - t2.medium
  - t2.large
  - t2.xlarge
  - t2.2xlarge
  - t3.micro
  - t3.medium
  - t3.large
  - t3.2xlarge
  - c3.large
  - c3.2xlarge
  - c3.8xlarge
  - c4.large
  - c4.2xlarge
  - c4.8xlarge
  - c5.large
  - c5.2xlarge
  - c5.18xlarge
  - m3.2xlarge
  - m4.large
  - m4.2xlarge
  - m4.16xlarge
  - m5.large
  - m5.2xlarge
  - m5.24xlarge
  - m5a.large
  - m5a.2xlarge
  - m5a.24xlarge
  - r4.large
  - r4.2xlarge
  - r4.16xlarge
  - r5.large
  - r5.2xlarge
  - r5.24xlarge
  - r5a.large
  - r5a.2xlarge
  - r5a.24xlarge
  - d2.8xlarge
- arm-large
  - a1.medium
  - a1.large
  - a1.xlarge
  - a1.2xlarge
  - a2.4xlarge

## Test

### run all test

```
$ python3 setup.py test
```

### tested region

- `us-west-2`
- `ap-northeast-1`

## Acknowledgement

- sysbench: https://github.com/akopytov/sysbench
- UnixBench: https://github.com/kdlucas/byte-unixbench
- HimenoBench
- STREAM
- fio
