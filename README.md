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

```
$ cloudbenchmark -j [JOB_TYPE] -s [JOB_SIZE] -b [RESULT_BUCKET]
```

## job list

- `s3-throughput`
  - `--target-s3 [TARGET_BUCKET]`
- `ec2-sysbench-cpu`
- `ec2-sysbench-memory`

## job size

- `small`
- `large`

