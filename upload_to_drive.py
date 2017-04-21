#!/usr/bin/python3

"""Example cooment to make pylint stop giving me errors."""

import datetime
import hashlib
import mimetypes
import time
import os
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
# from oauth2client.tools import run

from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
# Import our folder uploading script
# import initial_upload

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive Sync'

# Declare full path to folder and folder name
FULL_PATH = r'PUT YOUR FULL FOLDER PATH HERE'
DIR_NAME = 'PUT YOUR FOLDER NAME HERE'
# Or simply
# DIR_NAME = FULL_PATH.split('/')[-1]

# Don't really need it here
GOOGLE_MIME_TYPES = {
    'application/vnd.google-apps.document':
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # 'application/vnd.oasis.opendocument.text',
    'application/vnd.google-apps.spreadsheet':
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    # 'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.google-apps.presentation':
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    # 'application/vnd.oasis.opendocument.presentation'
}

# 'application/vnd.google-apps.folder': '',
# 'application/vnd.google-apps.form': 'application/pdf',
# 'application/vnd.google-apps.fusiontable': '',
# 'application/vnd.google-apps.map': 'application/pdf',
# 'application/vnd.google-apps.photo': 'image/jpeg',
# 'application/vnd.google-apps.file': '',
# 'application/vnd.google-apps.sites': '',
# 'application/vnd.google-apps.unknown': '',
# 'application/vnd.google-apps.video': '',
# 'application/vnd.google-apps.audio': '',
# 'application/vnd.google-apps.drive-sdk': ''
# 'application/octet-stream': 'text/plain'


