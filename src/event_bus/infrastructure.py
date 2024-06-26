from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    aws_sqs as sqs
)
from constructs import Construct

class MssEventBus(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)
       
        publisher = kwargs["publisher"]
        target_queue = kwargs.get("targetQueue", None)
        target_function = kwargs.get("targetFunction", None)

        event_bus = events.EventBus(
            self, "MssEventBus", 
            event_bus_name="MssEventBus"
        )

        checkout_basket_pattern = events.EventPattern(
            source=['com.swn.basket.checkoutbasket'],
            detail_type=['CheckoutBasket'])
        checkout_basket_rule = events.Rule(
            self,
            "CheckoutBasketRule",
            event_bus=event_bus,
            description="Basket microservice has checked out a basket",
            rule_name="CheckoutBasketRule",
            event_pattern= checkout_basket_pattern
        )

        event_bus.grant_put_events_to(publisher)
        publisher.add_environment("EVENT_BUSNAME", event_bus.event_bus_name)
        publisher.add_environment("EVENT_SOURCE", checkout_basket_pattern.source[0] )
        publisher.add_environment("DETAIL_TYPE", checkout_basket_pattern.detail_type[0] )                          

        if target_function:
            checkout_basket_rule.add_target(targets.LambdaFunction( target_function ))
        elif target_queue:
            checkout_basket_rule.add_target(targets.SqsQueue( target_queue ))
        else:
            raise ValueError("Must specify either targetFunction or targetQueue for MssEventBus")
