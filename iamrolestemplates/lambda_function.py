
import os
import re
import boto3
from datetime import datetime as dt
from troposphere import (
    Template
)


from iamrolestemplates.roles import (
    add_administrator_role,
    add_support_role
)

def init_template(description=None):
    """
    Initialize the template
    """
    template = Template(description)
    template.add_metadata({
        'GeneratedOn': dt.utcnow().isoformat()
    })
    return template

ACCOUNT_ID_PAT = re.compile(r'([0-9]{12})')


def upload_template_to_s3(template, bucket_name, session=None, file_name=None):
    """
    Function to upload the template file to S3.
    :param:template: Troposphere Template()
    :param:bucket_name: String of the bucket name
    :param:session: boto3 session to build the client
    :param:file_name: optional override name for file
    :return: S3 File URL
    """
    
    file_key = dt.utcnow().strftime('%Y/%m/%d/%H-%M')
    if not file_name:
        file_name = 'iam_roles.json'
    s3_path = f"{file_key}/{file_name}"
    if not session:
        client = boto3.client('s3')
    else:
        client = session.client('s3')
    try:
        client.put_object(
            Bucket=bucket_name,
            Body=template.to_json(),
            Key=s3_path,
            ContentEncoding='utf-8',
            ContentType='application/json',
            ServerSideEncryption='AES256'
        )
        return f"s3://{bucket_name}/{s3_path}"
    except Exception as e:
        print(e)


def define_bucket_name(event):
    """
    Defines the bucket name from either default, or ENV VAR or from event
    """
    bucket_name = 'lambda-my-aws-cfn-templates-eu-west-1'
    if 'BUCKET_NAME' in os.environ.keys():
        bucket_name = os.environ['BUCKET_NAME']
    elif 'BucketName' in event.keys():
        bucket_name = event['BucketName']
    return bucket_name


def lambda_handler(event, context):
    """
    Lambda function entry point.
    Requires event['AccountIds'] present.
    """
    
    if not 'AccountIds' in event.keys():
        raise ValueError(f"Function did not receive any account ids")
        
    elif not isinstance(event['AccountIds'], list):
        raise TypeError('AccountIds has to be of type', list)
    
    elif not event['AccountIds']:
        raise ValueError('AccountIds list is empty')
        
    for account_id in event['AccountIds']:
        if not ACCOUNT_ID_PAT.findall(account_id):
            raise ValueError(f"AccountID {account_id} is not valid: [0-9]{{12}}")
    
    options = {}
    upload = True
    bucket_name = define_bucket_name(event)
    description = "Lambda generated template"
    if 'Description' in event.keys():
        description = event['Description']
    if 'Options' in event.keys():
        options = event['Options']
    template = init_template(description)
    add_administrator_role(template, ['123456789012'], **options)
    add_support_role(template, ['12345678912'], **options)
    if 'Upload' in event.keys() and not event['Upload']:
        upload = False
    
    if upload:
        return upload_template_to_s3(template, bucket_name)
