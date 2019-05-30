from datetime import datetime
from utils.upload_gcs import GCSTransfer
import argparse
import email
import email.header
import getpass
import hashlib
import imaplib
import logging
import sys
import os  
import time
import socket

FORMAT = '%(asctime)-15s - %(message)s'
OUTPUT_PATH = 'output'
logging.basicConfig(format=FORMAT)

class IMAP4Connection():
    def __init__(self, account, folder, start_date, end_date):
        self.account = account
        self.folder = folder
        self.start_date = start_date
        self.end_date = end_date
        self.count=0
        self.slice_size=100
        self.passwd = None
        self.zero_mails = False

    def chunks(self, list):
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(list), self.slice_size):
            yield list[i:i + self.slice_size]

    def _gmailTime2Internaldate(self, date_time):
        _month_names = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if isinstance(date_time, (int, long, float)):
            tt = time.localtime(date_time)
        elif isinstance(date_time, (tuple, time.struct_time)):
            tt = date_time
        elif isinstance(date_time, str) and (date_time[0],date_time[-1]) == ('"','"'):
            return date_time        # Assume in correct format
        else:
            raise ValueError("date_time not of a known type")
        return ('"%02d-%s-%04d"' %
            ((tt[2], _month_names[tt[1]], tt[0])))


    def process_mailbox(self, imap_connection):
        where=[]
        where.append('ALL')
        if self.start_date != None:
            starts = self._gmailTime2Internaldate(time.mktime(datetime.strptime(self.start_date,"%Y-%m-%d").timetuple()))
            where.append('SINCE')
            where.append(starts)
        if self.end_date != None:
            ends = self._gmailTime2Internaldate(time.mktime(datetime.strptime(self.end_date,"%Y-%m-%d").timetuple()))
            where.append('BEFORE')
            where.append(ends)
        print '>> ', where

        status, email_ids = imap_connection.search(None, *where)
        if status != 'OK':
            print "No messages found!"
            return

        total_emails=len(email_ids[0].split())
        print '>> Total emails to process ', total_emails if len(email_ids)>0 else 'Zero.'

        #In case the amount of email_ids is zero stop processing
        if email_ids[0] == '' or len(email_ids) == 0:
            self.zero_mails=True

        email_ids_list = email_ids[0].split()
        email_id_lists_chunked = list(self.chunks(email_ids_list))

        for i in xrange(len(email_id_lists_chunked)):
            old_counter=self.count
            self.count=self.count+len(email_id_lists_chunked[i])
            print "Fetching from {} to {} out of {} (slize = {}), be patient may take some time.".format(
                                                                old_counter,
                                                                self.count,
                                                                total_emails,
                                                                self.slice_size)
            email_ids_sub_list=email_id_lists_chunked[i]
            fetch_ids = ','.join(email_ids_sub_list)

            status, emails = imap_connection.fetch(fetch_ids, '(RFC822)')

            print "Got {} emails.".format(len(emails)/2)

            for m in range(len(email_ids_sub_list)):
                msg = email.message_from_string(emails[m*2+0][1])
                decode = email.header.decode_header(msg['Subject'])[0]
                to = msg['To']
                date = msg['Date']

                subject = decode[0]
                # Now convert to local date-time
                date_tuple = email.utils.parsedate_tz(date)
                msg_date = datetime.now()
                if date_tuple:
                    msg_date = datetime.utcfromtimestamp(email.utils.mktime_tz(date_tuple))

                for attachment in msg.get_payload():
                    if attachment.get_content_type() == 'text/plain':
                        break
                    attachment_content = attachment.get_payload(decode=True)

                    hash_object = hashlib.md5(attachment_content)
                    attHash = hash_object.hexdigest()
                    msg_date_str = msg_date.strftime("%Y%m%d-%H%M")

                    #Adds a unique identifier to the message YYYYMMDD-HHMM-HashOfTheMessageOfTheFile.data
                    file_name = msg_date_str + "-" + attHash + ".data"

                    path = "{}/{}".format(OUTPUT_PATH,file_name)
                    f = open(path, 'wb')
                    f.write(attachment_content)
                    f.close()

                    #Upload attachment to GCS
                    #transfer = GCSTransfer(to, msg_date.strftime("%Y-%m-%d"))
                    #path = transfer.local_transfer(att_name, content)

    def connect(self):
        #Implement a basic retry mechanism
        while not self.zero_mails:
            try:
                self.establish_connection()
            except Exception as err:
                if self.count>0:
                    self.count-=self.slice_size
                print(err)
                seconds=10
                print "Retrying in {} seconds".format(seconds)
                time.sleep(seconds)

    def establish_connection(self):
        print 'Connects to GMAIL imap'
        imap_connection = imaplib.IMAP4_SSL('imap.gmail.com')

        try:
            print "Login the account <%s>" % (self.account)
            if self.passwd is None:
                self.passwd = getpass.getpass()
            status, data = imap_connection.login(self.account, self.passwd)
        except imaplib.IMAP4.error as err:
            print(err)
            logging.error("LOGIN FAILED!!! ")
            sys.exit(1)

        print ">> (%s, %s)" % (status, data)

        status, mailboxes = imap_connection.list()
        if status == 'OK':
            print "Mailboxes:"
            for mailbox in mailboxes:
                print '>> List mailboxes:\n', mailbox

        print 'Checking folder ', self.folder
        status, data = imap_connection.select('"%s"' % (self.folder))
        if status == 'OK':
            print 'Processing mailbox...\n'
            self.process_mailbox(imap_connection)
            imap_connection.close()
        else:
            print 'ERROR: Unable to open mailbox ', self.folder, ' - ', status

        imap_connection.logout()




#------------------- MAIN RECEPTIONS -------------------

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def main(account, folder, start_date, end_date):
    #uncomment this if you want to try the reconnection
    # socket.setdefaulttimeout(10)
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    imap = IMAP4Connection(account, folder, start_date, end_date)
    imap.connect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--account",
                        help="A valid account email to download the attachments.",
                        required=True)
    parser.add_argument("-f", "--folder",
                        help="The path to the label where the emails can be found.",
                        required=True)
    parser.add_argument("-s","--start_date",
                        help="The date after you want to get the emails.",
                        required=False)
    parser.add_argument("-e","--end_date",
                        help="The date before you want to get the emails.",
                        required=False)
    args = parser.parse_args()
    if args.start_date != None:
        validate_date(args.start_date)
    if args.end_date != None:
        validate_date(args.end_date)
    startTime = datetime.now()
    print datetime.now() - startTime
    main(**vars(args))
    print(datetime.now() - startTime)

