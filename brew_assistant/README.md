# Fellow Aiden Assistant
This is an interface to chat with your Aiden brewer using the OpenAI Assistants interface. 

![Fellow Brew Studio](https://github.com/9b/fellow-aiden/blob/master/brew_assistant/fellow-brew-assistant.png?raw=true)

## Requirements
```sh
pip install fellow-aiden
# AND
pip install streamlit
```

## Setup
Run the prep script to create the OpenAI Assistant within your account.
```sh
python prep.py
```

Add support for streamlit secrets
```sh
mkdir .streamlit
touch secrets.toml
```

Add details to `secrets.toml`
```sh
fellow_email = 'YOUR-EMAIL'
fellow_password = 'YOUR-PASSWORD'
openai_api_key = 'YOUR-API-KEY'
openai_assistant_id = 'YOUR-ASSISTANT-ID'
```

Save the Assistant ID and run the app.
```sh
streamlit run assistant.py
``` 

Once running local, you can optionally deploy to the cloud in public or private mode.

## Features
* Chat with Aiden machine using natural language
* Scrape coffee roaster websites or other URLs to add context to a session
* Generate recipes from coffee descriptions or URLs
* Manage profiles including listing and saving
* Query device configuration settings
