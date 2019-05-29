# IMAP Readme

## Requirements

 - Gmail account
 - Configure the [`App passwords`](https://support.google.com/accounts/answer/185833)
    `App passwords` let you sign in to your Google Account from apps on devices that don't support 2-Step Verification. You'll only need to enter it once so you don't need to remember it.

## How to run

This is an isolated program to process all the emails from an email account and that belongs to a email label.
The arguments are:
 - `account`: Required. The email account that contains the emails.
 - `folder`: Required. The folder that contains the emails.
 - `start_date`: Optional. Messages whose internal date is within or later than the specified date (format YYYY-MM-DD).
 - `end_date`: Optional. Messages whose internal date is earlier than the specified date (format YYYY-MM-DD).

Example:
```bash
$ python ./imap/read.py --account matias@globalfishingwatch.org -f PANAMA -s 2019-04-16 -e 2019-04-17
```
