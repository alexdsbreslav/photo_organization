import pandas as pd
import numpy as np
import os
from exif import Image as im
import datetime
from pathlib import Path
import sys

# ---- define the file paths
package_root = os.path.dirname(os.path.abspath(''))


# ---- get the name of the library that I am checking
path_list = [str(i) for i in Path(os.path.abspath(library)).glob('**/*')]
file_list = [i for i in path_list if os.path.isfile(i)]
ext_list = [i[i.rfind('.'):] for i in file_list]

# ---- create the dataframe
df = pd.DataFrame({'filepath': file_list, 'file_ext': ext_list})

# ---- define the file type
image_file_types = ['.bmp', '.jpg', '.nef', '.tif', '.png', '.pdf', '.jpeg']
video_file_types = ['.mts', '.mov', '.mpg', '.mp4']
photoshop_file_types = ['.psd', '.psb']

df['file_type'] = np.where(df.file_ext.str.lower().isin(image_file_types), 'image',
                           np.where(df.file_ext.str.lower().isin(video_file_types), 'video',
                                    np.where(df.file_ext.str.lower().isin(photoshop_file_types), 'photoshop', 'other')))

# ---- identify the metadata
df['datetime'] = np.nan
open_idx = df[df.file_type == 'image'].index

print('{} items to parse'.format(len(open_idx)))
item_n = 0

for i in open_idx:
    item_n += 1
    if item_n in [int(len(open_idx)/20)*i for i in range(1, 21)]:
        print('{:.0f}% complete'.format((item_n/len(open_idx)*100)))

    try:
        with open(df.loc[i, 'filepath'], 'rb') as image_file:
            exif_im = im(image_file)
            if exif_im.has_exif:
                try:
                    df.loc[i, 'datetime'] = datetime.datetime.strptime(exif_im['datetime_original'], '%Y:%m:%d %H:%M:%S')
                except:
                    pass
            else:
                pass
    except:
        pass

df.to_hdf('photo_database.h5', library)
