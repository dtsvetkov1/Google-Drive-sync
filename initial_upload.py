#!/usr/bin/python3

import mimetypes
from apiclient.http import MediaFileUpload

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive Sync script'

# Declare full path to folder and folder name
# or put script near folder and simply declare './FOLDER_NAME'
FULL_PATH = '/home/danila/Folder/Projects/Python/DriveSync/Example'
DIR_NAME = 'Example'
# Or simply
# DIR_NAME = FULL_PATH.split('/')[-1]


def folder_upload(FULL_PATH, items, service):
    '''Uploads folder and all it's content (if it doesnt exists)
    in root folder.
    
    Args:
        FULL_PATH: Global variable string, path to folder (full or relative).
        items: List of folders in root path on Google Drive.
        service: Google Drive service instance.

    Returns:
        Dictionary, where keys are folder's names
        and values are id's of these folders.
    '''

    parents_id = {}

    for root, dirs, files in os.walk(FULL_PATH, topdown=True):
        last_dir = root.split('/')[-1]
        pre_last_dir = root.split('/')[-2]
        if pre_last_dir not in parents_id.keys():
            pre_last_dir = []
        else:
            pre_last_dir = parents_id[pre_last_dir]

        folder_metadata = {'name': last_dir,
                           'parents': [pre_last_dir],
                           'mimeType': 'application/vnd.google-apps.folder'}
        create_folder = service.files().create(body=folder_metadata,
                                               fields='id').execute()
        folder_id = create_folder.get('id', [])

        for name in files:
            file_metadata = {'name': name, 'parents': [folder_id]}
            media = MediaFileUpload(
                os.path.join(root, name),
                mimetype=mimetypes.MimeTypes().guess_type(name)[0])
            file = service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()

        parents_id[last_dir] = folder_id

    return parents_id


def check_upload(service):
    """Checks if folder is already uploaded, 
    and if it's not, uploads it.
    
    Args:
        service: Google Drive service instance.

    Returns:
        ID of uploaded folder, full path to this folder on computer.

    """

    results = service.files().list(
        pageSize=100,
        q="'root' in parents and trashed != True and \
        mimeType='application/vnd.google-apps.folder'").execute()

    items = results.get('files', [])

    # Check if folder exists, and then create it or get this folder's id.
    if DIR_NAME in [item['name'] for item in items]:
        folder_id = [item['id']for item in items
                     if item['name'] == DIR_NAME][0]
    else:
        parents_id = folder_upload(FULL_PATH, items, service)
        folder_id = parents_id[DIR_NAME]

    return folder_id, FULL_PATH
