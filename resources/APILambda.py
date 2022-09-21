import json
import boto3
from botocore.exceptions import ClientError
import os
import constants as constants
from boto3.dynamodb.conditions import Key

# Get the service resource.
dynamodb = boto3.resource('dynamodb')

# set environment variable
tableName = os.environ["URL_TABLE"]
table = dynamodb.Table(tableName)


##################################################################################################################
#                                                   CRUD Operations                                              #
##################################################################################################################

def lambda_handler(event, context):
    # # Get the method
    method = event['httpMethod']
    body = event['body']

    #1. Get (Read) Item
    if method == 'GET':
        return get_url()
        
    #2. DELETE Item by Id    
    elif method == 'DELETE':
        # Get the id
        id_ = json.loads(body)['linkID']
        return delete_url(id_)
    
    #3. Post (Create) Item with Id
    #4. PUT (Update) Item by Id
    else:
        # Get the id and url
        id_ = json.loads(body)['linkID']
        url = json.loads(body)['url']
        
        return post_put_url(id_, url, method)


def get_url():
    response = table.scan()['Items']
    if response:
        return json_response(response)
    else:
        return json_response({"message": "URLs not found"})


def delete_url(id_):
    #3. DELETE Item by Id
    response = table.delete_item(
        Key={
            "linkID": str(id_)
        }
    )
    if response:
        return json_response({"message": "Successfully deleted URL from the table"})
    else:
        return json_response({"message": "URL not found"})


def post_put_url(id_, url, method):
    # add methods for CRUD operations [ create/update ]
    key = {
        "linkID": str(id_),
        "url": url
    }
    #3. Post (Create) Item with Id  -  key = {"linkID": 1, "url": "youtube.com" }
    if method == 'POST':
        try:
            response = table.put_item(
                Item=key,
                ConditionExpression='attribute_not_exists(linkID)'
            )
            if response:
                return json_response({"message": "Successfully added URL into the table"})
        # if link id already exits
        except ClientError as e:
            if e.response['Error']['Code']=='ConditionalCheckFailedException':
                return json_response({"message": "Link_ID already exits!"})
        
    # 4. PUT (Update) Item by Id
    elif method == 'PUT':
        response = table.update_item(
            Key={
                'linkID': str(id_)
            },
            UpdateExpression='SET #ui = :u',
            ConditionExpression='attribute_not_exists(deletedAt)',  # Do not update if deleted
            ExpressionAttributeValues={
                ':u': url
            },
            ExpressionAttributeNames={
                "#ui": "url"
            },
            ReturnValues="UPDATED_NEW"
        )
        if response:
            return json_response({"message": "Successfully updated URL in the table"})
        else:
            return json_response({"message": "URL not found"})
        
    # Note: You cannot use UpdateItem to update any primary key attributes.
    # Instead, you will need to delete the item, and then use PutItem to create a new item with new attributes
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.update_item

    else:
        return json_response({"message": "Invalid Method"})


def json_response(data):
    return {
        "statusCode": 200,
        "body": json.dumps(data),
        "headers": {'Content-Type': 'application/json'},
    }