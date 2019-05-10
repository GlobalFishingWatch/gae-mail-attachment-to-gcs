import ConfigParser

from google.cloud import storage

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

    def transfer(self, source_file, destination_file):
        """Transfer the attachment file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket)
        dest = "%s/%s" % (self.dir, destination_file)
        blob = bucket.blob(dest)

        blob.upload_from_filename(source_file)

        print('File {} uploaded to {}.'.format(
            source_file,
            dest))

