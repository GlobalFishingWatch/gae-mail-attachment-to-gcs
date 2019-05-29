import ConfigParser
import os
import logging
import re

class GCSTransfer:
    def __init__(self, to_account, msg_date):
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

    def transfer(self, source_file_name, source_content):
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
