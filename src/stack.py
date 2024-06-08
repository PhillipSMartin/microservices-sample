from aws_cdk import (
    Stack
)
from constructs import Construct
from src.api_gateway.infrastructure import MssApiGateway
from src.database.infrastructure import MssDatabase
from src.event_bus.infrastructure import MssEventBus
from src.lambda_layers.infrastructure import MssLambdaLayers
from src.lambda_runtimes.infrastructure import MssLambdaRuntimes

class MicroservicesSampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        database = MssDatabase(self, "Database")
        lambda_layers = MssLambdaLayers(self, "LambdaLayers")
        lambda_runtimes = MssLambdaRuntimes(self, "LambdaRuntimes", 
            productTable=database.productTable, 
            basketTable=database.basketTable,
            orderTable=database.orderTable,
            boto3Layer=lambda_layers.boto3Layer)
        MssApiGateway(self, "ApiGateway", 
            productFunction=lambda_runtimes.productFunction,
            basketFunction=lambda_runtimes.basketFunction,
            orderFunction=lambda_runtimes.orderFunction)
        MssEventBus(self, "EventBus",
            publisherFunction=lambda_runtimes.basketFunction,
            targetFunction=lambda_runtimes.orderFunction)
