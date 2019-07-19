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
        logging.info("Received a message from: %s", mail_message.sender)
        logging.info("The email subject: %s", mail_message.subject)
        to_addresses = str.join(str(mail_message.to), ', ')
        logging.info("The email was addressed to: %s", to_addresses)

        try:
            mail_bodies = mail_message.bodies("text/plain")
            for content_type, body in mail_bodies:
                logging.debug(
                    "Processing mail body with content type %s", content_type)
                text = body.decode()
                logging.debug("The mail body is [%s]", text)
        except:
            logging.exception("Unable to read the mail body")

        msg_date = datetime.now()

        if not hasattr(mail_message, 'attachments'):
            logging.info("The email has no attachments, skipping")
            return

        attachments = mail_message.attachments
        if len(attachments) > 0:
            logging.info("Email has attachments")
        for attachment in attachments:
            logging.info("Attachment filename %s.", attachment.filename)
            att_content = attachment.payload
            logging.info("Attachment payload %s.", att_content)

            hash_object = hashlib.md5(att_content.payload)
            attHash = hash_object.hexdigest()
            msg_date_str = msg_date.strftime("%Y%m%d")

            # Adds a unique identifier to the message YYYYMMDD-HashOfTheMessageOfTheFile.data
            att_name = msg_date_str + "-" + attHash + ".data"
            logging.info("Writting the file %s.", att_name)
            # Upload attachment to GCS
            transfer = GCSTransfer(to_addresses, msg_date.strftime("%Y-%m-%d"))
            try:
                path = transfer.transfer(att_name, att_content.payload.decode())
            except ValueError as ve:
                self.response.set_status(409)
                self.response.write(str(ve))


app = webapp2.WSGIApplication([VmsGCSUploaderHandler.mapping()], debug=True)
