from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from ddb_client import ddb_client
import json
import os
import uuid


def handler(event, context):
    print("request:", json.dumps(event, indent=2))

    try:
        body = None

        http_method = event.get('httpMethod')
        
        if http_method == "GET":
            if event.get('queryStringParameters') is not None:
                body = get_product_by_category(event)
            elif event.get('pathParameters') is not None:
                body = get_product(event['pathParameters']['id'])
            else:
                body = get_all_products()
        elif http_method == "POST":
            body = create_product(event)
        elif http_method == "DELETE":
            body = delete_product(event['pathParameters']['id'])
        elif http_method == "PUT":
            body = update_product(event)
        else:
            raise ValueError(f"Unsupported route: \"{http_method}\"")

        print(body)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully finished operation: "{http_method}"',
                'body': body
            })
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Failed to perform operation",
                'errorMsg': str(e),
                'errorStack': e.__traceback__
            })
        }


def get_product(product_id):
    print(f'getProduct, productid: "{product_id}"')

    try:
        params = {
            'TableName': os.getenv('DYNAMODB_TABLE_NAME'),
            'Key': {
                os.getenv('PRIMARY_KEY'): {'S': product_id}
            }
        }

        response = ddb_client.get_item(**params)
        
        item = response.get('Item')
        print(item)
        
        if item:
            return {k: v for k, v in item.items()}
        else:
            return {}

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def get_all_products():
    print("getAllProducts")

    try:
        params = {
            'TableName': os.getenv('DYNAMODB_TABLE_NAME')
        }

        response = ddb_client.scan(**params)
        
        items = response.get('Items')
        print(items)
        
        if items:
            return [{k: v for k, v in item.items()} for item in items]
        else:
            return {}

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def create_product(event):
    print(f'createProduct, event: "{event}"')

    try:
        product_request = json.loads(event['body'])
        product_id = str(uuid.uuid4())
        product_request[os.getenv('PRIMARY_KEY')] = product_id

        params = {
            'TableName': os.getenv('DYNAMODB_TABLE_NAME'),
            'Item': {k: {'S': v} if isinstance(v, str) else {'N': str(v)} for k, v in product_request.items()}
        }

        create_result = ddb_client.put_item(**params)
        
        print(create_result)
        return create_result

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def delete_product(product_id):
    print(f'deleteProduct, productid: "{product_id}"')

    try:
        params = {
            'TableName': os.getenv('DYNAMODB_TABLE_NAME'),
            'Key': {
                os.getenv('PRIMARY_KEY'): {'S': product_id}
            }
        }

        delete_result = ddb_client.delete_item(**params)
        
        print(delete_result)
        return delete_result

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def update_product(event):
    print(f'updateProduct, event: "{event}"')

    try:
        request_body = json.loads(event['body'])
        obj_keys = list(request_body.keys())
        
        update_expression = "SET " + ", ".join([f"#key{index} = :value{index}" for index in range(len(obj_keys))])
        expression_attribute_names = {f"#key{index}": key for index, key in enumerate(obj_keys)}
        expression_attribute_values = {f":value{index}": {'S': value} if isinstance(value, str) else {'N': str(value)} for index, (key, value) in enumerate(request_body.items())}

        params = {
            'TableName': os.getenv('DYNAMODB_TABLE_NAME'),
            'Key': {
                os.getenv('PRIMARY_KEY'): {'S': event['pathParameters']['id']}
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeNames': expression_attribute_names,
            'ExpressionAttributeValues': expression_attribute_values
        }

        update_result = ddb_client.update_item(**params)
        
        print(update_result)
        return update_result

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e
    

def get_product_by_category(event):
    print(f"getProductByCategory, category: \"{event['queryStringParameters']['category']}\"")

    try:
        category = event['queryStringParameters']['category']
        
        params = {
            'TableName': os.getenv('DYNAMODB_TABLE_NAME'),
            'FilterExpression': 'contains (category, :category)',
            'ExpressionAttributeValues': {
                ':category': {'S': category}
            }
        }

        response = ddb_client.scan(**params)
        
        items = response.get('Items')
        print(items)
        
        return [item for item in items] if items else []

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e
     