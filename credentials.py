from constants import *
from integrity import *
import configparser


# Initialize config parser
config = configparser.ConfigParser()

# Read credentials from config file
def read():
    loaded = config.read('credentials.ini')

    if not loaded:
        print(WARNING, "Credentials file not found! Creating a new one...")
        
        generate_credential_file(config)
        
        
# Control default credentials
def control_defaults():
    defaultDexcomUsername = False
    defaultDexcomPassword = False
    defaultDiscordClientID = False

    credentialLogQueue = []

    if config['Dexcom']['username'] == 'your_username': 
        defaultDexcomUsername = True
        
        # The reason why this is so messy is due to the fact that i use a log file, and want to format it neatly
        credentialLogQueue.append("Please update 'your_username' in the credentials.ini file with your actual Dexcom username." + ERROR_NEW_LINE)
        credentialLogQueue[-1] += "The username used to access the Dexcom API is the same as your account username." + ERROR_NEW_LINE
        credentialLogQueue[-1] += "This can be found on your Dexcom account page.\n" + ERROR_NEW_LINE
        credentialLogQueue[-1] += ("Link: %s (US)" % DEXCOM_US_ACCOUNT_LINK) + ERROR_NEW_LINE
        credentialLogQueue[-1] += ("Link: %s (EU)\n" % DEXCOM_EU_ACCOUNT_LINK)

    if config['Dexcom']['password'] == 'your_password': 
        defaultDexcomPassword = True

        # The reason why this is so messy is due to the fact that i use a log file, and want to format it neatly
        credentialLogQueue.append("Please update 'your_password' in the credentials.ini file with your actual Dexcom password." + ERROR_NEW_LINE)
        credentialLogQueue[-1] += "The password used to access the Dexcom API is the same as your account password." + ERROR_NEW_LINE
        credentialLogQueue[-1] += "This can be found on your Dexcom account page.\n" + ERROR_NEW_LINE
        credentialLogQueue[-1] += ("Link: %s (US)" % DEXCOM_US_ACCOUNT_LINK) + ERROR_NEW_LINE
        credentialLogQueue[-1] += ("Link: %s (EU)\n" % DEXCOM_EU_ACCOUNT_LINK)

    if config["Discord"]["client_id"] == 'your_discord_client_id': 
        defaultDiscordClientID = True

        # The reason why this is so messy is due to the fact that i use a log file, and want to format it neatly
        credentialLogQueue.append("Please update 'your_discord_client_id' in the credentials.ini file with your actual Discord token client ID." + ERROR_NEW_LINE)
        credentialLogQueue[-1] += "The client ID used to access the Discord API requires an OAuth2 application in your developer portal." + ERROR_NEW_LINE
        credentialLogQueue[-1] += "This can be found on your Discord developer portal.\n" + ERROR_NEW_LINE
        credentialLogQueue[-1] += "A good place to start would be Discord's OAuth2 documentation." + ERROR_NEW_LINE
        credentialLogQueue[-1] += ("Link: %s\n" % DISCORD_OAUTH2_DOCUMENTATION_LINK) + ERROR_NEW_LINE
        credentialLogQueue[-1] += "Alternatively, you can look it up on google." + ERROR_NEW_LINE
        credentialLogQueue[-1] += ("Link: %s\n" % DISCORD_CLIENT_ID_SEARCH_LINK)

    if defaultDexcomUsername or defaultDexcomPassword or defaultDiscordClientID:
        from log import logger

        for message in credentialLogQueue:
            logger.error(message)

        exit(1)


# Get credentials
def get(section:str, key: str) -> str:
    return config.get(section, key)
