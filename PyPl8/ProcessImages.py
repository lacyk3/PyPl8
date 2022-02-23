# Load Packages
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from PIL import Image
from skimage import feature, filters, data, color, io
import skimage
from skimage.transform import hough_circle
from skimage.feature import peak_local_max
from skimage.draw import disk
from scipy.signal import find_peaks
from IPython.display import clear_output
#import collections

import sys
sys.path.append('./')
from skimage.filters import sobel
from scipy.signal import find_peaks
from pathlib import Path
import glob
import os
import shutil
import pandas as pd
from skimage.exposure import histogram

from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb
from shutil import copy2
import cv2

from .Preprocessing import PreprocessingMethods as PP
#from .Barcodes import BarcodeMethods as BM

# -- Functions for Segmentation
def CalculateBackground(tiles):
    if len(np.shape(tiles[0]))==3:
        gray_tiles = [skimage.color.rgb2gray(t) for t in tiles]
    else:
        gray_tiles = tiles.copy()
    
    # Compute average background value of agar
    background_list = [np.median(t[0:20,0:-5]) for t in gray_tiles]
    background = np.mean(background_list)
    return background

def SegmentTile(tile, background, pin_size=25, threshold_method='otsu'):
    # -- convert to grayscale
    if len(np.shape(tile))==3:
        t = skimage.color.rgb2gray(tile)
    else:
        t = tile.copy()
    # -- initial intensity threshold    
    if threshold_method == 'otsu' or threshold_method == 'Otsu':
        thresh = threshold_otsu(t[25:-25,25:-25])     
    else:
        print('Threshold method not recognized')
    # -- binarize and fill
    bw = closing(t > thresh, square(3))
    bw = ndi.binary_fill_holes(bw)    
    label_image = label(bw)
    label_objects, nb_labels = ndi.label(label_image>0)
    # Select largest object
    sizes = np.bincount(label_objects.ravel())
    mask_sizes = sizes > 2000
    mask_sizes[0] = 0
    colony_mask_temp = mask_sizes[label_objects]
    # remove artifacts connected to image border
    colony_mask = clear_border(colony_mask_temp)
    
    # -- For large patches, use threshold results. To leave out circle fitting for everything, use pin_size = 0
    # -- For small patches fit circle to tile with min radius of pin_size, max of pin_size + 10
    if pin_size > 0 and (np.sum(colony_mask) <= np.pi*(pin_size+10)**2 or thresh < background + 0.035): 
        # Circular Hough Transform
        edges = 1*(t>np.mean(t[35:-35,35:-35])+.01)
        edges_center = edges[35:-35,35:-35]
        hough_radii = np.arange(pin_size,pin_size+10, 1)
        hough_res = hough_circle(edges_center, hough_radii)
        centers = [] 
        accums = [] 
        radii = []
        for radius, h in zip(hough_radii, hough_res):
            # For each radius, extract one circle
            peaks = peak_local_max(h, num_peaks=1, min_distance=25)
            centers.extend(peaks)
            accums.extend(h[peaks[:, 0],peaks[:,1]])
            radii.extend([radius])
            
        # Consider Likelihood of candidate circles.
        if np.max(accums) <= 0.42: # change tile to blank if circles all less than 42%
            colony_mask = np.zeros_like(t)>0
        else: # Pick circle with highest likelihood that is less than 92% for mask 
            # (higher indicates that the circle is entirely contained in patch, not on the edge)
            accums = accums*np.array([x < 0.92 for x in accums])
            idx = np.argmax(accums)
            center_x, center_y = centers[idx]
            radius = radii[idx]
            # Build mask
            cx, cy = disk((center_x, center_y), radius)
            colony_mask_center = np.zeros_like(edges_center)
            colony_mask = np.zeros_like(edges)
            try:
                colony_mask_center[cx,cy] = 1
                colony_mask[35:-35,35:-35] = colony_mask_center
            except:
                pass
            # Boolean-ize it
            colony_mask = colony_mask>0
            # Combine with thresholding result if the colony is sufficiently brighter than background
            if thresh> background + 0.035: 
                label_objects, nb_labels = ndi.label(1*((label_image+colony_mask)>0))
                # Select largest object
                sizes = np.bincount(label_objects.ravel())
                mask_sizes = sizes > 2000
                mask_sizes[0] = 0
                colony_mask_temp = mask_sizes[label_objects]
                # remove artifacts connected to image border
                colony_mask = clear_border(colony_mask_temp)
    return colony_mask

