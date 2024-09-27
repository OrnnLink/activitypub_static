from modules.utility import write_to_json, read_from_json

class FileDataHandler:
    def __init__(self, username, part_name, static_dir_path):
        self.username = username
        self.part_name = part_name
        self.static_dir_path = static_dir_path
    
    def add_update(self, data, update_part_name=True): 
        already_exists = self.__add_update_first_json(data, not update_part_name)
        if not already_exists and update_part_name:
            self.__add_update_part_name_count()
            return True
        return False
    
    def remove_update(self, data, update_part_name=True):
        already_exists = self.__remove_update_first_json(data)
        if already_exists and update_part_name:
            self.__remove_update_part_name_count()
            return True
        return False

    def __add_update_first_json(self, data, update=False):
        filename = f"{self.static_dir_path}/{self.username}/user-info/{self.part_name}/first.json"
        followers_json = read_from_json(filename)
        already_exists = True
        if not data in followers_json['orderedItems']:
            if not update:
                followers_json['orderedItems'].append(data)
            else:
                for i, item in enumerate(followers_json['orderedItems']):
                    if item['id'] == data['id']:
                        followers_json['orderedItems'][i] = data
                        break
            already_exists = False
            write_to_json(followers_json, filename)
        return already_exists
        
    def __add_update_part_name_count(self):
        filename = f"{self.static_dir_path}/{self.username}/user-info/{self.part_name}.json"
        followers_json = read_from_json(filename)
        followers_json['totalItems'] += 1
        write_to_json(followers_json, filename)

    def __remove_update_first_json(self, data):
        filename = f"{self.static_dir_path}/{self.username}/user-info/{self.part_name}/first.json"
        followers_json = read_from_json(filename)
        already_exists = False
        if data in followers_json['orderedItems']:
            followers_json['orderedItems'].remove(data)
            already_exists = True
            write_to_json(followers_json, filename)
        return already_exists
        
    def __remove_update_part_name_count(self):
        filename = f"{self.static_dir_path}/{self.username}/user-info/{self.part_name}.json"
        followers_json = read_from_json(filename)
        followers_json['totalItems'] = 1
        write_to_json(followers_json, filename)
    

         

    

         
