import os

from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _lambda_python
)
from constructs import Construct

class MssLambdaLayers(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.boto3Layer = _lambda_python.PythonLayerVersion(
            self, 'Boto3Layer',
            entry=os.path.join(os.path.dirname(__file__) + '/boto3'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_10],
            layer_version_name="Boto3Layer"
        )