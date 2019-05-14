import ConfigParser
import os
import base64
import logging

from google.cloud import storage

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

    def transfer(self, source_file_name, source_content):
        """Transfer the attachment file to the bucket."""

        source_path = "/tmp/%s" % (source_file_name)
        logging.info("Open to write the file %s" % (source_path))
        f = open(source_path, 'wb')
        f.write(base64.b64decode(source_content))
        logging.info("File written")
        f.close()

        destination_path = "%s/%s" % (self.dir, source_file_name)
        self.upload_blob(source_path, destination_path)

    # def cloud_copy(self, source_file_name, source_content):
    #     logging.info("Writting STARTS with cloudstorage")
    #     gcs_path = "gs://%s/%s/%s" % (self.bucket, self.dir, source_file_name)
    #     # The retry_params specified in the open call will override the default
    #     # retry params for this particular file handle.
    #     write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
    #     with cloudstorage.open(gcs_path, 'w', retry_params=write_retry_params) as cloudstorage_file:
    #         cloudstorage_file.write(base64.b64decode(source_content))
    #     logging.info("Writting ENDS with cloudstorage")
    #     return gcs_path

    def upload_command(self, source_file_name, source_path):
        gcs_path = "gs://%s/%s/%s" % (self.bucket, self.dir, source_file_name)
        BOTO = "-o Boto:parallel_process_count=%s -o Boto:parallel_thread_count=%s" % (self.boto_process, self.boto_thread)
        command='gsutil -m -q %s cp %s %s' % (BOTO, source_path, gcs_path)
        print(command)
        os.system(command)
        logging.info("File %s upload to %s" % (source_file_name, gcs_path))

    def upload_blob(self, source_path, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_path)

        print('File {} uploaded to {}.'.format(
            source_path,
            destination_blob_name))
