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

- `test-cpu`: t2.micro
- `all-cpu`: t2.micro, c3.large, c4.large, c5.large


# Test

```
$ python3 setup.py test
```

# Acknowledgement
