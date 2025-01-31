import os
import logging
import queue
import json
import time
from urllib import response
import requests

import streamlit as st
from openai import OpenAI
from streamlit import session_state as ss

st.set_page_config(page_title="Fellow Aiden", layout="centered")

from fellow_aiden import FellowAiden
from fellow_aiden.profile import CoffeeProfile


SYSTEM = """
Assume the role of a master coffee brewer. You focus exclusively on the pour over method and specialty coffee only. You often work with single origin coffees, but you also experiment with blends. Your recipes are executed by a robot, not a human, so maximum precision can be achieved. Temperatures are all maintained and stable in all steps. Always lead with the recipe, and only include explanations below that text, NOT inline. Below are the components of a recipe. 

Core brew settings: These settings are static and must match for single and batch brew.
Title: An interesting and creative name based on the coffee details. 
Ratio: How much coffee per water. Values MUST be between 14 and 20 with 0.5 step increments.
Bloom ratio: Water to use in bloom stage. Values MUST be between 1 and 3 with 0.5 step increments.
Bloom time: How long the bloom phase should last. Values MUST be between 1 and 120 seconds.
Bloom temperature: Temperature of the water. Values MUST be between 50 and 99 celsius.

Pulse settings: These are independent and can vary for single and batch brews. 
Number of pulses: Steps in which water is poured over coffee. Values MUST be between 1 and 10.
Time between pulses: Time in between each pulse. Values MUST be between 5 and 60 seconds. This MUST be included even if a single pulse is performed. 
Pulse temperate. Independent temperature to use for a given pulse.  Values MUST be between 50 and 99 celsius.

Below is an example of a previous recipe you put together for a speciality coffee called "Fruit cake" where you tasted cinnamon sugar, baked apples, and blackberry compote.

Roast: Light - Medium
Process | Cinnamon co-ferment | Strawberry co-ferment | Washed
33% Esteban Zamora - Cinnamon Anaerobic (San Marcos, Tarrazu, Costa Rica)
33% Sebastián Ramirez - Red Fruits (Quindio, Colombia)
33% Gamatui - Washed (Kapchorwa, Mt. Elgon, Uganda)

CORE
Ratio: 16
Bloom ratio: 3
Bloom time: 60s
Bloom temp: 87.5°C

SINGLE SERVE
Pulse 1 temp: 95°C
Pulse 2 temp: 92.5°C
Time between pulses: 25s
Number of pulses: 2 

BATCH
Pulse 1 temp: 95°C
Pulse 2 temp: 92.5°C
Time between pulses: 25s
Number of pulses: 2 

Here's another example. This coffee is a bold and intense cup composed of a smooth blend of Burundian and Latin American coffees with notes of mulled wine, baker's chocolate, blood orange, and a delicious blast of fudge.

Roast: Light - Medium
Process: Natural and Washed
Region: Burundi, Honduras and Peru
CORE
Ratio: 16
Bloom ratio: 2.5  
Bloom time: 30s
Bloom temp: 93.5°C 

SINGLE SERVE
Pulse 1 temp: 92°C
Pulse 2 temp: 92°C
Pulse 3 temp: 90.5°C 
Time between pulses: 20s
Number of pulses: 3 

BATCH
Pulse temp: 92°C 
Number of pulses: 1
"""    

REFORMAT_SYSTEM = """
Assume the role of a data engineer. You need to parse coffee recipes and their explanations so the data can be structured. Below are the important components of the recipe.

Core brew settings: These settings are static and must match for single and batch brew.
Title: An interesting and creative name based on the coffee details. 
Ratio: How much coffee per water. Values range from 1:14 to 1:20 with 0.5 steps.
Bloom ratio: Water to use in bloom stage. Values range from 1 to 3 with 0.5 steps.
Bloom time: How long the bloom phase should last. Values range from 1 to 120 seconds.
Bloom temperature: Temperature of the water. Values range from 50 celsius to 99 celsius.

Pulse settings: These are independent and can vary for single and batch brews. 
Number of pulses: Steps in which water is poured over coffee. Values range from 1 to 10.
Time between pulses: Time in between each pulse. Values range from 5 to 60 seconds. This must be included even if a single pulse is performed. 
Pulse temperate. Independent temperature to use for a given pulse.  Values range from 50 celsius to 99 celsius. 
"""

