from decimal import Decimal
from botocore.exceptions import ClientError
from ddb_client import (basket_table, basket_key)
import simplejson as json


def handler(event, context):
    print("request:", json.dumps(event))

    try:
        body = None

        http_method = event.get('httpMethod')
        
        if http_method == "GET":
            if event.get('pathParameters') is not None:
                body = get_basket(event['pathParameters']['userName'])
            else:
                body = get_all_baskets()

        elif http_method == "POST":
            if event.get('path') == "/basket/checkout":
                body = check_out_basket(event)
            else:
                body = create_basket(event)

        elif http_method == "DELETE":
            body = delete_basket(event['pathParameters']['userName'])

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
                'errorMsg': str(e)
            })
        }


def get_basket(user_name):
    print(f'getBasket, basketid: "{user_name}"')

    try:
        params = {
            'Key': {
                basket_key: user_name
            }
        }

        response = basket_table.get_item(**params)
        
        item = response.get('Item')
        print(item)
        
        if item:
            return item
        else:
           return {}

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def get_all_baskets():
    print("getAllBaskets")

    try:
        response = basket_table.scan()
        
        items = response.get('Items')
        print(items)
        
        if items:
            return items
        else:
            return {}

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def create_basket(event):
    print(f'createBasket, event: "{event}"')

    try:
        basket_request = json.loads(event['body'], parse_float=Decimal)

        params = {
            'Item': basket_request
        }

        create_result = basket_table.put_item(**params)
        
        print(create_result)
        return create_result

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def delete_basket(user_name):
    print(f'deleteBasket, basketid: "{user_name}"')

    try:
        params = {
            'Key': {
                basket_key: user_name
            }
        }

        delete_result = basket_table.delete_item(**params)
        
        print(delete_result)
        return delete_result

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        print(e)
        raise e


def check_out_basket(event):
    print(f'checkout basket, event: "{event}"')    