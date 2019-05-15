import exceptions
from datetime import datetime
from utils.upload_gcs import GCSTransfer
import logging
import email.utils
import hashlib

from google.appengine.api.mail import Attachment
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2

class VmsGCSUploaderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        logging.info("The email subject: " + mail_message.subject)
        to_addresses = str.join(str(mail_message.to), ', ')
        logging.info("The email was addressed to: " + to_addresses)

        try:
            logging.info("The email was CC-ed to: " + str.join(str(mail_message.cc), ', '))
        except exceptions.AttributeError:
            logging.info("The email has no CC-ed recipients")

        msg_date = datetime.now()
        try:
            mail_date = mail_message.date
            logging.info("The email was send on: " + mail_date)
            #Gets the date with timezone
            mail_date_tz = email.utils.parsedate_tz(mail_date)
            #Gets the timestamp of tz and convert to date flating to UTC
            msg_date = datetime.utcfromtimestamp(email.utils.mktime_tz(mail_date_tz))
        except exceptions.AttributeError :
            logging.info("The email has no send date specified!!!")

        attachments = mail_message.attachments
        if len(attachments)>0:
            logging.info("Email has attachments")
        for attachment in attachments:
            logging.info("Attachment filename %s.", attachment.filename)
            att_content = attachment.payload
            logging.info("Attachment payload %s.", att_content)

            hash_object = hashlib.md5(att_content.payload)
            attHash = hash_object.hexdigest()
            msg_date_str = msg_date.strftime("%Y%m%d-%H%M")

            #Adds a unique identifier to the message YYYYMMDD-HHMM-HashOfTheMessageOfTheFile.data
            att_name = msg_date_str + "-" + attHash + ".data"
            logging.info("Writting the file %s.", att_name)
            #Upload attachment to GCS
            transfer = GCSTransfer(to_addresses)
            path = transfer.transfer(att_name, att_content.payload)


app = webapp2.WSGIApplication([VmsGCSUploaderHandler.mapping()], debug=True)