CONFIG_ALIGNMENT = """
Assume the role of a data engineer. You are provided limited context of a setting to adjust. Use the information below to match the most likely setting and infer if the value type format is correct. If it's not, adjust it.

For example, assume you have the following settings and values:
    'languageCode': 'en-us',
    'serialNumber': '157024280390',
    'deviceTimezone': 'EST5EDT',
    'displayClock24hrMode': True,
    'displayClock': True,
    'doBrewCancel': None,
    'doBrew': None,

If the context is "time-format" and value is 12, then the best setting would be displayClock24hrMode and value set to False.

Here are all the possible settings:
{0}

Output as a json object.
"""

AIDEN_STARTER = """
Hey, I am Aiden! You can ask me about different coffees using URLs or descriptions. 
I can acess your existing profiles, generate new ones and save them for brewing. How can I help?
"""

def scrape_website(url: str) -> str:
    """
    Fetches the given URL and returns the raw HTML body as a string.
    If there's an error, returns an error message.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError if status != 200
        return response.text
    except Exception as e:
        return f"Error fetching '{url}': {str(e)}"


@st.cache_resource(show_spinner=False)
def init_logging():
    logging.basicConfig(format="[%(asctime)s] %(levelname)+8s: %(message)s")
    local_logger = logging.getLogger()
    local_logger.setLevel(logging.INFO)
    return local_logger

logger = init_logging()

def infer_setting_from_context(device_config, context, value):
    """Uses context to infer what setting should be adjusted."""
    try:
        prompt = CONFIG_ALIGNMENT.format(device_config)
        completion = ss["openai"].beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Context: " + context + "\nValue: " + value},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "setting_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "setting": {
                                "type": "string"
                            },
                            "value": {
                                "type": "string"
                            }
                        },
                        "required": ["setting", "value"],
                        "additionalProperties": False
                    }
                }
            }
        )
        alignment = completion.choices[0].message.content
        alignment = json.loads(alignment)
    except Exception as e:
        print("Failed to infer setting from context:", e)
        return False
    return alignment

def extract_recipe_from_description(model_explanation):
    """Extracts the recipe from the description."""
    try:
        completion = ss["openai"].beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": REFORMAT_SYSTEM},
                {"role": "user", "content": model_explanation},
            ],
            response_format=CoffeeProfile,
        )
        model_recipe = completion.choices[0].message.parsed
    except Exception as e:
        print("Failed to extract recipe from description:", e)
        return False
    return model_recipe

def generate_recipe(coffee_description):
    guidance = "Suggest a recipe for the following coffee. Provide your explanations below the recipe.\n"
    coffee_description = ' '.join([guidance, coffee_description])
    completion = ss["openai"].chat.completions.create(
        model="o1-preview",
        messages=[
            {"role": "user", "content": SYSTEM + coffee_description},
        ]
    )
    model_explanation = completion.choices[0].message.content
    return model_explanation

if 'tool_requests' not in ss:
    ss['tool_requests'] = queue.Queue()
tool_requests = ss['tool_requests']

def handle_requires_action(tool_request):
    """
    Called when the assistant run hits 'requires_action' with one or more function calls.
    We see which function the model wants, call the real library or mock.
    Then we submit the outputs back to the run.
    """
    tool_outputs = []
    data = tool_request.data

    for tool in data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.arguments:
            function_arguments = json.loads(tool.function.arguments)
        else:
            function_arguments = {}

        st.toast(f"Executing tool: {tool.function.name}", icon=":material/function:")

        match tool.function.name:

            case "get_device_name":
                logger.info("Calling get_device_name function")
                aiden = ss.get("fellow_aiden")
                brewer_name = aiden.get_display_name()
                if not brewer_name:
                    brewer_name = "Unknown Brewer Name"
                tool_outputs.append({"tool_call_id": tool.id, "output": brewer_name})

            case "list_profiles":
                logger.info("Calling list_profiles function")
                aiden = ss.get("fellow_aiden")
                profiles = aiden.get_profiles()
                if not profiles:
                    profiles = "Couldn't get profiles"
                tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(profiles)})

            case "create_profile_from_link":
                logger.info("Calling create_profile_from_link function")
                aiden = st.session_state.get("fellow_aiden")
                link = function_arguments.get("link")
                try:
                    new_profile = aiden.create_profile_from_link(link)
                    tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(new_profile)})
                except Exception as e:
                    logger.exception("Failed to create profile from link")
                    error_msg = {
                        "status": "error",
                        "message": f"Error creating profile from link: {str(e)}"
                    }
                    tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(error_msg)})

            case "delete_profile_by_id":
                logger.info("Calling delete_profile function")
                aiden = st.session_state.get("fellow_aiden")
                link = function_arguments.get("id")
                try:
                    new_profile = aiden.delete_profile_by_id(link)
                    tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(new_profile)})
                except Exception as e:
                    logger.exception("Failed to delete profile by ID")
                    error_msg = {
                        "status": "error",
                        "message": f"Error deleting profile from link: {str(e)}"
                    }
                    tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(error_msg)})

            case "scrape_website":
                url = function_arguments.get("url")
                result = scrape_website(url)
                tool_outputs.append({"tool_call_id": tool.id, "output": result})

            case "provide_recipe":
                coffee_description = function_arguments.get("coffee_description")
                result = generate_recipe(coffee_description)
                tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(result)})

            case "adjust_setting":
                aiden = st.session_state.get("fellow_aiden")
                device_settings = aiden.get_device_config()
                context_setting = function_arguments.get("setting")
                context_value = function_arguments.get("value")
                alignment = infer_setting_from_context(device_settings, context_setting, context_value)
                if alignment:
                    try:
                        adjustment = aiden.adjust_setting(alignment['setting'], alignment['value'])
                        tool_outputs.append({
                            "tool_call_id": tool.id,
                            "output": "Successfully adjusted setting"
                        })
                    except Exception as e:
                        logger.exception("Failed to adjust setting")
                        error_msg = {
                            "status": "error",
                            "message": f"Error adjusting device setting: {str(e)}"
                        }
                        tool_outputs.append({"tool_call_id": tool.id, "output": error_msg})
                else:
                    logger.error("Failed to infer setting from context")
                    error_msg = {
                        "status": "error",
                        "message": "Failed to infer setting from context"
                    }
                    tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(error_msg)})

            case "save_recipe":
                recipe_description = function_arguments.get("recipe_description")
                while True:
                    model_recipe = extract_recipe_from_description(recipe_description)
                    if model_recipe:
                        break
                recipe = model_recipe.model_dump()
                recipe['profileType'] = 0
                aiden = st.session_state.get("fellow_aiden")
                created_profile = aiden.create_profile(recipe)
                tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(created_profile)})

            case "get_device_config":
                logger.info("Calling get_device_config function")
                aiden = st.session_state.get("fellow_aiden")
                remote_arg = function_arguments.get("remote", True)
                try:
                    device_config = aiden.get_device_config(remote=True)
                    # Return as JSON so the Assistant can parse it
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": json.dumps(device_config)
                    })
                except Exception as e:
                    logger.exception("Failed to get device config")
                    error_msg = {
                        "status": "error",
                        "message": f"Error getting device config: {str(e)}"
                    }
                    tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(error_msg)})

            case _:
                logger.error(f"Unrecognized function name: {tool.function.name}. Tool: {tool}")
                ret_val = {
                    "status": "error",
                    "message": (
                        "Function name is not recognized. Make sure you submit the request "
                        "with the correct structure. Fix your request and try again."
                    )
                }
                tool_outputs.append({"tool_call_id": tool.id, "output": json.dumps(ret_val)})

    st.toast("Function completed", icon=":material/function:")
    return tool_outputs, data.thread_id, data.id


def data_streamer():
    """
    Stream data from the assistant. Text messages are yielded. Images and tool requests are put in the queue.
    """
    logger.info("Starting data streamer on ss.stream")
    st.toast("Thinking...", icon=":material/emoji_objects:")
    content_produced = False

    for response in ss.stream:
        match response.event:
            case "thread.message.delta":
                content = response.data.delta.content[0]
                match content.type:
                    case "text":
                        value = content.text.value
                        content_produced = True
                        yield value
                    case "image_file":
                        logger.info(f"Image file: {content}")
                        image_content = io.BytesIO(client.files.content(content.image_file.file_id).read())
                        content_produced = True
                        yield Image.open(image_content)

            case "thread.run.requires_action":
                logger.info(f"Run requires action: {response}")
                tool_requests.put(response)
                if not content_produced:
                    yield "Executing %s..." % response.data.required_action.submit_tool_outputs.tool_calls[0].function.name
                return  # End streaming - we'll handle the function call

            case "thread.run.failed":
                logger.error(f"Run failed: {response}")
                return  # End

    st.toast("Completed", icon=":material/emoji_objects:")
    logger.info("Finished data streamer")


def add_message_to_state_session(message):
    if len(message) > 0:
        ss.messages.append({"role": "assistant", "content": message})

def display_stream(content_stream, create_context=True):
    """
    Streams partial content from the run and displays it in the UI.
    If there's a function call, we handle it after streaming stops.
    """
    ss.stream = content_stream
    if create_context:
        with st.chat_message("assistant"):
            response = st.write_stream(data_streamer)
    else:
        response = st.write_stream(data_streamer)

    if response is not None:
        if isinstance(response, list):
            for message in response:
                add_message_to_state_session(message)
        else:
            add_message_to_state_session(response)


def main():
    if "fellow_aiden" not in ss:
        ss["fellow_aiden"] = None

    email = st.sidebar.text_input("Email for Aiden")
    password = st.sidebar.text_input("Password for Aiden", type="password")
    assistant_id = st.sidebar.text_input("OpenAI Assistant ID", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    derived = False

    if 'fellow_email' in st.secrets:
        email = st.secrets['fellow_email']
    if 'fellow_password' in st.secrets:
        derived = True
        password = st.secrets['fellow_password']
    if 'openai_assistant_id' in st.secrets:
        assistant_id = st.secrets['openai_assistant_id']
    if 'openai_api_key' in st.secrets:
        openai_api_key = st.secrets['openai_api_key']


    if derived and not ss['fellow_aiden']:
        try:
            ss["fellow_aiden"] = FellowAiden(email, password)
            st.success("FellowAiden initialized!")
        except Exception as e:
            st.error(f"Failed to init FellowAiden: {e}")

    if st.sidebar.button("Log in") and not ss['fellow_aiden']:
        try:
            ss["fellow_aiden"] = FellowAiden(email, password)
            st.success("FellowAiden initialized!")
        except Exception as e:
            st.error(f"Failed to init FellowAiden: {e}")

    st.title("My Aiden")
    if "messages" not in ss:
        ss.messages = [{"role": "assistant", "content": AIDEN_STARTER}]

    # Display conversation from session so far
    for message in ss.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if "openai" not in ss and openai_api_key:
        logger.info("Creating OpenAI client")
        ss["openai"] = OpenAI(api_key=openai_api_key)

    # Retrieve or create the assistant object
    if "assistant" not in ss and assistant_id:
        # Attempt to retrieve an existing assistant by ID
        # Replace with your actual assistant ID, or create a new one as needed
        assistant = ss["openai"].beta.assistants.retrieve(assistant_id=assistant_id)
        if assistant is None:
            raise RuntimeError(f"Assistant not found with ID={assistant_id}")
        logger.info(f"Loaded assistant: {assistant.name}")
        ss["assistant"] = assistant

    ready = bool(email and password and assistant_id and openai_api_key)

    if prompt := st.chat_input("Ask to generate a recipe from a roaster URL..."):

        if not ready:
            st.warning(f"Ensure all settings are filled in on the side bar.")
            return

        # Display user message in the UI
        with st.chat_message("user"):
            st.write(prompt)

        if "thread" in ss:
            thread = ss["thread"]
        else:
            thread = ss["openai"].beta.threads.create()
            logger.info(f"Created new thread: {thread.id}")
            ss["thread"] = thread

        ss["openai"].beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        with ss["openai"].beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=ss["assistant"].id
        ) as stream:
            display_stream(stream)

            while not tool_requests.empty():
                logger.info("Handling tool requests")
                with st.chat_message("assistant"):
                    # handle the function calls
                    tool_outputs, thread_id, run_id = handle_requires_action(tool_requests.get())

                    # Now we submit them back (also streaming)
                    with ss["openai"].beta.threads.runs.submit_tool_outputs_stream(
                        thread_id=thread_id,
                        run_id=run_id,
                        tool_outputs=tool_outputs
                    ) as tool_stream:
                        # Display any additional partial response
                        display_stream(tool_stream, create_context=False)
        


if __name__ == "__main__":
    main()
