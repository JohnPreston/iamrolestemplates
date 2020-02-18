"""
Generates the Trust Policy for the IAM role
"""

from troposphere import Sub
from troposphere.iam import Policy


def generate_assume_role_policy(remote_accounts, **kwargs):
    """
    Generates the IAM Role Assume policy document
    """
    use_mfa = True
    if 'UseMfa' in kwargs.keys() and not bool(kwargs['UseMfa']):
        use_mfa = False
    mfa_age = 43200
    if 'MfaAge' in kwargs.keys():
        mfa_age = kwargs['MfaAge']
    policy_document = {
        "Version": "2012-10-17",
        "Statement": []
    }
    statement = {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
            "AWS": [
                Sub(f"arn:${{AWS::Partition}}:iam::{account}:root")
                for account in remote_accounts
            ]
        }
    }
    mfa_condition = {
        "Bool": {
            "aws:MultiFactorAuthPresent": "true",
            "aws:SecureTransport": "true"
        },
        "NumericLessThan": {"aws:MultiFactorAuthAge": mfa_age}
    }
    if use_mfa:
        statement['Condition'] = mfa_condition
    policy_document['Statement'].append(statement)
    return policy_document
