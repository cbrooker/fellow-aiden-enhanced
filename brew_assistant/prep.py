"""Create assistant within OpenAI."""
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

assistant = client.beta.assistants.create(
    name="DEBUG Aiden Coffee Assistant",
    instructions=(
        "You are a coffee machine assistant. Users may request list/create/delete "
        "coffee profiles, share links, etc. Use the function tools to handle. "
        "Return final answers in plain text."
    ),
    model="gpt-4o",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "list_profiles",
                "description": "List all existing coffee profiles",
                "strict": False,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_profile_from_link",
                "description": "Create a new coffee profile from a shared brew link",
                "strict": False,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "link": {
                            "type": "string",
                            "description": "The shared brew link"
                        }
                    },
                    "required": ["link"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_share_link",
                "description": "Generate a share link for a coffee profile",
                "strict": False,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "profile_id": {
                            "type": "string",
                            "description": "The ID of the profile to share"
                        }
                    },
                    "required": ["profile_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_name",
                "description": "Get the coffee device display name",
                "strict": False,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_config",
                "description": "Return the current device config.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": ["remote"],
                    "properties": {
                        "remote": {
                            "type": "boolean",
                            "description": (
                                "If True, force a new request to Fellow's API to "
                                "refresh the device config. Otherwise, returns the "
                                "cached config."
                            )
                        }
                    },
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scrape_website",
                "description": "Fetches a webpage and returns its raw HTML body.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": (
                                "The website URL to fetch, e.g. 'https://example.com'"
                            )
                        }
                    },
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "provide_recipe",
                "description": (
                    "Suggest a recipe for the given coffee description and "
                    "provide explanations below the recipe."
                ),
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": ["coffee_description"],
                    "properties": {
                        "coffee_description": {
                            "type": "string",
                            "description": (
                                "Description of the coffee for which the recipe "
                                "is to be generated"
                            )
                        }
                    },
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "save_recipe",
                "description": "Save a recipe to the machine based on a recipe explanation.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": ["recipe_description"],
                    "properties": {
                        "recipe_description": {
                            "type": "string",
                            "description": (
                                "Description of the coffee for which the recipe "
                                "is to be extracted"
                            )
                        }
                    },
                    "additionalProperties": False
                }
            }
        }
    ]
)
data = assistant.to_dict()
print("Assistant ID: %s" % data['id'])