def BuildSegmentedImage(image,colony_masks,corners):
    if len(np.shape(image))==3:
        img = skimage.color.rgb2gray(image)
    else:
        img = image.copy()
    
    label_image = label(1*(PP.MergeTiles(np.zeros_like(img),colony_masks, corners)>0))
    image_label_overlay = label2rgb(label_image, image=img, bg_label=0)   
    return image_label_overlay

# -- Functions for Quantitative Feature Extraction

def SizeFeatures(tile,mask):
    if len(np.shape(tile))==3:
        gray_tile = skimage.color.rgb2gray(tile)
    else:
        gray_tile = tile.copy()
    clean_tile = tile*mask

    area = np.sum(1*mask)
    pixel_sum = np.sum(clean_tile)
    if area > 0:
        avg_int = pixel_sum/area
    else:
        avg_int = 0
    perimeter = skimage.measure.perimeter(mask)
    background = np.sum(tile*(1-1*mask))/np.sum((1-1*mask))
    return [area, avg_int, pixel_sum, background, perimeter]

def TextureFeatures(tile,mask):
    if len(np.shape(tile))==3:
        gray_tile = skimage.color.rgb2gray(tile)
    else:
        gray_tile = tile.copy()
    area = np.sum(1*mask)                 
    selem = np.array([[0, 0, 0, 1, 0, 0, 0],
                      [0, 0, 1, 1, 1, 0, 0],
                      [0, 1, 1, 1, 1, 1, 0],
                      [1, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 1, 0],
                      [0, 0, 1, 1, 1, 0, 0],
                      [0, 0, 0, 1, 0, 0, 0]])
       
    if area > 0:
        # -- variance
        variance = np.var(tile[mask])
        # -- local binary patterns
        LBP = mask*skimage.feature.local_binary_pattern(tile, 8, 10, method='uniform') 
        hist, hist_centers = histogram(LBP[mask])
        temp = hist[hist>0]/area
        if len(temp) == 10:
                LBP_score = temp
        else:
            LBP_score = np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
        # sobel filter
        clean_tile = tile*mask
        mask_temp = clean_tile>0.2
        im = 255*clean_tile*mask_temp
        M = skimage.morphology.binary_erosion(clean_tile*mask_temp,selem=selem )
        im_contrast = skimage.exposure.adjust_gamma(im)
        filt1 = skimage.filters.sobel(im, mask=M)
        filt2 = skimage.filters.sobel(filt1, mask=M)
        C_score = np.sum(filt2[mask])/area
    else:
        variance = np.nan
        LBP_score = np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
        C_score = np.nan
    return [variance, C_score]+LBP_score.tolist()

def BuildDF(tiles,masks,features ='all',save=True):
    
    positions = ([x+y for x in ['A','B','C','D','E','F','G','H'] 
            for y in ['1','2','3','4','5','6','7','8','9','10','11','12']])    
    data = []
    if features == 'all':
        features = (['Position','Area','AvgInt','PixelSum', 'Background', 'Perimeter','Variance', 'Complexity',
                    'LBP1', 'LBP2','LBP3','LBP4','LBP5','LBP6','LBP7','LBP8','LBP9','LBP10'])
        j = 0
        for (tile,mask,position) in zip(tiles,masks,positions):
            size_features = SizeFeatures(tile,mask)
            texture_features = TextureFeatures(tile,mask)
            for t in texture_features:
                size_features.append(t)
            size_features.insert(0,position)    
            data.append(size_features.copy())
    elif features == 'size':
        features = ['Position','Area','AvgInt','PixelSum', 'Background', 'Perimeter']
        j = 0
        for (tile,mask,position) in zip(tiles,masks,positions):
            size_features = SizeFeatures(tile,mask)
            size_features.insert(0,position)    
            data.append(size_features.copy())
    else:
        print('Feature options are \"size\" or \"all\"')
                  
    df = pd.DataFrame(data, columns = features)
    return df

