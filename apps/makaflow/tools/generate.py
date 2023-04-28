
import random
import uuid
from base64 import b64encode
from secrets import token_bytes


import ruamel.yaml
yaml = ruamel.yaml.YAML()

def new_users():
  s_num = 1010
  user_num = 40

  users = []

  for n in range(s_num, s_num+user_num):
    _u = {
      "name": f"user{n}",
      "nickname": f"user{n}",
      "password": b64encode(token_bytes(16)).decode(),
      "uuid_str":str(uuid.uuid4()),
      "auth": str(random.random())[-6:]
    }
    users.append(_u)
  res={"users":users}

  yaml.dump(res, open('runtime/users.yaml', 'w+'))


def update_users():

  server_profile = yaml.load(open("runtime/users.yaml", 'r'))
  users = server_profile['users']

  for user in users:
    user['email'] = f"{user['name']}@gmail.com"
    user['level'] = 0
    
  res={"users":users}

  yaml.dump(res, open('runtime/users2.yaml', 'w+'))


if __name__ == "__main__":
  update_users()