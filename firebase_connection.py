import pyrebase

# Connect your own firebase database here!
config = {
  "apiKey": "",
  "authDomain": "",
  "databaseURL": "",
  "projectId": "",
  "storageBucket": "",
  "messagingSenderId": "",
  "appId": "",
  "measurementId": ""
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()

def update_module(telehandle: str, module_code: str):
    module_code = module_code.upper()
    
    # Updating modules that user is taking
    module_list = database.child('users').child(telehandle).get().val()

    # Creates an empty list if module does not exist in database
    if module_list is None:
        module_list = []

    module_list = list(set(module_list))  # Technically this line is unnecessary

    if module_code in module_list:
        return "You have already registered this module. Please enter another module, or enter 'done' if you do not wish to add in anymore modules."

    module_list.append(module_code)
    database.child('users').child(telehandle).set(module_list)
    
    # Updating Modules
    user_list = database.child('modules').child(module_code).get().val()

    if user_list is None:
        user_list = []
    user_list = list(set(user_list))  # Technically this line is unnecessary
    user_list.append(telehandle)
    database.child('modules').child(module_code).set(user_list)


def find_friends(telehandle: str):
    user_modules_list = database.child('users').child(telehandle).get().val()

    # Taking all modules from database to reduce frequency of database access
    all_modules_list = database.child('modules').get().val()

    if all_modules_list == None:
        return ""
    
    all_modules_dict = dict(all_modules_list)

    results  = []
    for mod in user_modules_list:
        results.append( (mod, all_modules_dict.get(mod)))
    return results

def get_modules(telehandle: str):
    '''
    Returns a list of all modules currently registered by user in database.
    '''
    user_modules_list = database.child('users').child(telehandle).get().val()
    return user_modules_list

def delete_module(telehandle: str, module_code: str):
    module_code = module_code.upper()
    
    # Making changes to user modules
    user_modules_list = database.child('users').child(telehandle).get().val()

    if user_modules_list == None:
        return

    if module_code in user_modules_list:
      user_modules_list.remove(module_code)
      database.child('users').child(telehandle).set(user_modules_list)

    # Making changes to modules containing users
    modules_tab_list = database.child('modules').child(module_code).get().val()

    if modules_tab_list == None:
        return

    if telehandle not in modules_tab_list:
      modules_tab_list.remove(telehandle)
      database.child('modules').child(module_code).set(modules_tab_list)