def ProcessImage(file, sourcefolder, outputfolder,
                 crop_method = 'Auto', pin_size = 25, crop_param = None, s = 200, array_dimensions = (8,12),
                 adjust = True, rotate = False, save = True, display = False, calibrate = False):
    
    image = PP.LoadImage(file, sourcefolder, rotate = rotate)
    
    if crop_method == 'Auto':
        tiles, corners = PP.AutoCrop(file, sourcefolder, rotate = rotate, 
                                  s = s, array_dimensions = array_dimensions, 
                                  adjust=adjust, display = display)    
    elif crop_method == 'Grid':
        if calibrate:
            not_accept = True
            while not_accept:
                PP.GridDisplay(image)
                c1 = int(input("Input the x position of the center of patch A1 in pixels and press enter."))
                r1 = int(input("Input the y position of the center of patch A1 in pixels and press enter."))
                clear_output()
                PP.EnhancedGridDisplay(image, (r1,c1),s,array_dimensions)
                user_input = input("Would you like to proceed? y/n")
                if user_input == 'y':
                    not_accept = False
                if user_input == 'n':
                    continue                 
            clear_output()
            crop_param = (r1,c1)            
        if crop_param:
            A1_location = crop_param
        else:
            A1_location = (650,600)
        tiles, corners = PP.GridCrop(file, sourcefolder, rotate = rotate, 
                                  A1_location = A1_location, s = s, array_dimensions = array_dimensions, 
                                  adjust=adjust, display = display)
    elif crop_method == 'Click':
        tiles, corners = PP.ClickCrop(file, sourcefolder, 
                                   s=s, array_dimensions = array_dimensions, 
                                   rotate = rotate, adjust = adjust)
    else:
        print('crop_method options are Auto, Grid, or Crop')
        
    background = CalculateBackground(tiles)
    masks = []
    for tile in tiles:
        masks.append(SegmentTile(tile, background, pin_size=pin_size, threshold_method='otsu'))
    
    image_label_overlay = BuildSegmentedImage(image,masks,corners)
    df = BuildDF(tiles, masks, features ='all',save=True)
    
    if save:
        filename = file.split('.')[0]+'.csv'
        (df.to_csv(os.path.join(outputfolder, filename), index=False))
        img_seg = 255*(image_label_overlay[200:-200,200:-200,:]) 
        A = Image.fromarray(img_seg.astype('uint8'), 'RGB')
        A.save(os.path.join(outputfolder,file.split('.')[0]+'_seg.jpg'))
    
    if display:
        fig, axs = plt.subplots(1,1,figsize=(12,16))
        axs.imshow(image_label_overlay[200:-200,200:-200,:]);
        axs.axis('off')
        plt.show();
    return df, tiles, masks, corners
    
