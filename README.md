# gae-mail-attachment-to-gcs
Process inbound messages from VMS

Handles the incoming email that match for a specific email address and execute a script to read the attachment and upload it to GCS.
This project runs under GAE standard environement with python 2.7

## Requirements

This application requires some third-praty libraries.
They are installed under the `lib/` folder.

- `google-cloud-storage`: To storage the attachment in the GCS.

- `requests-toolbelt`: To support an error uploading the file to GCS.

## Configuration

The file `reception.cfg` under the directory `config` declares the configuration of the project.

* BUCKET: Required. GCS bucket where to be stored the attachments.
* DIRECTORY: Required. GCS directory in bucket where the attachment will be saved.
