import os

path = "/etc/nginx/sites-enabled"
for name in os.listdir(path):
    if name != "lisenok":
        os.remove(os.path.join(path, name))
print(os.listdir(path))
