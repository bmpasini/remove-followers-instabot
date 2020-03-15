Remove Followers InstaBot
========

This Instagram bot automates the process of removing followers that you no longer want. The input is a list of usernames of the followers you would like to keep. This bot will slowly remove unwanted followers, respecting Instagram's restrictive policy for automated behaviors. It aims to behave as a normal user would.

Removing followers is not officially supported by Instagram's API. This bot uses Instagram's unofficial Web API.

## Setup
Clone this repository:
```
git clone https://github.com/bmpasini/remove-followers-instabot.git
```
Run the following command to install the dependencies:
```
cd remove-followers-instabot && sudo pip install -r config/dependencies.txt
```

Modify the `config/config.yml` file to customize your bot:
```
CREDENTIALS:
  USERNAME: 'USERNAME'
  PASSWORD: 'PASSWORD'
REMOVE_FOLLOWERS_COUNT: 1000
KEEP_FOLLOWERS: [ 'bobmarley', 'snoopdogg', 'infectedmushroom' ]
```

- `CREDENTIALS`: Your login info.
- `TOTAL_LIKES`: The number of followers you wish to be removed in one run of the bot. My suggestion is to not choose a value greater than 1000, as Instagram may suspect your activities and delete your account. Run this bot every day with this config until you clear your account from unwanted followers.
- `KEEP_FOLLOWERS`: The username of followers that you would like to keep.

Then run:
```
python3 src/instabot.py
```

You may also pass in the path of a log file, for a personalized log:
```
python3 src/instabot.py <log_file_path>
```
