# photo_organization
I created these scripts for a personal project. A family member had over 200K photos spread across iCloud, Photos, and multiple backups. The number of Photos in their library was causing major performance issues on the computer and none of the archived/backed-up photos were easily accessible or searchable.

These scripts:
1. Identify all files and filetypes from an unorganized directory of files
2. Identify the image files and pulls their metadata whenever possible
3. Rename all of the image files with the date they were taken and a unique image id number (to ensure duplicates never get overwritten)
3. Reorganize the files into a `photo_archive` folder where:
    - Images, movies, photoshop files, and miscellaneous files are pulled out and placed in separate respective directories
    - Image files are placed in subfolders corresponding to the year they were taken


Requirements:
Python 3:
  - pandas
  - numpy
  - exif
  - datetime
  - pathlib

To use these scripts, you must first drop all photos and photo directories into a folder named `photo_libraries`.

Please reach out with any questions, concerns, or suggestions! alexander.breslav@duke.edu
