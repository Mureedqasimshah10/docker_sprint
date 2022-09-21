import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk.assertions import Match
import pytest

from sprint4.sprint4_stack import Sprint4Stack

# Pytest fixture
# https://docs.pytest.org/en/6.2.x/fixture.html
@pytest.fixture
def test_app():
    app = core.App()
    stack = Sprint4Stack(app, "sprint4")
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.assertions/Template.html
    template = assertions.Template.from_stack(stack)
    return template
    

def test_to_json(test_app):
    # Assert that the CloudFormation template deserialized into an object
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.to_json
    test_app.to_json()

def test_lambda_created(test_app):
    # Assert that we have created 2 Lambda
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.resource_count_is
    test_app.resource_count_is("AWS::Lambda::Function", 3)

def test_subscription_created(test_app):
    # Assert that we have created 2 subscriptions
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.resource_count_is
    test_app.resource_count_is("AWS::SNS::Subscription", 2)

def test_table_created(test_app):
    # Assert that we have created a table
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.resource_count_is
    test_app.resource_count_is("AWS::DynamoDB::Table", 2)

def test_role_created(test_app):
    # Assert that role has same properties
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.has_resource_properties
    test_app.has_resource_properties(
        "AWS::IAM::Role",
            {
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            "",
                            [
                                "arn:",
                                {
                                "Ref": "AWS::Partition"
                                },
                                ":iam::aws:policy/CloudWatchFullAccess"
                                ]
                            ]
                        },
                {
                    "Fn::Join": [
                    "",
                    [
                        "arn:",
                        {
                        "Ref": "AWS::Partition"
                        },
                        ":iam::aws:policy/AmazonDynamoDBFullAccess"
                        ]
                    ]
                }
            ]
        }
    )

def test_alarm_composite_key_created(test_app):
    # Assert that we have composite keys in Alarm table with same name
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.has_resource_properties
    test_app.has_resource_properties(
        "AWS::DynamoDB::Table",
            {
                "KeySchema": [
                   {
                     "AttributeName": "MetricName",
                     "KeyType": "HASH"
                   },
                   {
                     "AttributeName": "Timestamp",
                     "KeyType": "RANGE"
                   }
                ],
            }
    )


def test_url_partition_key_created(test_app):
    # Assert that we have partition key in URL table with same name
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.has_resource_properties
    test_app.has_resource_properties(
        "AWS::DynamoDB::Table",
            {
                "KeySchema": [
                   {
                     "AttributeName": "linkID",
                     "KeyType": "HASH"
                   },
                ],
            }
    )



def test_lambda_subscription_created(test_app):
    # Assert that we have subscription protocol for lambda
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.has_resource_properties
    test_app.has_resource_properties("AWS::SNS::Subscription", {"Protocol": "lambda"})


def test_email_subscription_created(test_app):
    # Assert that we have subscription protocol for email
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.has_resource_properties
    test_app.has_resource_properties("AWS::SNS::Subscription", {"Protocol": "email"})
    

def test_rule_created(test_app):
    # Assert that we have same properties for rule
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html#aws_cdk.assertions.Template.has_resource_properties
    test_app.has_resource_properties(
        "AWS::Events::Rule",
            {
                "State": "ENABLED",
                "Targets": [
                    {
                        "Arn": {
                            "Fn::GetAtt": [
                                "WHFunctions1AE513AC",
                                "Arn"
                            ]
                        },
                        "Id": "Target0"
                    }
                ]
            }
        )
