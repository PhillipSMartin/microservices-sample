from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets
)
from constructs import Construct

class MssEventBus(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        event_bus = events.EventBus(
            self, "MssEventBus", 
            event_bus_name="MssEventBus"
        )

        checkout_basket_rule = events.Rule(
            self,
            "CheckoutBasketRule",
            event_bus=event_bus,
            description="Basket microservice has checked out a basket",
            rule_name="CheckoutBasketRule",
            event_pattern= events.EventPattern(
                source=['com.swn.basket.checkoutbasket'],
                detail_type=['CheckoutBasket']
            )
        )

        event_bus.grant_put_events_to(kwargs["publisherFunction"])
        checkout_basket_rule.add_target(targets.LambdaFunction( kwargs["targetFunction"] ))

