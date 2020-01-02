import pandas as pd
import numpy as np
import os
import datetime
import shutil
import sys

# ---- define the file paths
package_root = os.path.dirname(os.path.abspath(''))
library = os.path.join(package_root, 'photo_libraries')

# ---- get database
df = pd.read_hdf(os.path.abspath('photo_database.h5'), 'input')
if 'datetime' not in df.columns:
    raise Exception('database does not contain image metadata')

# ---- check that the dates are valid
check_dt = df[pd.notnull(df.datetime)]
invalid_dt = check_dt[(check_dt.datetime > datetime.datetime.today()) |
                (check_dt.datetime < datetime.datetime.utcfromtimestamp(0))].index
df.loc[invalid_dt, 'datetime'] = np.nan

# ---- create the photo archive folder
root = os.path.join(package_root, 'photo_archive')
try:
    os.mkdir(os.path.join(root))
    print('created photo archive')
except FileExistsError:
    pass

# ---- create folders for files that do not have metadata
for file_type in df.file_type.unique():
    try:
        os.mkdir(os.path.join(root, file_type))
        print('created sub-folder for {}'.format(file_type))
    except FileExistsError:
        pass

# ---- create folder for images that do no have metadata
try:
    os.mkdir(os.path.join(root, 'image', 'unknown'))
    print('created sub-folder for images without metadata')
except FileExistsError:
    pass

# ---- create folders for each unique year:
if df.datetime.notnull().all():
    for year in df.datetime.dt.year.unique():
        if pd.notnull(year):
            try:
                os.mkdir(os.path.join(root, 'image', str(int(year))))
                print('created sub-folder: {}'.format(str(int(year))))
            except FileExistsError:
                pass

# ---- create destination codes
def create_destinations(df):
    seed_since_epoch = int((datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds())
    rng = np.random.RandomState(seed_since_epoch)

    df['img_id'] = ['img_id_'+str(i).zfill(10) for i in rng.randint(0,1e10, len(df))]
    df['file_name'] = [df.filepath.loc[i][df.filepath.loc[i].rfind('/')+1:] for i in df.filepath.index]

    if df.datetime.notnull().all():
        df['file_name'] = np.where(pd.notnull(df.datetime), 'date_'+df.datetime.dt.strftime('%Y%m%d') + '_' + df.img_id + df.file_ext.str.lower(), df.file_name)

    destination = []
    for i in df.index:
        if pd.isnull(df.loc[i, 'datetime']):
            if df.loc[i, 'file_type'] == 'image':
                destination.append(os.path.join(root, df.loc[i, 'file_type'], 'unknown', df.loc[i, 'file_name']))
            else:
                destination.append(os.path.join(root, df.loc[i, 'file_type'], df.loc[i, 'file_name']))
        else:
            destination.append(os.path.join(root, df.loc[i, 'file_type'], df.loc[i, 'datetime'].strftime('%Y'), df.loc[i, 'file_name']))
    df['destination'] = destination
    return df


# ---- function to move the file
def move_file(idx, df):
    try:
        shutil.move(df.loc[idx,'filepath'], df.loc[idx, 'destination'])

    except PermissionError:
        raise PermissionError('permission error moving {} to {}'\
            .format(df.loc[idx, 'filepath'], df.loc[idx, 'destination']))
    return


# ---- function to check for duplicate names and add DUPLICATE if it is
def check_for_duplicate_file_name(idx, df):
    i = 1
    while os.path.exists(df.loc[idx, 'destination']):
        if pd.isnull(df.loc[idx, 'datetime']):
            if df.loc[idx, 'file_type'] == 'image':
                df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                          'unknown', 'DUPLICATE{}_'.format(i) + df.loc[idx, 'file_name'])
            else:
                df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                          'DUPLICATE{}_'.format(i) + df.loc[idx, 'file_name'])
        else:
            df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                      df.loc[idx, 'datetime'].strftime('%Y'),
                                                      'DUPLICATE{}_'.format(i) + df.loc[idx, 'file_name'])
        i += 1
    return df


# ---- bring together the two functions above to move all of the images
def organize_files(df):
    for idx in df.index:
        # ---- make sure that the source file exists
        if not os.path.exists(df.loc[idx, 'filepath']):
            raise Exception('source file {} does not exist'.format(df.loc[idx, 'filepath']))
        else:
            df = check_for_duplicate_file_name(idx, df)
            move_file(idx, df)
    return df


df = create_destinations(df)
df = organize_files(df)
df.to_hdf('photo_database.h5', 'output')
