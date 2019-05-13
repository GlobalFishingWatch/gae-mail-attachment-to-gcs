import ConfigParser
import os

class GCSTransfer:
    def __init__(self):
        configParser = ConfigParser.RawConfigParser()
        file = r'./config/reception.cfg'
        configParser.read(file)
        self.boto_process = configParser.get('GCS', 'BOTO_PARALLEL_PROCESS')
        self.boto_thread = configParser.get('GCS', 'BOTO_PARALLEL_THREAD')
        self.bucket = configParser.get('GCS', 'BUCKET')
        self.dir = configParser.get('GCS', 'DIRECTORY')
        configParser

    def transfer(self, source_file_name, source_file_content, destination_file):
        """Transfer the attachment file to the bucket."""
        source_path = "/tmp/%s".format(source_file_name)
        f = open(source_path, 'wb')
        f.write(source_file_content)
        f.close()

        gcs_path = "gs://%s/%s/%s" % (self.bucket, self.dir, source_file_name)
        BOTO = "-o Boto:parallel_process_count=%s -o Boto:parallel_thread_count=%s" % (self.boto_process, self.boto_thread)
        command='gsutil -m -q  %s cp %s %s' % (BOTO, source_path, gcs_path)
        print(command)
        os.system(command)
