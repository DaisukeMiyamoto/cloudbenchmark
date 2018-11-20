import sys
import datetime
import s3benchmark
import benchmarkrecorder


def main():
    s3_bucket_name = 'midaisuk-s3-test'

    max_concurrency_list = [10, 100]
    max_io_queue_list = [1000, 10000]
    filesize_list = [32, 64]
    # filesize_list = [32, 64, 128, 256, 512, 1024, 2048, 4096]
    threads_list = [1, 2]
    # threads_list = [1, 2, 4, 8, 16, 32]
    trial = 3
    random_data = True
    
    recorder = benchmarkrecorder.BenchmarkRecorder([
        'trial',
        'file_size',
        'max_concurrency',
        'max_io_queue',
        'random_data',
        'num_process',
        'upload_time_sec',
        'download_time_sec',
        'upload_speed_mbps',
        'download_speed_mbps',
    ])

    for max_concurrency in max_concurrency_list:
        for max_io_queue in max_io_queue_list:
            for num_process in threads_list:
                for filesize in filesize_list:
                    print('Settings:')
                    print(' * Max Concurrency: %d' % max_concurrency)
                    print(' * Max IO Queue: %d' % max_io_queue)
                    print(' * Random Data: %s' % random_data)

                    for i in range(trial):
                        s3bench = s3benchmark.S3Benchmark(s3_bucket_name,
                            max_concurrency=max_concurrency,
                            max_io_queue=max_io_queue,
                            random_data=random_data
                        )
                        
                        upload_time, download_time = s3bench.multi_run(num_process, filesize)
                        recorder.add_record([
                                trial,
                                filesize,
                                max_concurrency,
                                max_io_queue,
                                random_data,
                                num_process,
                                upload_time,
                                download_time,
                                filesize * num_process / upload_time * 8,
                                filesize * num_process  / download_time * 8,
                            ]
                        )

    print(recorder.df)
    today = datetime.date.today()
    recorder.upload_to_s3('result.tmp', 'midaisuk-benchmarks', 'tmp/' + str(today) + '.csv', file_type='csv')


if __name__=='__main__':
    main()
