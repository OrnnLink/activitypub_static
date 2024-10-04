import os
import json
import shutil
from modules.handler.config_data_handler import ConfigDataHandler
from modules.generate_key import generate_key, write_key_to_files

# def mock_config_handler():
#     handler = ConfigDataHandler.get_instance()
#     handler.username = data['username']
#     handler.domain= data['domain']
#     handler.site_dir_path = data["site_dir_path"]
#     handler.static_dir_path = f"{self.site_dir_path}/static"
#     handler.public_key_path = data["public_key_path"]
#     self.actor_id = f"https://{self.domain}/{self.username}/user-info/actor.json"
#     self.follower_url = f"https://{self.domain}/{self.username}/user-info/followers.json"
#     self.following_url = f"https://{self.domain}/{self.username}/user-info/following.json"
#     self.private_key_path = data["private_key_path"]

def make_test_folder():
    dirnames = [
        "tests/activitypub", "tests/activitypub/static",
        "tests/resources", "tests/activities", "tests/resources/users"
    ]
    for dirname in dirnames: 
        os.makedirs(dirname)

    filenames = {
        "tests/activitypub/hugo.toml": ["baseURL = 'https://staticap.netlify.app/'\n"]
    }
    for filename in filenames:
        lines = filenames[filename]
        with open(filename, "w") as fd:
            fd.writelines(lines)
    __make_config_file()
    __make_keys()
    handler = ConfigDataHandler.get_instance()
    handler.set_config("tests/config.json")

def tear_down_test_folders():
    dirnames = [ 
                "tests/activitypub", 
                "tests/resources", 
                "tests/activities"
                ]
    for dirname in dirnames:
        shutil.rmtree(dirname)
    os.remove("tests/config.json")
    
def __make_config_file():
    filename = "tests/config.json"
    data = {
        "username": "noah",
        "domain": "staticap.netlify.app",
        "private_key_path": "tests/resources/private_key.pem",
        "public_key_path": "tests/resources/public_key.pem",
        "site_dir_path": "tests/activitypub"
    }
    write_to_json(data, filename) 

def __make_keys():
    private_pem, public_pem = generate_key()
    write_key_to_files(private_pem, public_pem, "tests/resources/")

def __make_activities_files():
    ...


def read_from_json(filename):
    with open(filename, "r") as fd:
        try:
            return json.load(fd)
        except Exception as e:
            return None

def write_to_json(data: dict, filename: str):
    with open(filename, "w") as fd:
        try:
            fd.write(json.dumps(data, indent=4))
        except Exception:
            return False
    return True