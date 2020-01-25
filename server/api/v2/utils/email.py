import boto3
from enum import Enum
from flask import render_template
from premailer import transform

from app import app

class Template(Enum):
    DIGEST = 1
    VERIFY = 2

    @property
    def file(self):
        if self.value == Template.DIGEST.value:
            return "digest.html"
        elif self.value == Template.VERIFY.value:
            return "verify.html"

    @property
    def subject(self):
        if self.value == Template.DIGEST.value:
            return "Today's Dormspam Digest"
        elif self.value == Template.VERIFY.value:
            return "Verify your email to use dormsp.am"

def send_email(template, to_email, data):
    client = boto3.client(
                service_name="ses",
                region_name="us-east-1",
                aws_access_key_id=app.config["AWS_SES_ACCESS_KEY_ID"],
                aws_secret_access_key=app.config["AWS_SES_SECRET_ACCESS_KEY"])

    source = "dormsp.am <digest@dormsp.am>"

    destination = {
        "ToAddresses": [
            to_email
        ]
    }

    message = {
        "Subject": {
            "Data": template.subject
        },
        "Body": {
            "Html": {
                "Data": transform(render_template(template.file, **data))
            },
            "Text": {
                "Data": "hello"
            }
        }
    }

    client.send_email(Source=source, Destination=destination, Message=message)
