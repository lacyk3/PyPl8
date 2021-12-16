import glob
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pyzbar.pyzbar import decode
from PIL.ExifTags import TAGS

# -----------------------------
# Functions
# -----------------------------

def get_field (exif,field):
    for (k,v) in exif.items():
        if TAGS.get(k) == field:
            return v

def rename_images(image_folder_path, mastersheet, code=''):
    '''
    Input: -file path to folder containing images to be renamed. eg. r'C:User\\Documents\\Image_Folder'
           -file name of .csv containing the information to be used in the new file name. 
           Required column titles are 'Barcode', 'Plate', and 'Condition'
           -string that is to be included in new image name as short hand for the folder. Default is blank.
    Output: None
    
    Running this function with the master sheet in the current working directory will result in renaming the 
    .jpg files within the input folder as 'Plate_Condition_code_hr-min-sec.jpg' where the appropriate plate 
    and condition info are determined by decoding the barcode within the image and matching the result with 
    the appropriate row in mastersheet.
    '''
    df = pd.read_excel (mastersheet)
    os.chdir(image_folder_path)
    s = df['Barcode']
    image_filenames = glob.glob('*.jpg')
    
    for filename in image_filenames:
        image = Image.open(filename)
        im = np.array(image)
        all_the_info = decode(im)
        if not all_the_info:
            continue
        barcode = all_the_info[0].data
        d = barcode.decode('ASCII')
        image_row = df.loc[s==int(d)]
        print(image_row)
        info = image_row.iloc[0]
        exif_data = image._getexif()
        DT = get_field(exif_data,'DateTime')
        Time = DT.split()[1]
        Time = Time.replace(':','-')
        new_name = info.Plate+'_'+info.Condition+'_'+str(info.Replicate)+'_'+code+'_'+Time+'.jpg'
        dst = new_name
        src = filename
        os.rename(src,dst)
        
def identityfxn(a):
    plt.plot(a,a)
    plt.show()
    return a
