from botocore.exceptions import ClientError
from datetime import datetime
from typing import Any, Dict

import ddb_client as db
import logging
import os
import simplejson as json

logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

GET = "GET"


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for the AWS Lambda function.

    Parameters:
    event (dict): The event triggering the Lambda function.
    context: The context in which the Lambda function is called.

    Returns on syncthronous invocation:
    dict: The response object containing statusCode and body.
    """
 
    logger.info("request: %s", json.dumps(event))

    if event.get('detail-type'):
        try:
            event_bridge_invocation(event)

        # errors should send event to dead-letter queue
        except ClientError as e:
            logger.error("Client Error: %s", e.response["Error"]["Message"])
            raise
  
        except Exception as e:
            logger.error("Exception: %s", str(e))
            raise  

    else:
        try:
            body = api_gateway_invocation(event) 
            response = {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Successfully finished operation',
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
    

def event_bridge_invocation(event: Dict[str, Any]) -> None:
    """
    Handle async invocation from EventBridge.

    Parameters:
    event (dict): The event containing order data.
    """
    logger.debug('event_bridge_invocation')
    create_order(event.get("detail", {}))


def api_gateway_invocation(event: Dict[str, Any]) -> Dict[str, Any]: 
    """
    Handle sync invocation from ApiGateway.

    Parameters:
    event (dict): The event containing order data.

    Returns:
    dict: The result of the operation.
    """    
    logger.debug('api_gateway_invocation') 

    http_method = event.get('httpMethod')
    body = None
    
    if http_method == GET:
        if event.get('pathParameters') and db.order_date in event['pathParameters']:
            body = get_order(event['pathParameters'][db.order_date])
        else:
            body = get_all_orders()

    else:
        raise ValueError(f"Unsupported route: \"{http_method}\"")
    
    return body


def create_order(basket_checkout_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new order.

    Parameters:
    event (dict): order data.

    Returns:
    dict: The result of the create operation.
    """
    logger.debug("create_order")

    now = datetime.now()
    basket_checkout_request["orderDate"] = now.isoformat()
    logger.info('create_order, request: %s', json.dumps(basket_checkout_request))

    params = {
        'Item': basket_checkout_request
    }
    create_result = db.order_table.put_item(**params)       

    logger.info('create_order, result: %s', json.dumps(create_result))      
    return create_result


def get_order(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve an order for a given user name and order date.

    Parameters:
    event: A dictionary representing the order request.

    Returns:
    dict: A dictionary representing the order.
    """
    logger.debug('get_order')

    if not db.user_name in event.get("pathParameters", {}):
        raise ValueError("Path must include user name")
    if not db.order_date in event.get("queryStringParameters", {}):
        raise ValueError(f"Query parameters must include {order_date}")
    
    user_name = event["pathParameters"][db.user_name]
    order_date = event["queryStringParameters"][db.order_date]                                  
    params = {
        'KeyConditionExpression': { f"{db.user_name} = ':user_name' and {db.order_date} = ':order_date'" },
        'ExpressionAttributeValues': {
            ":user_name": { "S": user_name },
            ":order_date": { "S": order_date }
       }
    }

    response = db.product_table.query(**params)     
    items = response.get('Items', [])       

    logger.info('get_product_by_category, return: %s', json.dumps(items))
    return items


def get_all_orders() -> Dict[str,Any]:
    """
    Retrieve all orders.

    Returns:
    dict: A dictionary containing all orders.
    """
    logger.debug("get_all_orders")

    response = db.order_table.scan()      
    items = response.get('Items', [])
    
    logger.info('get_all_orders, result: %s', json.dumps(items)) 
    return items
 