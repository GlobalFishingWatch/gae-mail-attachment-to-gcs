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

FORMAT = '%(asctime)-15s - %(message)s'
OUTPUT_PATH = 'output'
logging.basicConfig(format=FORMAT)

def chunks(list, number_of_elements):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(list), number_of_elements):
        yield list[i:i + number_of_elements]

def _gmailTime2Internaldate(date_time):
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

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def process_mailbox(imap_connection, start_date, end_date):
    where=[]
    where.append('ALL')
    if start_date != None:
        starts = _gmailTime2Internaldate(time.mktime(datetime.strptime(start_date,"%Y-%m-%d").timetuple()))
        where.append('SINCE')
        where.append(starts)
    if end_date != None:
        ends = _gmailTime2Internaldate(time.mktime(datetime.strptime(end_date,"%Y-%m-%d").timetuple()))
        where.append('BEFORE')
        where.append(ends)
    print '>> ', where

    status, email_ids = imap_connection.search(None, *where)
    if status != 'OK':
        print "No messages found!"
        return

    total_emails=len(email_ids[0].split())
    print '>> Total emails to process ', total_emails if len(email_ids)>0 else 'Zero.'
    email_ids_list = email_ids[0].split()
    slice_size=100
    email_id_lists_chunked = list(chunks(email_ids_list, slice_size))

    count=0
    for i in xrange(len(email_id_lists_chunked)):
        old_counter=count
        count=count+len(email_id_lists_chunked[i])
        print "Fetching from {} to {} out of {} (slize = {}), be patient may take some time.".format(
                                                            old_counter,
                                                            count,
                                                            total_emails,
                                                            slice_size)
        email_ids_sub_list=email_id_lists_chunked[i]
        fetch_ids = ','.join(email_ids_sub_list)
        
        #Implement a basic retry mechanism
        while True:
            try:
                status, emails = imap_connection.fetch(fetch_ids, '(RFC822)')
                if status == 'OK':
                    break
            except Exception as err:
                print(err)
                seconds=10
                print "Retrying in {} seconds".format(seconds)
                time.sleep(seconds)
        
        print "Got {} emails.".format(len(emails)/2)
        
        for m in range(len(email_ids_sub_list)):
            msg = email.message_from_string(emails[m*2+0][1])
            decode = email.header.decode_header(msg['Subject'])[0]
            to = msg['To']
            date = msg['Date']

            subject = decode[0]
            #print '>> Message %s: %s, to: %s' % (i, subject, to)
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
                #print '>> ', attachment_content
                #print '>> ', file_name
                
                path = "{}/{}".format(OUTPUT_PATH,file_name)
                f = open(path, 'wb')
                f.write(attachment_content)
                f.close()
    
                #Upload attachment to GCS
                #transfer = GCSTransfer(to, msg_date.strftime("%Y-%m-%d"))
                #path = transfer.local_transfer(att_name, content)


def main(account, folder, start_date, end_date):
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    print 'Connects to GMAIL imap'
    imap_connection = imaplib.IMAP4_SSL('imap.gmail.com')

    try:
        print "Login the account <%s>" % (account)
        status, data = imap_connection.login(account, getpass.getpass())
    except imaplib.IMAP4.error as err:
        print(err)
        logging.error("LOGIN FAILED!!! ")
        sys.exit(1)

    print ">> (%s, %s)" % (status, data)

    status, mailboxes = imap_connection.list()
    if status == 'OK':
        print "Mailboxes:"
        for mailbox in mailboxes:
            print '>> ', mailbox

    print 'Checking folder ', folder
    status, data = imap_connection.select('"%s"' % (folder))
    if status == 'OK':
        print "Processing mailbox...\n"
        process_mailbox(imap_connection, start_date, end_date)
        imap_connection.close()
    else:
        print "ERROR: Unable to open mailbox ", folder, ' - ', status

    imap_connection.logout()

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
    main(args.account, args.folder, args.start_date, args.end_date)
    print(datetime.now() - startTime)

