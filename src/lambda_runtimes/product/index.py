from botocore.exceptions import ClientError
from decimal import Decimal
from typing import Any, Dict

import ddb_client as db
import logging
import os
import simplejson as json
import uuid

logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for the AWS Lambda function.

    Parameters:
    event (dict): The event triggering the Lambda function.
    context: The context in which the Lambda function is called.

    Returns:
    dict: The response object containing statusCode and body.
    """
    logger.info("request: %s", json.dumps(event))

    try:
        body = None
        http_method = event.get('httpMethod')
        
        if http_method == GET:
            if event.get('queryStringParameters'):
                body = get_product_by_category(event)
            elif event.get('pathParameters') and db.product_key in event['pathParameters']:
                body = get_product(event['pathParameters'][db.product_key])
            else:
                body = get_all_products()

        elif http_method == POST:
            body = create_product(event)

        elif http_method == DELETE:
            if event.get('pathParameters') and db.product_key in event['pathParameters']:
                body = delete_product(event['pathParameters'][db.product_key])
            else:
                raise ValueError(f"{db.product_key} must be specified on a DELETE request")
 
        elif http_method == PUT:
            body = update_product(event)

        else:
            raise ValueError(f"Unsupported route: \"{http_method}\"")

        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully finished operation: "{http_method}"',
                'body': body
            })
        }
        logger.info("response: %s", json.dumps(response))
        return response
        
    except ClientError as e:
        error_msg = e.response["Error"]["Message"]
        logger.error("Client Error: %s", error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Failed to perform operation",
                'errorMsg': error_msg
            })
        }  
    
    except Exception as e:
        error_msg = str(e)
        logger.error("Exception: %s", error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Failed to perform operation",
                'errorMsg': error_msg
            })
        }


def get_product(product_id: str) -> Dict[str, Any]:
    """
    Retrieve a product for a given id.

    Parameters:
    product_id (str): The id of the product to be retrieved.

    Returns:
    dict: A dictionary representing the product.
    """
    logger.info('get_product, product_id: %s', product_id)

    params = {
        'Key': { db.product_key: product_id }
    }
    response = db.product_table.get_item(**params)       
    item = response.get('Item', {})

    logger.info('get_product, result: %s', json.dumps(item))       
    return item


def get_all_products() -> Dict[str,Any]:
    """
    Retrieve all products.

    Returns:
    dict: A dictionary containing all products.
    """
    logger.debug("get_all_products")

    response = db.product_table.scan()      
    items = response.get('Items', {})
    
    logger.info('get_all_products, result: %s', json.dumps(items)) 
    return items


def create_product(event: Dict[str,Any]) -> Dict[str,Any]:
    """
    Create a new product.

    Parameters:
    event (dict): The event containing product data.

    Returns:
    dict: The result of the create operation.
    """   
    logger.debug('create_product')

    product_request = json.loads(event['body'], parse_float=Decimal)
    product_id = str(uuid.uuid4())
    product_request[db.product_key] = product_id
    logger.info('create_product, request: %s', json.dumps(product_request))

    params = {
        'Item': product_request
    }
    create_result = db.product_table.put_item(**params)       

    logger.info('create_product, result: %s', json.dumps(create_result))      
    return create_result


def delete_product(product_id: Dict[str,Any]) -> Dict[str,Any]:
    """
    Delete a product for a given id.

    Parameters:
    product_id (str): The id of the product to be deleted.

    Returns:
    dict: The result of the delete operation.
    """
    logger.info('delete_product, product_id: %s', product_id)

    params = {
        'Key': { db.product_key: product_id }
    }
    delete_result = db.product_table.delete_item(**params)   

    logger.info('delete_product, result: %s', json.dumps(delete_result)) 
    return delete_result


def update_product(event: Dict[str,Any]) -> Dict[str,Any]:
    """
    Updaste a product.

    Parameters:
    event (dict): The event containing new product data.

    Returns:
    dict: The result of the create operation.
    """
    logger.debug('update_product')

    request_body = json.loads(event['body'], parse_float=Decimal)
    logger.info('update_product, request: %s', json.dumps(request_body))

    obj_keys = list(request_body.keys())      
    update_expression = "SET " + ", ".join([f"#key{index} = :value{index}" for index in range(len(obj_keys))])
    expression_attribute_names = {f"#key{index}": key for index, key in enumerate(obj_keys)}
    expression_attribute_values = {f":value{index}": {'S': value} if isinstance(value, str) else {'N': str(value)} for index, (key, value) in enumerate(request_body.items())}

    params = {
        'Key': { db.product_key: event['pathParameters'][db.product_key] },
        'UpdateExpression': update_expression,
        'ExpressionAttributeNames': expression_attribute_names,
        'ExpressionAttributeValues': expression_attribute_values
    }
    update_result = db.product_table.update_item(**params)
    
    logger.info('update_result, result: %s', json.dumps(update_result)) 
    return update_result
    

def get_product_by_category(event: Dict[str,Any]) -> Dict[str,Any]:
    """
    Get products belonging to a specified cateogry.

    Parameters:
    event (dict): The event with a '?category=' query parameter.

    Returns:
    dict: The products belonging to the specified category
    """
    logger.debug('get_product_by_category')

    if 'category' not in event['queryStringParameters']:
        raise ValueError('Query parameters on url must contain "category"')
    category = event['queryStringParameters']['category']
    logger.info('get_product_by_category, category:%s', category) 

    params = {
        'FilterExpression': 'contains (category, :category)',
        'ExpressionAttributeValues': { ':category': category }
    }

    response = db.product_table.scan(**params)     
    items = response.get('Items', {})       
    item_list = [item for item in items] if items else []

    logger.info('get_product_by_category, return: %s', json.dumps(item_list))
    return item_list
