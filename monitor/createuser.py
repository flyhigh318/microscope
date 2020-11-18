import os,sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitor.settings")
sys.path.append(str(BASE_DIR))
print(sys.path)
import django
django.setup()

from django.contrib.auth.models import User

def createLoginUser(username,mail,password):
    user = User.objects.create_user(username, mail, password)
    user.is_staff = True
    user.save()

if __name__ == '__main__':
    username = 'admin'
    mail = 'admin@rootcloud.com'
    password = 'changeme'
    createLoginUser(username, mail, password)