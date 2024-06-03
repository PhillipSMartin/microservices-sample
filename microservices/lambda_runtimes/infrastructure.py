import os

from aws_cdk import (
        aws_lambda as _lambda,
        aws_lambda_python_alpha as _lambda_python
)
from constructs import Construct

class MssLambdaRuntimes(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)  

        self.productFunction = _lambda_python.PythonFunction(
            self, 'productLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_10,
            index='index.py',
            handler='handler',
            entry=os.path.join(os.path.dirname(__file__) + '/product'),
            environment={ 'DYNAMODB_TABLE_NAME': kwargs["productTable"].table_name, 'PRIMARY_KEY': kwargs["productTablePrimaryKey"] },
            layers=[kwargs["boto3Layer"]],
            function_name="ProductFunction"
        )

        kwargs["productTable"].grant_read_write_data(self.productFunction)