import ConfigParser
import os
import logging
import re

from google.cloud import storage
from requests_toolbelt.adapters import appengine

class GCSTransfer:
    def __init__(self, to_account, msg_date):
        #This line fixes the error
        #AttributeError: 'VerifiedHTTPSConnection' object has no attribute '_tunnel_host'
        appengine.monkeypatch()
        configParser = ConfigParser.RawConfigParser()
        file = r'./config/reception.cfg'
        configParser.read(file)
        self.msg_date=msg_date
        self.bucket = configParser.get('DEFAULT', 'BUCKET')
        self.dir = configParser.get('DEFAULT', 'DIRECTORY')

        for account in configParser.sections():
            matchObj = re.match('.*%s.*' % (account), to_account, re.I)
            if matchObj:
                self.bucket = configParser.get(account, 'BUCKET')
                self.dir = configParser.get(account, 'DIRECTORY')

    def exists(self, bucket, destination_path):
        """ Verifies if the file already exists in GCS """
        # https://github.com/googleapis/google-cloud-python/blob/storage-1.15.0/storage/google/cloud/storage/bucket.py#L661
        return bucket.get_blob(destination_path) != None

    def transfer(self, source_file_name, source_content):
        """Transfer the attachment file to the bucket."""

        source_path = "/tmp/%s" % (source_file_name)
        logging.info("Open to write the file %s" % (source_path))
        f = open(source_path, 'wb')
        f.write(source_content)
        logging.info("File written")
        f.close()

        destination_path = "%s/%s/%s" % (self.dir, self.msg_date, source_file_name)
        self.upload_blob(source_path, destination_path)

    def upload_blob(self, source_path, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket)
        if self.exists(bucket, destination_blob_name):
            # Throws conflict error
            raise ValueError('The file {}/{} does not exists.'.format(self.bucket, destination_blob_name))

        # Uploads the blob to the GCS
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_path)

        logging.info("File %s uploaded to %s", source_path, destination_blob_name)

        # Checks if the file already exists
        if not self.exists(bucket, destination_blob_name):
            # Throws error on not saving file.
            raise ValueError('The file {}/{} does not exists.'.format(self.bucket, destination_blob_name))



    def local_transfer(self, source_file_name, source_content):
        """Transfer the attachment file to the bucket."""

        source_path = "/tmp/%s" % (source_file_name)
        logging.info("Open to write the file %s" % (source_path))
        f = open(source_path, 'wb')
        f.write(source_content)
        logging.info("File written")
        f.close()

        destination_path = "gs://%s/%s/%s/%s" % (self.bucket, self.dir, self.msg_date, source_file_name)
        command='gsutil -m cp %s %s' % (source_path, destination_path )
        print(command)
        os.system(command)
