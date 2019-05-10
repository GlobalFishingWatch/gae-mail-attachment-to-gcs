import logging

from google.appengine.api.mail import Attachment
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2

class VmsGCSUploaderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)

        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        msg_date = html_bodies.date
        msg_date = msg_date.strftime("%Y%m%d-%H%M")

        for body in html_bodies:
            decoded_html = body.decode()
            logging.info("Html body of length %d.", len(decoded_html))
            logging.info("Html body %s.", decoded_html)

        attachments = main_message.attachments
        logging.info("Html attachments of length %d.", len(attachments))
        for attachment in attachments:
            logging.info("Attachment filename %s.", attachment.filename)
            logging.info("Attachment payload %s.", attachment.payload)
            #Adds a unique identifier to the message YYYYMMDD-HHMM-HashOfTheMessageOfTheFile.data
            att_nam = msg_date + "-" + attachment + ".data"
            logging.info("Attachment name %s.", att_name)
            #Upload attachment to GCS
            # GCSTransfer()

        #TODO remove, just for debugging
        for content_type, body in plaintext_bodies:
            plaintext = body.decode()
            logging.info("Plain text body of length %d.", len(plaintext))
            logging.info("Plain text body %s.", plaintext)


app = webapp2.WSGIApplication([VmsGCSUploaderHandler.mapping()], debug=True)
