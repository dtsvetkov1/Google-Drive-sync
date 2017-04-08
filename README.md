![Google Drive sync logo](./google-drive-logo-logo.png)
# Google-Drive-sync
A Python script to automatically synchronize your Google Drive content with local storage files.

# What it can do (for now)
- Upload folder and all it's content from local storage to Google Drive
-  Check and synchronize changes on local storage with (same) Google Drive folder
-  Check and synchronize changes on Drive with its local storage instance

So, it's two-way synchronization of selected folders, which you can run at any time (in any 'direction') you want (isn't this a dream, yeah?).

# Setup and autorun 

1) Turn on Google Drive API [here] (if you have any troubles, check [Python Quickstart guide]).
1) Get your .json client secret config file in [Google API Projects page] and put it in working directory (don't forget to save it as *client-secret.json*)
1) In *initial_upload.py* file script change global variables FULL_PATH and DIR_NAME to your's full folder path and folder's name, which you want to upload/synchronize, respectively.
1) First time you run *drive_sync.py* or *download_from_drive.py*, it will open browser/new tab, and you will need to authenticate the script (or if it doesn't redirect you, copy the link and do authentification manually).
1) Run *drive_sync.py* script, if you want to apply changes made on local storage to specific Google Drive folder, and run *download_from_drive.py* if you want to apply changes from that Google Drive folder to your local storage.
1) (Optional) put script that you need to cron or any other task planner that you use.
1) Enjoy how simple it is!

## Requirements and Dependencies

To run this amazing project, you will need:

- Python 3 or higher installed
- Google API Python library. To install it simply run
```
   sudo pip install --upgrade google-api-python-client
```
(or see this [installation page] for more information)

- Google Account
- Internet connection

All of these items are extremely important because if you won't have at least one of then, nothing will work :('

## Support

If you have any questions how to use this stuff, offerings or simply want to contact me, please write me anytime on Telegram [@I_love_cats1] or email <danilatsvet@gmail.com>.


[installation page]: https://developers.google.com/api-client-library/python/start/installation
[@I_love_cats1]: https://web.telegram.org/#/im?p=@I_love_cats1
[here]: https://console.developers.google.com/flows/enableapi?apiid=drive
[Python Quickstart guide]: https://developers.google.com/drive/v3/web/quickstart/python
[Google API Prijects page]: https://console.developers.google.com/iam-admin/projects
