import boto3
import os

# Access DynamoDB table
ddb_resource = boto3.resource('dynamodb')
basket_table = ddb_resource.Table(os.getenv('DYNAMODB_TABLE_NAME'))
basket_key = os.getenv('PRIMARY_KEY')