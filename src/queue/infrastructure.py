from aws_cdk import (
    aws_sqs as sqs
)
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from constructs import Construct


class MssQueues(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.order_queue = sqs.Queue(self, "orderQueue",
            queue_name="OrderQueue"
        )

        kwargs["consumer"].add_event_source( SqsEventSource(
                self.order_queue,
                batch_size=3
            )
        )