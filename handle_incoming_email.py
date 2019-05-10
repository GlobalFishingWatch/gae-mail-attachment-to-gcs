import logging
from datetime import datetime

from google.appengine.api.mail import Attachment
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2
import hashlib

class VmsGCSUploaderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        logging.info("The email subject: " + mail_message.subject)
        logging.info("The email was addressed to: " + str.join(str(mail_message.to), ', '))

        try:
            logging.info("The email was CC-ed to: " + str.join(str(mail_message.cc), ', '))
        except exceptions.AttributeError:
            logging.info("The email has no CC-ed recipients")

        msg_date = datetime.now()
        try:
            msg_date = mail_message.date
            logging.info("The email was send on: " + str(msg_date))
        except exceptions.AttributeError :
            logging.info("The email has no send date specified!!!")

        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        for body in html_bodies:
            logging.info("Html body %s.", body)
            num, decoded_html = body
            logging.info("Html body of length %d.", len(decoded_html))
            logging.info("Html body %s.", decoded_html)
            logging.info("Html body tupple %d.", body.decode())


        attachments = main_message.attachments
        logging.info("Html attachments of length %d.", len(attachments))
        for attachment in attachments:
            logging.info("Attachment filename %s.", attachment.filename)
            logging.info("Attachment payload %s.", attachment.payload)

            hash_object = hashlib.md5(bytearray(attachment.content))
            attHash = hash_object.hexdigest()
            msg_date_str = msg_date.strftime("%Y%m%d-%H%M")

            #Adds a unique identifier to the message YYYYMMDD-HHMM-HashOfTheMessageOfTheFile.data
            att_nam = msg_date_str + "-" + attHash + ".data"
            logging.info("Attachment name %s.", att_name)
            #Upload attachment to GCS
            # GCSTransfer()

        #TODO remove, just for debugging
        for content_type, body in plaintext_bodies:
            plaintext = body.decode()
            logging.info("Plain text body of length %d.", len(plaintext))
            logging.info("Plain text body %s.", plaintext)


app = webapp2.WSGIApplication([VmsGCSUploaderHandler.mapping()], debug=True)
