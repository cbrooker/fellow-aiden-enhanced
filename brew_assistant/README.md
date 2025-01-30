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

Save the Assistant ID and run the app.
```sh
streamlit run assistant.py
``` 

## Features
* Chat with Aiden machine using natural language
* Scrape coffee roaster websites or other URLs to add context to a session
* Generate recipes from coffee descriptions or URLs
* Manage profiles including listing and saving
* Query device configuration settings
