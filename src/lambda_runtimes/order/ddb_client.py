import boto3
import os

# Access DynamoDB table
ddb_resource = boto3.resource('dynamodb')
order_table = ddb_resource.Table(os.getenv('DYNAMODB_TABLE_NAME'))
user_name = os.getenv('PARTITION_KEY')
order_date = os.getenv('SORT_KEY')