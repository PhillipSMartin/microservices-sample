import aws_cdk as core
import aws_cdk.assertions as assertions

from src.stack import MicroservicesSampleStack

# example tests. To run these tests, uncomment this file along with the example
# resource in microservices_sample/microservices_sample_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MicroservicesSampleStack(app, "microservices-sample")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
