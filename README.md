# gae-mail-attachment-to-gcs
Process inbound messages from VMS

Handles the incoming email that match for a specific email address and execute a script to read the attachment and upload it to GCS.
This project runs under GAE standard environement with python 2.7 reference notes https://cloud.google.com/appengine/docs/standard/python/concepts

## Requirements

This application requires some third-praty libraries.
They are installed under the `lib/` folder.

- `google-cloud-storage`: To storage the attachment in the GCS.

- `requests-toolbelt`: To support an error uploading the file to GCS.

If you need to add a new one, add it in `requirements.txt` and then run
```
$ pip install -t lib/ -r requirements.txt
```

## Configuration

The file `reception.cfg` under the directory `config` declares the configuration of the project.
The section indicates the mails account that will match with the `email to` field

* BUCKET: Required. GCS bucket where to be stored the attachments.
* DIRECTORY: Required. GCS directory in bucket where the attachment will be saved.

There is a DEFAULT section in case the email does not match any of available mail accounts.
