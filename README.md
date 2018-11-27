cloudbenchmark
---

Benchmark suite for cloud environment

# Supported benchmark targets

- Amazon EC2: CPU, memory
- Amazon S3: throughput

# Prepare

- install ansible
- install sysbench
- set up aws credentials

# Install

```
$ sudo pip3 install cloudbenchmark
```

# Usage

## local mode

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

## remote mode

```
$ cloudbenchmark-manager -t [TEST-SET]
```

### test set

- `test-cpu`
- `ec2-sysbench-cpu-small`
- `ec2-sysbench-cpu-large`
- `ec2-sysbench-memory-large`

### large set instances

- t2.large
- t2.2xlarge
- t3.large
- t3.2xlarge
- c3.large
- c3.8xlarge
- c4.large
- c4.8xlarge
- c5.large
- c5.18xlarge
- m3.2xlarge
- m4.large
- m4.16xlarge
- m5.large
- m5.24xlarge
- r4.large
- r4.16xlarge
- r5.large
- r5.24xlarge

# Test

```
$ python3 setup.py test
```

# Acknowledgement
