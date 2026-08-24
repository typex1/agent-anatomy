"""aws_lookup — a Lambda-hosted MCP tool, behind AgentCore Gateway.

This is the third answer to "where does an MCP tool live?":

    clock_server.py   -> a subprocess on your machine (stdio)
    AWS Knowledge     -> someone else's managed service (HTTP)
    THIS FILE         -> nowhere, until invoked (Lambda behind Gateway)

Note what is MISSING here: any trace of MCP. No JSON-RPC, no schemas,
no server loop. The Lambda receives a plain event with the tool's
arguments; AgentCore Gateway does all protocol translation. The tool's
schema lives in gateway/aws_lookup_schema.json — the contract and the
code are deliberately separate artifacts.

The tool itself: look up which account you're in and where a given
AWS region physically is — the kind of tiny, stateless helper that is
obviously not worth a server.
"""

import json

import boto3

# Partial map: enough for the demo, honest about being partial.
REGION_LOCATIONS = {
    "us-east-1": "N. Virginia, USA",
    "us-east-2": "Ohio, USA",
    "us-west-2": "Oregon, USA",
    "eu-central-1": "Frankfurt, Germany",
    "eu-west-1": "Ireland",
    "eu-north-1": "Stockholm, Sweden",
    "ap-southeast-1": "Singapore",
    "ap-northeast-1": "Tokyo, Japan",
}


def handler(event, context):
    # Gateway passes tool arguments as the event; the tool name arrives
    # in the client context so one Lambda can serve many tools.
    tool_name = context.client_context.custom["bedrockAgentCoreToolName"]
    # Gateway prefixes the tool name with "<targetName>___"
    tool_name = tool_name.split("___")[-1]

    if tool_name == "aws_account_info":
        ident = boto3.client("sts").get_caller_identity()
        return {
            "account_id": ident["Account"],
            "region_of_this_lambda": context.invoked_function_arn.split(":")[3],
        }

    if tool_name == "region_location":
        region = event.get("region", "")
        return {
            "region": region,
            "location": REGION_LOCATIONS.get(region, f"unknown to this demo (knows {len(REGION_LOCATIONS)} regions)"),
        }

    return {"error": f"unknown tool {tool_name!r}"}
