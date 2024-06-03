from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as db
)
from constructs import Construct


class MssDatabase(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.productTablePrimaryKey = "id"
        self.productTable = db.Table(
            self, 'product',
            partition_key=db.Attribute(
                name=self.productTablePrimaryKey,
                type=db.AttributeType.STRING
            ),
            table_name= 'product',
            removal_policy= RemovalPolicy.DESTROY,
            billing_mode= db.BillingMode.PAY_PER_REQUEST         
        )
