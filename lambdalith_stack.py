"""Infrastructure for the Lambdalith FastAPI Lambda."""

from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class LambdalithStack(Stack):
    """CDK stack that exposes FastAPI through API Gateway."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_fn = lambda_.Function(
            self,
            "FastApiLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=lambda_.Code.from_asset(
                ".",
                exclude=[
                    ".venv",
                    "cdk.out",
                    "__pycache__",
                    "tests",
                ],
            ),
        )

        apigateway.LambdaRestApi(
            self,
            "FastApiEndpoint",
            handler=lambda_fn,
        )
