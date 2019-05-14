import ConfigParser
import os
import base64
import logging

from google.cloud import storage
from requests_toolbelt.adapters import appengine

class GCSTransfer:
    def __init__(self):
        #This line fixes the error
        #AttributeError: 'VerifiedHTTPSConnection' object has no attribute '_tunnel_host'
        appengine.monkeypatch()
        configParser = ConfigParser.RawConfigParser()
        file = r'./config/reception.cfg'
        configParser.read(file)
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

    def upload_blob(self, source_path, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_path)

        print('File {} uploaded to {}.'.format(
            source_path,
            destination_blob_name))
