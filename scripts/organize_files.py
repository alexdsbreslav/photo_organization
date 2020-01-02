import pandas as pd
import numpy as np
import os
import datetime
import shutil
import sys

# ---- get database
library = sys.argv[1]
df = pd.read_hdf(os.path.abspath('photo_database.h5'), library)
if 'datetime' not in df.columns:
    raise Exception('database does not contain image metadata')

# ---- check that the dates are valid
invalid_dt = df[(df.datetime > datetime.datetime.today()) | (df.datetime < datetime.datetime.utcfromtimestamp(0))].index
df.loc[invalid_dt, 'datetime'] = np.nan

# ---- identify the root directory
root = os.path.abspath('ob_photo_archive')
if not os.path.isdir(root):
    raise Exception('root directory not located')

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

def move_files(df):
    for idx in df.index:
        # ---- make sure that the source file exists
        if os.path.exists(df.loc[idx, 'filepath']):
            # ---- check to make sure that I am not overwriting anything
            if not os.path.exists(df.loc[idx, 'destination']):
                try:
                    shutil.move(df.loc[idx,'filepath'], df.loc[idx, 'destination'])
                except PermissionError:
                    print('permission error moving {} to {}'.format(df.loc[idx, 'filepath'], df.loc[idx, 'destination']))
            # ---- if I am, rename the file and then move it
            else:
                if pd.isnull(df.loc[idx, 'datetime']):
                    if df.loc[idx, 'file_type'] == 'image':
                        df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                                  'unknown', 'DUPLICATE_' + df.loc[idx, 'file_name'])
                    else:
                        df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                                  'DUPLICATE_' + df.loc[idx, 'file_name'])
                else:
                    df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                              df.loc[idx, 'datetime'].strftime('%Y'),
                                                              'DUPLICATE_' + df.loc[idx, 'file_name'])
                try:
                    if not os.path.exists(df.loc[idx, 'destination']):
                        shutil.move(df.loc[idx, 'filepath'], df.loc[idx, 'destination'])
                    else:
                        df.loc[idx, 'destination'] = os.path.join(root, df.loc[idx, 'file_type'],
                                                                  'DUPLICATE2_' + df.loc[idx, 'file_name'])
                        shutil.move(df.loc[idx, 'filepath'], df.loc[idx, 'destination'])

                except PermissionError:
                    print('permission error moving {} to {}'.format(df.loc[idx, 'filepath'],
                                                                    df.loc[idx, 'destination']))
    return


df = create_destinations(df)
move_files(df)
