from constants import PROCESS, WARNING
import configparser
import os


def verify_project(): 
    print(PROCESS, "Verifying project integrity...")

    # Check that all necessary directories exist
    if not os.path.exists("logs/"):
        print(WARNING, "Logs directory is missing!")
        print(PROCESS, "Creating logs directory...")

        os.makedirs("logs/")

    # TODO: Implement integrity check for `assets/`, and download missing assets



def generate_credential_file(config: configparser.ConfigParser):
    print(PROCESS, "Creating a new credentials file...")

    # Write default credentials to the config file
    config['Dexcom'] = {
        'username': 'your_username',
        'password': 'your_password'
    }
    
    config['Discord'] = {
        'client_id': 'your_discord_client_id'
    }

    # Save the config file
    with open('credentials.ini', 'w') as configfile:
        config.write(configfile)
