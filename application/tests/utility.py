import os
import json
import shutil
from modules.handler.config_data_handler import ConfigDataHandler
from modules.generate_key import generate_key, write_key_to_files

def make_test_folder():
    dirnames = [
        "tests/activitypub", "tests/activitypub/static",
        "tests/resources", "tests/activities", "tests/resources/users",
        "tests/activitypub/content",
    ]
    for dirname in dirnames: 
        os.makedirs(dirname)

    filenames = {
        "tests/activitypub/hugo.toml": ["baseURL = 'https://staticap.netlify.app/'\n"]
    }

    with open("tests/netlify.toml", "w") as fd:
        fd.writelines([])

    for filename in filenames:
        lines = filenames[filename]
        with open(filename, "w") as fd:
            fd.writelines(lines)
    __make_config_file()
    __make_keys()
    __make_activities_files()
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
    os.remove("tests/netlify.toml")
    
def __make_config_file():
    filename = "tests/config.json"
    data = {
        "username": "noah",
        "domain": "staticap.netlify.app",
        "private_key_path": "tests/resources/private_key.pem",
        "public_key_path": "tests/resources/public_key.pem",
        "site_dir_path": "tests/activitypub",
        "root_dir_path": "tests"
    }
    write_to_json(data, filename) 

def __make_keys():
    private_pem, public_pem = generate_key()
    write_key_to_files(private_pem, public_pem, "tests/resources/")

def __make_activities_files():
    os.makedirs("tests/activitypub/static/noah")
    os.makedirs("tests/activitypub/static/noah/user-info")
    os.makedirs("tests/activitypub/static/noah/replies")
    filenames = [ 'followers', "following", "outbox", "inbox"]
    path= "tests/activitypub/static/noah/user-info"
    for name in filenames:
        filename = f"{path}/{name}.json"
        data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"https://staticap.netlify.app/noah/user-info/{name}.json",
            "type": "OrderedCollection",
            "totalItems": 0,
            "first": f"https://staticap.netlify.app/noah/user-info/{name}/first.json"
        }
        write_to_json(data,filename)
        os.makedirs(f"{path}/{name}")
        filename = f"{path}/{name}/first.json"
        data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"https://staticap.netlify.app/noah/user-info/{name}/first.json",
            "partOf": f"https://staticap.netlify.app/noah/user-info/{name}.json",
            "type": "OrderedCollectionPage",
            "orderedItems": []
        }
        write_to_json(data,filename)
        ...
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