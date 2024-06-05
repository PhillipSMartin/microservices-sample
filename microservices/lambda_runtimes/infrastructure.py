import os

from aws_cdk import (
        aws_lambda as _lambda,
        aws_lambda_python_alpha as _lambda_python
)
from aws_cdk.aws_dynamodb import ITable
from constructs import Construct

class MssLambdaRuntimes(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)  

        self.productFunction = self.create_product_function(kwargs["productTable"], kwargs["productTablePrimaryKey"], kwargs["boto3Layer"])
        self.basketFunction = self.create_basket_function(kwargs["basketTable"], kwargs["basketTablePrimaryKey"], kwargs["boto3Layer"])

    def create_product_function(self, productTable : ITable, primaryKey : str, layer : _lambda.ILayerVersion):
        productFunction = _lambda_python.PythonFunction(
            self, 'productLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_10,
            index='index.py',
            handler='handler',
            entry=os.path.join(os.path.dirname(__file__) + '/product'),
            environment={ 'DYNAMODB_TABLE_NAME': productTable.table_name, 'PRIMARY_KEY': primaryKey },
            layers=[layer],
            function_name="ProductFunction"
        )

        productTable.grant_read_write_data(productFunction)
        return productFunction
    
    def create_basket_function(self, basketTable : ITable, primaryKey : str, layer : _lambda.ILayerVersion):
        basketFunction = _lambda_python.PythonFunction(
            self, 'basketLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_10,
            index='index.py',
            handler='handler',
            entry=os.path.join(os.path.dirname(__file__) + '/basket'),
            environment={ 'DYNAMODB_TABLE_NAME': basketTable.table_name, 'PRIMARY_KEY': primaryKey },
            layers=[layer],
            function_name="BasketFunction"
        )

        basketTable.grant_read_write_data(basketFunction)
        return basketFunction