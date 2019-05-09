# gae-mail-attachment-to-gcs
Process inbound messages from VMS

Handles the incoming email that match for a specific email address and execute a script to read the attachment and upload it to GCS.

## Configuration

The file `reception.cfg` under the directory `config` declares the configuration of the project.

* BUCKET: Required. GCS bucket where to be stored the attachments.
* DIRECTORY: Required. GCS directory in bucket where the attachment will be saved.
