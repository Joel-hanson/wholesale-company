import os
import time

from os import walk
from django.conf import settings


def get_file_details():
    file_details = []

    _, _, filenames = next(walk(settings.MEDIA_ROOT))
    for file_name in filenames:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        created = os.path.getctime(file_path)

        year, month, day, hour, minute, second = time.localtime(created)[:-3]
        file_details.append({
            'file_name': file_name,
            'created_at': "%02d/%02d/%d %02d:%02d:%02d"%(day, month, year, hour, minute, second)
        })
    return file_details


def get_last_created_file():
    file_name = None
    last_created_at = None
    file_path = None

    _, _, filenames = next(walk(settings.MEDIA_ROOT))
    for name in filenames:
        file_path = os.path.join(settings.MEDIA_ROOT, name)
        created = os.path.getctime(file_path)

        if last_created_at:
            if created > last_created_at:
                file_name = name
                last_created_at = created
        else:
            last_created_at = created
            file_name = name

    file_name_regex = "^{}$".format(file_name)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    return file_name_regex, file_path
