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

# Full region list, copied from the official AWS documentation:
# https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html
# (34 commercial regions; GovCloud and China partitions excluded.)
# Why hardcode ALL of them? A demo agent answered "eu-central-2 -> Vienna"
# from parametric knowledge when this map was partial. Zurich, actually.
# A tool that answers authoritatively must BE authoritative.
REGION_LOCATIONS = {
    "us-east-1": "US East (N. Virginia), United States of America",
    "us-east-2": "US East (Ohio), United States of America",
    "us-west-1": "US West (N. California), United States of America",
    "us-west-2": "US West (Oregon), United States of America",
    "af-south-1": "Africa (Cape Town), South Africa",
    "ap-east-1": "Asia Pacific (Hong Kong), Hong Kong",
    "ap-south-2": "Asia Pacific (Hyderabad), India",
    "ap-southeast-3": "Asia Pacific (Jakarta), Indonesia",
    "ap-southeast-5": "Asia Pacific (Malaysia), Malaysia",
    "ap-southeast-4": "Asia Pacific (Melbourne), Australia",
    "ap-south-1": "Asia Pacific (Mumbai), India",
    "ap-southeast-6": "Asia Pacific (New Zealand), New Zealand",
    "ap-northeast-3": "Asia Pacific (Osaka), Japan",
    "ap-northeast-2": "Asia Pacific (Seoul), South Korea",
    "ap-southeast-1": "Asia Pacific (Singapore), Singapore",
    "ap-southeast-2": "Asia Pacific (Sydney), Australia",
    "ap-east-2": "Asia Pacific (Taipei), Taiwan",
    "ap-southeast-7": "Asia Pacific (Thailand), Thailand",
    "ap-northeast-1": "Asia Pacific (Tokyo), Japan",
    "ca-central-1": "Canada (Central), Canada",
    "ca-west-1": "Canada West (Calgary), Canada",
    "eu-central-1": "Europe (Frankfurt), Germany",
    "eu-west-1": "Europe (Ireland), Ireland",
    "eu-west-2": "Europe (London), United Kingdom",
    "eu-south-1": "Europe (Milan), Italy",
    "eu-west-3": "Europe (Paris), France",
    "eu-south-2": "Europe (Spain), Spain",
    "eu-north-1": "Europe (Stockholm), Sweden",
    "eu-central-2": "Europe (Zurich), Switzerland",
    "il-central-1": "Israel (Tel Aviv), Israel",
    "mx-central-1": "Mexico (Central), Mexico",
    "me-south-1": "Middle East (Bahrain), Bahrain",
    "me-central-1": "Middle East (UAE), United Arab Emirates",
    "sa-east-1": "South America (São Paulo), Brazil",
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
