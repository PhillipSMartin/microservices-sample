import os

from aws_cdk import (
        aws_lambda as _lambda,
        aws_lambda_python_alpha as _lambda_python
)
from aws_cdk.aws_dynamodb import (Table)
from constructs import Construct

class MssLambdaRuntimes(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)  

        self.productFunction = self.create_product_function(kwargs["productTable"], kwargs["boto3Layer"])
        self.basketFunction = self.create_basket_function(kwargs["basketTable"], kwargs["boto3Layer"])
        self.orderFunction = self.create_order_function(kwargs["orderTable"], kwargs["boto3Layer"])

    def create_product_function(self, productTable: Table, layer: _lambda.ILayerVersion):
        productFunction = _lambda_python.PythonFunction(
            self, 'productLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_10,
            index='index.py',
            handler='handler',
            entry=os.path.join(os.path.dirname(__file__) + '/product'),
            environment={ 'DYNAMODB_TABLE_NAME': productTable.table_name, 
                         'PRIMARY_KEY': productTable.schema().partition_key.name },
            layers=[layer],
            function_name="ProductFunction"
        )

        productTable.grant_read_write_data(productFunction)
        return productFunction
    
    def create_basket_function(self, basketTable: Table, layer: _lambda.ILayerVersion):
        basketFunction = _lambda_python.PythonFunction(
            self, 'basketLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_10,
            index='index.py',
            handler='handler',
            entry=os.path.join(os.path.dirname(__file__) + '/basket'),
            environment={ 'DYNAMODB_TABLE_NAME': basketTable.table_name, 
                         'PRIMARY_KEY': basketTable.schema().partition_key.name },
            layers=[layer],
            function_name="BasketFunction"
        )

        basketTable.grant_read_write_data(basketFunction)
        return basketFunction

    def create_order_function(self, orderTable: Table, layer: _lambda.ILayerVersion):
        orderFunction = _lambda_python.PythonFunction(
            self, 'orderLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_10,
            index='index.py',
            handler='handler',
            entry=os.path.join(os.path.dirname(__file__) + '/order'),
            environment={ 'DYNAMODB_TABLE_NAME': orderTable.table_name, 
                         'PARTITION_KEY': orderTable.schema().partition_key.name, 
                         'SORT_KEY': orderTable.schema().sort_key.name },
            layers=[layer],
            function_name="OrderFunction"
        )

        orderTable.grant_read_write_data(orderFunction)
        return orderFunction
