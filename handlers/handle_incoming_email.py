import logging

from google.appengine.api.mail import Attachment
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class VmsGCSUploaderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logger.info("Received a message from: " + mail_message.sender)

        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        msg_date = html_bodies.date
        msg_date = msg_date.strftime("%Y%m%d-%H%M")

        for body in html_bodies:
            decoded_html = body.decode()
            logger.info("Html body of length %d.", len(decoded_html))
            logger.info("Html body %s.", decoded_html)

        attachments = main_message.attachments
        logger.info("Html attachments of length %d.", len(attachments))
        for attachment in attachments:
            logger.info("Attachment %s.", attachment)
            #Adds a unique identifier to the message YYYYMMDD-HHMM-HashOfTheMessageOfTheFile.data
            att_nam = msg_date + "-" + attachment + ".data"
            logger.info("Attachment name %s.", att_name)
            #Upload attachment to GCS
            # GCSTransfer()

        #TODO remove, just for debugging
        for content_type, body in plaintext_bodies:
            plaintext = body.decode()
            logger.info("Plain text body of length %d.", len(plaintext))
            logger.info("Plain text body %s.", plaintext)


app = webapp2.WSGIApplication([VmsGCSUploaderHandler.mapping()], debug=True)
