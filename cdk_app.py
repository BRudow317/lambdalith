"""CDK app entrypoint."""

import aws_cdk as cdk

from lambdalith_stack import LambdalithStack


app = cdk.App()
LambdalithStack(app, "LambdalithStack")
app.synth()
