import os
from os import listdir
from os.path import isfile, join, isdir
from rhs_mesial_api.settings import BASE_DIR

from ..models import *

def moveService():
    WORKING_DIR = BASE_DIR / 'media/service/'
    SERVICE_DIR = BASE_DIR / 'service/'

    if not isdir(SERVICE_DIR):
        os.mkdir(SERVICE_DIR)
    
    allFiles = [f for f in listdir(WORKING_DIR) if isfile(join(WORKING_DIR, f))]
    serviceFiles = [f for f in listdir(SERVICE_DIR) if isfile(join(SERVICE_DIR, f))]


    if len(allFiles) != 1 or not ('service.json' in allFiles):
        return False

    if len(serviceFiles) > 0:
        for f in serviceFiles:
            os.remove(join(SERVICE_DIR, f))
        GoogleAPIServiceJSON.objects.all().delete()

    f = allFiles[0]
    os.rename(join(WORKING_DIR, f), join(SERVICE_DIR, "service.json"))
    serviceFiles = [f for f in listdir(SERVICE_DIR) if isfile(join(SERVICE_DIR, f))]
    return 'service.json' in serviceFiles
