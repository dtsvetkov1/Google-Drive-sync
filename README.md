PICTURE HERE!

# Google-Drive-sync
A Python script to automatically syncronize your Google Drive content with local storage files.


# What iit can do (for now) (Features)
- Upload folder and all it's content from local storage to Google Drive
-  Syncronise (Check) changes on local storage with (same) Google Drive folder
-  Syncronise (Check) changes on Drive with it's local storage instance

So, it's two-way syncronisation of selected folders, which you can run at any time (in any 'direction') you want (isn't this a dream, yeah?).

# (Setup) Installation and autorun 

Edit client_secrets_sample.json and add your Google API client id and client secret (If you don't have one, get it [here]() and save as *client-secret.json*).

1) Get your .json client secret config file [here]() and put it in working directiory (dont forget to save it as *client-secret.json*)
1) In *initial_upload.py* file sript change gloval variables FULL_PATH and DIR_NAME to your's full folder path and folder's name which you want to upload/synconise, respectively.
1) First time you run *drive_sync.py* or *download_from_drive.py*, it will open browser/new tab so you can authenticate the script.
1) Run *drive_sync.py* script, if you want to apply changes mage on local storage to specific Google Drive folder, and run *download_from_drive.py* when you want to apply changes from that Google Drive folder to your local storage.
1) (Optional) put script that you need to cron or any other task planner that yoyu use.
1) Enjoy how simple it is!


## Requirements and Dependencies

To run this amasing stuff, you will need:

- Python 3 or higher installed
- Google API Python library. To install it simply run
  
  sudo pip install --upgrade google-api-python-client
(or see [here]() for more information)

- Google Account
- Internet connection

All of these items are extremely important, because if you wont have at list one of then, nothing will work :(

## Support

If you have any questions how to use this stuff, offerings or simply want to contact me, please write me any time  on [Telegram]() or [email]().


[composer.json]: ./composer.json
[Composer]: http://getcomposer.org/
[исходные коды]: https://github.com/Bashka/bricks_cli_routing/releases
[PHPUnit]: http://phpunit.de/
[обсуждение]: https://github.com/Bashka/bricks_cli_routing/issues
[Doxygen]: http://www.stack.nl/~dimitri/doxygen/index.html

