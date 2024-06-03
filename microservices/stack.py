from aws_cdk import (
    Stack
)
from constructs import Construct
from microservices.api_gateway.infrastructure import MssApiGateway
from microservices.database.infrastructure import MssDatabase
from microservices.lambda_layers.infrastructure import MssLambdaLayers
from microservices.lambda_runtimes.infrastructure import MssLambdaRuntimes

class MicroservicesSampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        database = MssDatabase(self, "Database")
        lambda_layers = MssLambdaLayers(self, "LambdaLayers")
        lambda_runtimes = MssLambdaRuntimes(self, "LambdaRuntimes", productTable=database.productTable, 
            productTablePrimaryKey=database.productTablePrimaryKey,
            boto3Layer=lambda_layers.boto3Layer)
        api_gateway = MssApiGateway(self, "ApiGateway", productFunction=lambda_runtimes.productFunction)
