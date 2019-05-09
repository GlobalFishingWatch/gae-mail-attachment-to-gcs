import os
import ConfigParser

class GCSTransfer:
    def __init__(self):
        configParser = ConfigParser.RawConfigParser()
        file = r'./config/reception.cfg'
        configParser.read(file)
        boto_process = configParser.get('GCS', 'BOTO_PARALLEL_PROCESS')
        boto_thread = configParser.get('GCS', 'BOTO_PARALLEL_THREAD')
        self.BOTO = "-o Boto:parallel_process_count=%i -o Boto:parallel_thread_count=%i" % (boto_process, boto_thread)
        self.bucket = configParser.get('GCS', 'BUCKET')
        self.dir = configParser.get('GCS', 'DIRECTORY')

    def transfer(self, source_file, gcs_path):
        gcs_path = "gs://%s/%s" % (self.bucket, self.dir)
        command='gsutil -m -q %s cp %s %s' % (BOTO, source_file, gcs_path )
        print(command)
        os.system(command)
