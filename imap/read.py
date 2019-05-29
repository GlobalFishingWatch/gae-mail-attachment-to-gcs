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
import time

FORMAT = '%(asctime)-15s - %(message)s'
logging.basicConfig(format=FORMAT)

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

def process_mailbox(M, start_date, end_date):
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
    # status, data = M.search(None, "ALL")
    status, data = M.search(None, *where)
    if status != 'OK':
        print "No messages found!"
        return

    print '>> Total emails to process ', len(data[0]) if len(data)>0 else 'Zero.'

    for num in data[0].split():
        status, data = M.fetch(num, '(RFC822)')
        if status != 'OK':
            print "ERROR getting message", num
            return

        msg = email.message_from_string(data[0][1])
        decode = email.header.decode_header(msg['Subject'])[0]
        to = msg['To']
        date = msg['Date']

        # subject = unicode(decode[0])
        subject = decode[0]
        print '>> Message %s: %s, to: %s' % (num, subject, to)
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(date)
        msg_date = datetime.now()
        if date_tuple:
            msg_date = datetime.utcfromtimestamp(email.utils.mktime_tz(date_tuple))

        for attachment in msg.get_payload():
            if attachment.get_content_type() == 'text/plain':
                break
            att_content = attachment.get_payload(decode=True)

            hash_object = hashlib.md5(att_content)
            attHash = hash_object.hexdigest()
            msg_date_str = msg_date.strftime("%Y%m%d-%H%M")

            #Adds a unique identifier to the message YYYYMMDD-HHMM-HashOfTheMessageOfTheFile.data
            att_name = msg_date_str + "-" + attHash + ".data"
            content = att_content
            print '>> ', content
            print '>> ', att_name

            #Upload attachment to GCS
            transfer = GCSTransfer(to, msg_date.strftime("%Y-%m-%d"))
            path = transfer.local_transfer(att_name, content)


def main(account, folder, start_date, end_date):
    print 'Connects to GMAIL imap'
    M = imaplib.IMAP4_SSL('imap.gmail.com')

    try:
        print "Login the account <%s>" % (account)
        status, data = M.login(account, getpass.getpass())
    except imaplib.IMAP4.error as err:
        print(err)
        logging.error("LOGIN FAILED!!! ")
        sys.exit(1)

    print ">> (%s, %s)" % (status, data)

    status, mailboxes = M.list()
    if status == 'OK':
        print "Mailboxes:"
        for mailbox in mailboxes:
            print '>> ', mailbox

    print 'Checking folder ', folder
    status, data = M.select('"%s"' % (folder))
    if status == 'OK':
        print "Processing mailbox...\n"
        process_mailbox(M, start_date, end_date)
        M.close()
    else:
        print "ERROR: Unable to open mailbox ", folder, ' - ', status

    M.logout()

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
    main(args.account, args.folder, args.start_date, args.end_date)

