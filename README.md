# Fellow Aiden

[![PyPI version](https://badge.fury.io/py/fellow-aiden.svg)](https://badge.fury.io/py/fellow-aiden)

This library provides an interface to the Fellow Aiden coffee brewer. An additional brew studio UI with support for AI-generated recipes is also included. You can run the Brew Studio locally on your system or make use of the hosted version: [https://fellow-brew-studio.streamlit.app/](https://fellow-brew-studio.streamlit.app/)

![Fellow Brew Studio](https://github.com/9b/fellow-aiden/blob/master/brew_studio/fellow-brew-studio.png?raw=true)

## Quick Start

**Install the library**:

```sh
pip install fellow-aiden
# or
python setup.py install
```

**Set ENV variables**:

```sh
export FELLOW_EMAIL='YOUR-EMAIL-HERE'
export FELLOW_PASSWORD='YOUR-PASSWORD-HERE'
```

## Sample Code

This sample code shows some of the range of functionality within the library:

```python
import os
from fellow_aiden import FellowAiden

# EMAIL = "YOUR-EMAIL-HERE"
# PASSWORD = "YOUR-PASSWORD-HERE"

EMAIL = os.environ['FELLOW_EMAIL']
PASSWORD = os.environ['FELLOW_PASSWORD']

# Create an instance
aiden = FellowAiden(EMAIL, PASSWORD)

# Get display name of brewer
name = aiden.get_display_name()

# Get profiles
profiles = aiden.get_profiles()

# Add a profile
profile = {
    "profileType": 0,
    "title": "Debug-FellowAiden",
    "ratio": 16,
    "bloomEnabled": True,
    "bloomRatio": 2,
    "bloomDuration": 30,
    "bloomTemperature": 96,
    "ssPulsesEnabled": True,
    "ssPulsesNumber": 3,
    "ssPulsesInterval": 23,
    "ssPulseTemperatures": [96,97,98],
    "batchPulsesEnabled": True,
    "batchPulsesNumber": 2,
    "batchPulsesInterval": 30,
    "batchPulseTemperatures": [96,97]
}
aiden.create_profile(profile)

# Find profile
pid = None
option = aiden.get_profile_by_title('FellowAiden', fuzzy=True)
if option:
    pid = option['id'] # p0

# Share a profile
share_link = aiden.generate_share_link(pid)

# Delete a profile
aiden.delete_profile_by_id(pid)

# Add profile from shared brew link
aiden.create_profile_from_link('https://brew.link/p/ws98')

# Add a schedule
schedule = {
    "days": [True, True, False, True, False, True, False], // sunday - saturday
    "secondFromStartOfTheDay": 28800, // time since 12 am
    "enabled": True,
    "amountOfWater": 950, // 150 - 1500
    "profileId": "p7", // must be valid profile
}
aiden.create_schedule(schedule)

# Delete a schedule
aiden.delete_schedule_by_id('s0')

```

## Features

* Access all settings and details from Aiden brewer
* Manage custom brewing profiles
* Add shared profiles from URL
* Generate share links from custom profiles
* Search profiles using title (match and fuzzy)
* Manage custom brewing schedules
* Brew Studio UI with support for AI, Brew Links and Profile adjustments
