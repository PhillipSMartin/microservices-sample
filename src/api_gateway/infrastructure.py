from aws_cdk import (
    aws_apigateway as api
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction

from constructs import Construct

class MssApiGateway(Construct) :
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.createProductApi(kwargs["productFunction"])
        self.createBasketApi(kwargs["basketFunction"])
        self.createOrderApi(kwargs["orderFunction"])

    def createProductApi(self, productFunction : PythonFunction):
        # Product microservices api gateway
        # root name = product

        # GET /product
        # POST /product

        # Single product with id parameter
        # GET /product/{id}
        # PUT /product/{id}
        # DELETE /product/{id}

        self.productApi = api.LambdaRestApi(self, 'productApi',
            rest_api_name='Product Service',
            handler=productFunction,
            proxy=False
        )
        
        product = self.productApi.root.add_resource('product')
        product.add_method('GET') # GET /product
        product.add_method('POST') # POST / product

        singleProduct = product.add_resource('{id}') # product/{id}
        singleProduct.add_method('GET') # GET /product/{id}
        singleProduct.add_method('PUT') # PUT /product/{id}
        singleProduct.add_method('DELETE') # DELETE /product/{id}

    def createBasketApi(self, basketFunction : PythonFunction):
        # Basket microservices api gateway
        # root name = basket

        # GET /basket
        # POST /basket

        # Single basket with userName parameter
        # GET /basket/{userName}
        # DELETE /basket/{userName}

        # POST /basket/checkout

        self.basketApi = api.LambdaRestApi(self, 'basketApi',
            rest_api_name='Basket Service',
            handler=basketFunction,
            proxy=False
        )
        
        basket = self.basketApi.root.add_resource('basket')
        basket.add_method('GET') # GET /basket
        basket.add_method('POST') # POST / basket

        singleBasket = basket.add_resource('{userName}') # basket/{userName}
        singleBasket.add_method('GET') # GET /basket/{userName}
        singleBasket.add_method('DELETE') # DELETE /basket/{userName}

        basketCheckout = basket.add_resource('checkout')
        basketCheckout.add_method('POST'); # POST /basket/checkout
            # expected request payload: { username: swn }

    def createOrderApi(self, orderFunction : PythonFunction):
        # Order microservices api gateway
        # root name = order

        # GET /order
        # GET /order/{userName}

        self.orderApi = api.LambdaRestApi(self, 'orderApi',
            rest_api_name='Order Service',
            handler=orderFunction,
            proxy=False
        )
        
        order = self.orderApi.root.add_resource('order')
        order.add_method('GET') # GET /order

        singleOrder = order.add_resource('{userName}') # order/{userName}
        singleOrder.add_method('GET') # GET /order/{userName}