def folder_upload(service):
    '''Uploads folder and all it's content (if it doesnt exists)
    in root folder.

    Args:
        items: List of folders in root path on Google Drive.
        service: Google Drive service instance.

    Returns:
        Dictionary, where keys are folder's names
        and values are id's of these folders.
    '''

    parents_id = {}

    for root, _, files in os.walk(FULL_PATH, topdown=True):
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
            service.files().create(body=file_metadata,
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
        parents_id = folder_upload(service)
        folder_id = parents_id[DIR_NAME]

    return folder_id, FULL_PATH




def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-sync.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # if flags:
        credentials = tools.run_flow(flow, store, flags=None)
        # else:  # Needed only for compatibility with Python 2.6
        # flags = None
        # credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ', credential_path)
    return credentials


def get_tree(folder_name, tree_list, root, parents_id, service):
    """Gets folder tree relative paths.

    Recursively gets through subfolders, remembers their names ad ID's.

    Args:
        folder_name: Name of folder, initially
        name of parent folder string.
        folder_id: ID of folder, initially ID of parent folder.
        tree_list: List of relative folder paths, initially
        empy list.
        root: Current relative folder path, initially empty string.
        parents_id: Dictionary with pairs of {key:value} like
        {folder's name: folder's Drive ID}, initially empty dict.
        service: Google Drive service instance.

    Returns:
        List of folder tree relative folder paths.

    """
    folder_id = parents_id[folder_name]

    results = service.files().list(
        pageSize=1000,
        q=("%r in parents and \
        mimeType = 'application/vnd.google-apps.folder'and \
        trashed != True" % folder_id)).execute()

    items = results.get('files', [])
    root += folder_name + os.path.sep

    for item in items:
        parents_id[item['name']] = item['id']
        tree_list.append(root + item['name'])
        folder_id = [i['id'] for i in items
                     if i['name'] == item['name']][0]
        folder_name = item['name']
        get_tree(folder_name, tree_list,
                 root, parents_id, service)


def by_lines(input_str):
    """Helps Sort items by the number of slashes in it.

    Returns:
        Number of slashes in string.
    """
    return input_str.count(os.path.sep)


def main():
    """Syncronizes computer folder with Google Drive folder.

    Checks files if they exist, uploads new files and subfolders,
    deletes old files from Google Drive and refreshes existing stuff.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    # Get id of Google Drive folder and it's path (from other script)
    # folder_id, full_path = initial_upload.check_upload(service)
    folder_id, full_path = check_upload(service)
    folder_name = full_path.split(os.path.sep)[-1]
    tree_list = []
    root = ''
    parents_id = {}

    parents_id[folder_name] = folder_id
    get_tree(folder_name, tree_list, root, parents_id, service)
    os_tree_list = []
    root_len = len(full_path.split(os.path.sep)[0:-2])

    # Get list of folders three paths on computer
    for root, dirs, files in os.walk(full_path, topdown=True):
        for name in dirs:
            var_path = (os.path.sep).join(
                root.split(os.path.sep)[root_len + 1:])
            os_tree_list.append(os.path.join(var_path, name))

    # old folders on drive
    remove_folders = list(set(tree_list).difference(set(os_tree_list)))
    # new folders on drive, which you dont have(i suppose hehe)
    upload_folders = list(set(os_tree_list).difference(set(tree_list)))
    # foldes that match
    exact_folders = list(set(os_tree_list).intersection(set(tree_list)))

    # Add starting directory
    exact_folders.append(folder_name)
    # Sort uploadable folders
    # so now in can be upload from top to down of tree
    upload_folders = sorted(upload_folders, key=by_lines)

    # Here we upload new (abcent on Drive) folders
    for folder_dir in upload_folders:
        var = os.path.join(full_path.split(os.path.sep)[0:-1]) + os.path.sep
        variable = var + folder_dir
        last_dir = folder_dir.split(os.path.sep)[-1]
        pre_last_dir = folder_dir.split(os.path.sep)[-2]

        files = [f for f in os.listdir(variable)
                 if os.path.isfile(os.path.join(variable, f))]

        folder_metadata = {'name': last_dir,
                           'parents': [parents_id[pre_last_dir]],
                           'mimeType': 'application/vnd.google-apps.folder'}
        create_folder = service.files().create(
            body=folder_metadata, fields='id').execute()
        folder_id = create_folder.get('id', [])
        parents_id[last_dir] = folder_id

        for os_file in files:
            some_metadata = {'name': os_file, 'parents': [folder_id]}
            os_file_mimetype = mimetypes.MimeTypes().guess_type(
                os.path.join(variable, os_file))[0]
            media = MediaFileUpload(os.path.join(variable, os_file),
                                    mimetype=os_file_mimetype)
            upload_this = service.files().create(body=some_metadata,
                                                 media_body=media,
                                                 fields='id').execute()
            upload_this = upload_this.get('id', [])

    # Check files in existed folders and replace them
    # with newer versions if needed
    for folder_dir in exact_folders:

        var = (os.path.sep).join(full_path.split(
            os.path.sep)[0:-1]) + os.path.sep

        variable = var + folder_dir
        last_dir = folder_dir.split(os.path.sep)[-1]
        # print(last_dir, folder_dir)
        os_files = [f for f in os.listdir(variable)
                    if os.path.isfile(os.path.join(variable, f))]
        results = service.files().list(
            pageSize=1000, q=('%r in parents and \
            mimeType!="application/vnd.google-apps.folder" and \
            trashed != True' % parents_id[last_dir]),
            fields="files(id, name, mimeType, \
            modifiedTime, md5Checksum)").execute()

        items = results.get('files', [])

        refresh_files = [f for f in items if f['name'] in os_files]
        remove_files = [f for f in items if f['name'] not in os_files]
        upload_files = [f for f in os_files
                        if f not in [j['name']for j in items]]

        # Check files that exist both on Drive and on PC
        for drive_file in refresh_files:
            file_dir = os.path.join(variable, drive_file['name'])
            file_time = os.path.getmtime(file_dir)
            mtime = [f['modifiedTime']
                     for f in items if f['name'] == drive_file['name']][0]
            mtime = datetime.datetime.strptime(
                mtime[:-2], "%Y-%m-%dT%H:%M:%S.%f")
            drive_time = time.mktime(mtime.timetuple())
            # print(drive_file['name'])
            # if file['mimeType'] in GOOGLE_MIME_TYPES.keys():
            # print(file['name'], file['mimeType'])
            # print()
            os_file_md5 = hashlib.md5(open(file_dir, 'rb').read()).hexdigest()
            if 'md5Checksum' in drive_file.keys():
                # print(1, file['md5Checksum'])
                drive_md5 = drive_file['md5Checksum']
                # print(2, os_file_md5)
            else:
                # print('No hash')
                drive_md5 = None
                # print(drive_md5 != os_file_md5)

            if (file_time > drive_time) or (drive_md5 != os_file_md5):
                file_id = [f['id'] for f in items
                           if f['name'] == drive_file['name']][0]
                file_mime = [f['mimeType'] for f in items
                             if f['name'] == drive_file['name']][0]

                # File's new content.
                # file_mime = mimetypes.MimeTypes().guess_type(file_dir)[0]
                file_metadata = {'name': drive_file['name'],
                                 'parents': [parents_id[last_dir]]}
                # media_body = MediaFileUpload(file_dir, mimetype=filemime)
                media_body = MediaFileUpload(file_dir, mimetype=file_mime)
                # print('I am HERE, ', )
                service.files().update(fileId=file_id,
                                       media_body=media_body,
                                       fields='id').execute()

        # Remove old files from Drive
        for drive_file in remove_files:

            file_id = [f['id'] for f in items
                       if f['name'] == drive_file['name']][0]
            service.files().delete(fileId=file_id).execute()

        # Upload new files on Drive
        for os_file in upload_files:

            file_dir = os.path.join(variable, os_file)

            # File's new content.
            filemime = mimetypes.MimeTypes().guess_type(file_dir)[0]
            file_metadata = {'name': os_file,
                             'parents': [parents_id[last_dir]]}
            media_body = MediaFileUpload(file_dir, mimetype=filemime)

            service.files().create(body=file_metadata,
                                   media_body=media_body,
                                   fields='id').execute()

    remove_folders = sorted(remove_folders, key=by_lines, reverse=True)

    # Delete old folders from Drive
    for folder_dir in remove_folders:
        var = (os.path.sep).join(full_path.split(
            os.path.sep)[0:-1]) + os.path.sep
        variable = var + folder_dir
        last_dir = folder_dir.split('/')[-1]
        folder_id = parents_id[last_dir]
        service.files().delete(fileId=folder_id).execute()

if __name__ == '__main__':
    main()
