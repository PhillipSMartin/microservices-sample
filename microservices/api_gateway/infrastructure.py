from aws_cdk import (
    aws_apigateway as api
)

from constructs import Construct

class MssApiGateway(Construct) :
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.productApi = api.LambdaRestApi(self, 'productApi',
            rest_api_name='Product Service',
            handler=kwargs["productFunction"],
            proxy=False
        )
        
        product = self.productApi.root.add_resource('product')
        product.add_method('GET') # GET /product
        product.add_method('POST') # POST / product

        singleProduct = product.add_resource('{id}') # product/{id}
        singleProduct.add_method('GET') # GET /product/{id}
        singleProduct.add_method('PUT') # PUT /product/{id}
        singleProduct.add_method('DELETE') # DELETE /product/{id}