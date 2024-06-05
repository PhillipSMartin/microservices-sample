from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as db
)
from constructs import Construct


class MssDatabase(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.productTable, self.productTablePrimaryKey = self.create_product_table();
        self.basketTable, self.basketTablePrimaryKey = self.create_basket_table();

    def create_product_table(self):
        productTable = db.Table(
            self, 'product',
            partition_key=db.Attribute(
                name="id",
                type=db.AttributeType.STRING
            ),
            table_name= 'product',
            removal_policy= RemovalPolicy.DESTROY,
            billing_mode= db.BillingMode.PAY_PER_REQUEST         
        )
        return productTable, "id"

    def create_basket_table(self):
        basketTable = db.Table(
            self, 'basket',
            partition_key=db.Attribute(
                name="userName",
                type=db.AttributeType.STRING
            ),
            table_name= 'basket',
            removal_policy= RemovalPolicy.DESTROY,
            billing_mode= db.BillingMode.PAY_PER_REQUEST         
        )
        return basketTable, "userName"
