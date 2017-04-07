#!/usr/bin/python3

import httplib2
import os
import time
import datetime
import mimetypes
import shutil
import io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

import initial_upload

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


# Sample (reference) map of Google Docs MIME types to possible exports
# (for more information check about().get() method with exportFormats field)
GOOGLE_MIME_TYPES = {
    # 'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.google-apps.document': 'application/vnd.oasis.opendocument.text',
    # 'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.spreadsheet': 'application/x-vnd.oasis.opendocument.spreadsheet',
    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.google-apps.drawing': 'image/jpeg',
    'application/vnd.google-apps.script': 'application/vnd.google-apps.script+json'
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
}


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
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_tree(folder_name, folder_id, tree_list, 
             root, parents_id, service):
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
    parents_id[folder_name] = folder_id

    results = service.files().list(
        pageSize=100,
        q=("%r in parents and \
        mimeType = 'application/vnd.google-apps.folder'and \
        trashed != True" % folder_id)).execute()

    items = results.get('files', [])
    root += folder_name + '/'

    for item in items:
        parents_id[item['name']] = item['id']
        tree_list.append(root + item['name'])
        folder_id = [i['id'] for i in items
                     if i['name'] == item['name']][0]
        folder_name = item['name']
        get_tree(folder_name, folder_id, tree_list,
                 root, parents_id, service)


def download_file_from_gdrive(path, file, service):
    """Downloads file from Google Drive.

    If file is Google Doc's type, then it will be downloaded
    with the corresponding non-Google mimetype.

    Args:
        path: Directory string, where file will be saved.
        file: File information object (dictionary), including it's name, ID
        and mimeType.
        service: Google Drive service instance.
    """
    print(file['name'])
    file_id = file['id']
    if file['mimeType'] in GOOGLE_MIME_TYPES.keys():
        request = service.files().export_media(
            fileId=file_id,
            mimeType=GOOGLE_MIME_TYPES[file['mimeType']])
            # mimeType='application/pdf')
        # fh = io.FileIO(os.path.join(path, file['name']), 'wb')
        fh = io.FileIO(os.path.join(path, file['name']), 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    else:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(os.path.join(path, file['name']), 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download %d%%." % int(status.progress() * 100))


def byLines(inputStr):
    return inputStr.count('/')


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    # Get id of Google Drive folder and it's path (from other script)
    folder_id, full_path = initial_upload.check_upload(service)
    folder_name = full_path.split('/')[-1]
    tree_list = []
    root = ''
    parents_id = {}

    About_drive = service.about().get(
        fields='importFormats, exportFormats').execute()
    print(About_drive)

    get_tree(folder_name, folder_id, tree_list,
             root, parents_id, service)
    os_tree_list = []
    root_len = len(full_path.split('/')[0:-2])

    # Get list of folders three paths on computer
    for root, dirs, files in os.walk(full_path, topdown=True):
        for name in dirs:
            var_path = '/'.join(root.split('/')[root_len + 1:])
            os_tree_list.append(os.path.join(var_path, name))

    # old folders on computer
    download_folders = list(set(tree_list).difference(set(os_tree_list)))
    # new folders on computer, which you dont have(i suppose heh)
    remove_folders = list(set(os_tree_list).difference(set(tree_list)))
    # foldes that match
    exact_folders = list(set(os_tree_list).intersection(set(tree_list)))

    exact_folders.append(folder_name)

    # Download folders from Drive
    download_folders = sorted(download_folders, key=byLines)

    for folder_dir in download_folders:
        var = '/'.join(full_path.split('/')[0:-1]) + '/'
        variable = var + folder_dir
        last_dir = folder_dir.split('/')[-1]

        folder_id = parents_id[last_dir]
        results = service.files().list(
            pageSize=20, q=('%r in parents' % folder_id)).execute()

        items = results.get('files', [])
        os.makedirs(variable)
        files = [f for f in items
                 if f['mimeType'] != 'application/vnd.google-apps.folder']

        for file in files:
            # file_id = f['id']
            download_file_from_gdrive(variable, file, service)

    # Check and refresh files in existing folders
    for folder_dir in exact_folders:
        var = '/'.join(full_path.split('/')[0:-1]) + '/'
        variable = var + folder_dir
        last_dir = folder_dir.split('/')[-1]
        os_files = [f for f in os.listdir(variable)
                    if os.path.isfile(os.path.join(variable, f))]
        folder_id = parents_id[last_dir]

        results = service.files().list(
            pageSize=100,
            q=('%r in parents and \
            mimeType!="application/vnd.google-apps.folder"' % folder_id),
            fields="nextPageToken, \
            files(id, name, mimeType, modifiedTime)").execute()

        items = results.get('files', [])

        refresh_files = [f for f in items if f['name'] in os_files]
        upload_files = [f for f in items if f['name'] not in os_files]
        remove_files = [f for f in os_files
                        if f not in [j['name']for j in items]]

        for file in refresh_files:
            file_dir = os.path.join(variable, file['name'])
            file_time = os.path.getmtime(file_dir)
            mtime = file['modifiedTime']
            mtime = datetime.datetime.strptime(mtime[:-2],
                                               "%Y-%m-%dT%H:%M:%S.%f")
            drive_time = time.mktime(mtime.timetuple())

            if (file_time < drive_time):
                os.remove(os.path.join(variable, file['name']))
                download_file_from_gdrive(variable, file, service)

            else:
                pass

        for file in remove_files:
            os.remove(os.path.join(variable, file))

        for file in upload_files:
            download_file_from_gdrive(variable, file, service)

    # Delete old and unwanted folders from computer
    remove_folders = sorted(remove_folders, key=byLines, reverse=True)

    for folder_dir in remove_folders:
        var = '/'.join(full_path.split('/')[0:-1]) + '/'
        variable = var + folder_dir
        last_dir = folder_dir.split('/')[-1]
        shutil.rmtree(variable)

if __name__ == '__main__':
    main()