def Process1Image(file, sourcefolder, outputfolder,
                 corners, pin_size = 25, s = 200, array_dimensions = (8,12),
                 adjust = True, rotate = False, save = True, display = False):
    # -- Load Image
    image = PP.LoadImage(file, sourcefolder, rotate = rotate)
    # -- Set Corners
    if adjust:
        new_corners = PP.AutoAdjust(image, corners, s = s, array_dimensions = array_dimensions)
        corners = PP.AutoAdjust(image, new_corners, s = s, array_dimensions = array_dimensions)
    else:
        corners = corners
    # -- Crop tiles    
    tiles = PP.MakeTiles(image, corners, s = s)        
    # -- Calculate Background value    
    background = CalculateBackground(tiles)
    # -- Segment tiles
    masks = []
    for tile in tiles:
        masks.append(SegmentTile(tile, background, pin_size=pin_size, threshold_method='otsu'))
    # -- Merge Segmented Plate image
    image_label_overlay = BuildSegmentedImage(image,masks,corners)
    # -- Extract Features
    df = BuildDF(tiles, masks, features ='all',save=True)
    # -- Save Results
    if save:
        filename = file.split('.')[0]+'.csv'
        (df.to_csv(os.path.join(outputfolder, filename), index=False))
        img_seg = 255*(image_label_overlay[200:-200,200:-200,:]) 
        A = Image.fromarray(img_seg.astype('uint8'), 'RGB')
        A.save(os.path.join(outputfolder,file.split('.')[0]+'_seg.jpg'))
    # -- Display Segmented Image
    if display:
        fig, axs = plt.subplots(1,1,figsize=(12,16))
        axs.imshow(image_label_overlay[200:-200,200:-200,:]);
        axs.axis('off')
        plt.show();
    return None    
        
def ProcessBatch(sourcefolder, outputfolder,   
                crop_method = 'Auto', s = 200, pin_size = 25, array_dimensions = (8,12),
                adjust = True, rotate = False, save = True, display = False):
    # -- Set Up Folders
    wd = os.getcwd()
    if save:
        if not os.path.isdir(outputfolder):
            os.mkdir(outputfolder)
    # -- List Files
    file_list = PP.ListFiles(sourcefolder)
    image_list = [x  for x in file_list if "jpg" or "JPG" or "JPEG" or "jpeg" in x]
    
    # -- Calibrate using first image
    file = image_list[0]
    df, tiles, masks, corners = ProcessImage(file, sourcefolder, outputfolder,
                                     crop_method = crop_method, crop_param = None, s = s, 
                                     array_dimensions = array_dimensions, pin_size = pin_size,
                                     adjust = adjust, rotate = rotate, 
                                     save = False, display = True, calibrate = True)
    PP.DisplayTiles(tiles)
    user_input = input("Would you like to proceed? y/n")
        
    # -- Process all images
    if user_input == 'y':
        lines = (['BATCH PROCESS PARAMETERS',
                'Crop method: '+crop_method, 
                'Tile side length: ' +str(s)+ ' pixels', 
                'Pin radius: '+str(pin_size)+ ' pixels', 
                'Array dimensions: '+str(array_dimensions),
                'Autoadjust: '+str(adjust), 
                'Rotate images: '+str(adjust),
                'SEGMENTATION PARAMETERS',
                'Minimum intensity: 0.035 + background',
                'Minimum area: np.pi*(pin_size+10)**2',
                'Minimum circle certainty: 0.42',
                'Maximum circle certainty: 0.92', 
                'CROPPING PARAMETERS',
                'Min object size in auto adjust: 2000 pixels',
                'Plate Height in auto crop: ~1700 pixels',
                'Plate intensity in auto crop: 0.5',
                'Row buffer in auto crop: 250',
                'Column buffer in auto crop: 175',
                'COMPLETION'])
        
        with open(os.path.join(outputfolder,'BatchParameters.txt'), 'w') as f:
            for line in lines:
                f.write(line)
                f.write('\n')
                
        count = 0
        for file in file_list:
            try:
                Process1Image(file, sourcefolder, outputfolder,
                     corners, s = s, array_dimensions = array_dimensions, pin_size = pin_size,
                     adjust = adjust, rotate = rotate, save = True, display = False)
                count = count+1
            except:
                continue
                
        file_object = open(os.path.join(outputfolder,'BatchParameters.txt'), 'a')
        file_object.write(str(count)+' out of '+ str(len(file_list))+ ' images processed.')
        file_object.close()
    return None
    
    
    
    
    
    
