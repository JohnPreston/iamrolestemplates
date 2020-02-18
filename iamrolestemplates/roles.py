"""
Generates the administrator role
"""

from troposphere.iam import (
    Role,
    Policy,
    PolicyType
)

from troposphere import (
    Sub, Ref
)

from iamrolestemplates.trust_policy import generate_assume_role_policy


ADMIN_MANAGED_POLICIES = [
    "arn:aws:iam::aws:policy/AdministratorAccess"
]


SUPPORT_MANAGED_POLICES = [
    "arn:aws:iam::aws:policy/job-function/SupportUser"
]


def add_administrator_role(template, account_ids, **kwargs):
    """
    Function to add the administrator
    """
    if not account_ids:
        raise ValueError(f"account_ids is an empty list. It must contain a list of account IDS")
    role = Role(
        'AdministratorRole',
        template=template,
        ManagedPolicyArns=ADMIN_MANAGED_POLICIES,
        AssumeRolePolicyDocument = generate_assume_role_policy(account_ids, **kwargs)
    )


def add_support_role(template, account_ids, **kwargs):
    """
    Functiont to add a support role to the IAM Roles template
    """
    role = Role(
        'SupportRole',
        template=template,
        ManagedPolicyArns=SUPPORT_MANAGED_POLICES,
        AssumeRolePolicyDocument = generate_assume_role_policy(account_ids, **kwargs)
    )
