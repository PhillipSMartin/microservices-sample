from botocore.exceptions import ClientError
from decimal import Decimal
from typing import Any, Dict

import ddb_client as db
import event_bridge_client as eb
import logging
import simplejson as json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

GET = "GET"
POST = "POST"
DELETE = "DELETE"
CHECKOUT_PATH = "/basket/checkout"


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
            if event.get('pathParameters') and 'userName' in event['pathParameters']:
                body = get_basket(event['pathParameters']['userName'])
            else:
                body = get_all_baskets()

        elif http_method == POST:
            if event.get('path') == CHECKOUT_PATH:
                body = checkout_basket(event)
            else:
                body = create_basket(event)

        elif http_method == DELETE:
            if event.get('pathParameters') and 'userName' in event['pathParameters']:
                body = delete_basket(event['pathParameters']['userName'])
            else:
                raise ValueError("userName must be specified on a DELETE request")

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
    
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Failed to perform operation",
                'errorMsg': str(e)
            })
        }
        logger.error("response: %s", json.dumps(response))
        return response

def get_basket(user_name: str) -> Dict[str, Any]:
    """
    Retrieve a basket for a given user.

    Parameters:
    user_name (str): The username whose basket is to be retrieved.

    Returns:
    dict: A dictionary representing the basket.
    """

    logger.info('get_basket, user_name: %s', user_name)

    try:
        params = {
            'Key': { db.basket_key: user_name }
        }
        response = db.basket_table.get_item(**params)      
        item = response.get('Item')
        
        logger.info('get_basket, result: %s', json.dumps(item))       
        return item if item else {}

    except ClientError as e:
        logger.error("ClientError: %s", e.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise


def get_all_baskets() -> Dict[str,Any]:
    """
    Retrieve all baskets.

    Returns:
    dict: A dictionary containing all baskets.
    """

    logger.info("get_all_baskets")

    try:
        response = db.basket_table.scan()      
        items = response.get('Items', {})
        
        logger.info('get_all_baskets, result: %s', json.dumps(items)) 
        return items

    except ClientError as e:
        logger.error("ClientError: %s", e.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise


def create_basket(event: Dict[str,Any]) -> Dict[str,Any]:
    """
    Create a new basket.

    Parameters:
    event (dict): The event containing basket data.

    Returns:
    dict: The result of the create operation.
    """
    
    logging.info('create_basket')

    try:
        basket_request = json.loads(event['body'], parse_float=Decimal)
        logging.info('create_basket, request: %s', json.dumps(basket_request))
 
        params = {
            'Item': basket_request
        }
        create_result = db.basket_table.put_item(**params)       
 
        logging.info('create_basket, result: %s', json.dumps(create_result))      
        return create_result

    except ClientError as e:
        logger.error("ClientError: %s", e.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise


def delete_basket(user_name: Dict[str,Any]) -> Dict[str,Any]:
    """
    Delete a basket for a given user.

    Parameters:
    user_name (str): The username whose basket is to be deleted.

    Returns:
    dict: The result of the delete operation.
    """
    
    logging.info('delete_basket, user_name: %s', user_name)

    try:
        params = {
            'Key': { db.basket_key: user_name }
        }
        delete_result = db.basket_table.delete_item(**params)       

        logging.info('delete_basket, result: %s', json.dumps(delete_result)) 
        return delete_result

    except ClientError as e:
        logger.error("ClientError: %s", e.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise


def checkout_basket(event: Dict[str,Any]) -> Dict[str,Any]:
    """
    Checkout a basket for a given user.

    Parameters:
    event (dict): The event containing checkout data.

    Returns:
    dict: The result of the checkout operation.
    """
    
    logger.info('checkout_basket')

    try:
        event_body = event.get('body', '{}')
        checkout_request = json.loads(event_body, parse_float=Decimal)
        logging.info('checkout_basket, request: %s', json.dumps(checkout_request))
        
        if not checkout_request or not checkout_request.get('userName'):
            raise ValueError(f'userName should exist in checkoutRequest: "{checkout_request}"')
        user_name = checkout_request.get('userName')

        basket = get_basket(user_name)
        if not basket:
            raise ValueError(f'No basket found for user "{user_name}"')
        
        checkout_payload = prepare_order_payload(checkout_request, basket)
        published_event = publish_checkout_basket_event(checkout_payload)
        delete_basket(user_name)

        logging.info('checkout_basket, result: %s', json.dumps(published_event))
        return published_event

    except ClientError as e:
        logger.error("ClientError: %s", e.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise
    
def prepare_order_payload(checkout_request: Dict[str,Any], basket: Dict[str,Any]) -> Dict[str,Any]:
    """
    Prepare the payload for order creation.

    Parameters:
    checkout_request (dict): The checkout request data.
    basket (dict): The user's basket data.

    Returns:
    dict: The prepared order payload.
    """
    
    logger.info("prepare_order_payload")

    if not ('items' in basket and isinstance(basket['items'], list) and basket['items']):
        raise ValueError( f'Basket should contain a list of items: "{basket}"')
    
    try:
        total_price = sum(Decimal(str(item['price'])) for item in basket['items'])
        checkout_request['totalPrice'] = total_price
        checkout_request.update(basket)
        logger.info('Successfully prepared order payload: %s', json.dumps(checkout_request))

        return checkout_request
       
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise
    
def publish_checkout_basket_event(checkout_payload: Dict[str,Any]) -> Dict[str,Any]:
    """
    Publish the checkout event to the event bus.

    Parameters:
    checkout_payload (dict): The payload for the checkout event.

    Returns:
    dict: The result of the event publish operation.
    """
    
    logger.info('publish_checkout_basket_event, payload: %s', json.dumps(checkout_payload))

    try:
        response = eb.client.put_events(
            Entries=[
                {
                    'Source': eb.event_source,
                    'Resources': [],
                    'Detail': json.dumps(checkout_payload),
                    'DetailType': eb.detail_type,
                    'EventBusName': eb.event_busname
                }
            ]
        )

        logger.info('publish_checkout_basket_event, response: %s', json.dumps(response))
        return response
    
    except ClientError as e:
        logger.error("ClientError: %s", e.response['Error']['Message'])
        raise
    except Exception as e:
        logger.error("Exceptions: %s", str(e))
        raise
