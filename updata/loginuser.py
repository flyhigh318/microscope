import logging
from django.contrib.auth.models import User
logging = logging.getLogger("instruction")

def createLoginUser(username="admin",mail="admin@rootcloud.com",password="changeme"):
    msg = ""
    user = User.objects.filter(username=username)
    if user.exists():
        msg = "default user {} is already created".format(username)
        logging.warn(msg)
    else:
        user = User.objects.create_user(username, mail, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        if User.objects.filter(username=username).exists():
            msg = "default user {} has been successfully created".format(username)
            logging.info(msg)
        else:
            msg = "default user {} has been failed created".format(username)
            logging.error(msg)
    return msg