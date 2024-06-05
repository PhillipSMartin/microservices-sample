import boto3
import os

# Access DynamoDB table
ddb_resource = boto3.resource('dynamodb')
product_table = ddb_resource.Table(os.getenv('DYNAMODB_TABLE_NAME'))
product_key = os.getenv('PRIMARY_KEY')