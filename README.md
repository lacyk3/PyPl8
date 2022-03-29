# PyPl8

Image analysis package for segmenting images of microbial communities and extracting quantitative features automatically. 

## Background
This package makes use of the cv2 and sci-kit image libraries for image processing. 

It was developed in the Dudley lab at Pacific Northwest Research Institute and is currently most useful for analyzing images of rectangularly arrayed
patches/colonies on agar plates photographed against a dark background.

## Organization

* **PyPl8.BarcodeMethods** contains the function `Rename()`. This function renames a folder of images by matching the barcode visible in each image to information provided in an excel spreadsheet. Barcodes are detected using pyzbar. 
See their [documentation](https://pypi.org/project/pyzbar/) for a list of recognizable barcode styles. 

* **PyPl8.PreprocessingMethods** contains functions used to crop each image to relevant areas of interest prior to segmentation. 

* **ProcessImages.py** contains the function `ProcessImage()` for processing a single image and the functions `ProcessBatch()` and `ParallelProcessBatch()` for processing a folder of images with the same settings.

* The package contains 3 example images,`Funnel()`, `PSAT1()`, and `OTC()`, which can be used to test out the package.
The function `ProcessImageTest()`, processes images already loaded into the workspace as arrays as the example images would be.

* To check which version of PyPl8 you have installed run
```
    import PyPl8
    PyPl8.__version__
```
## Examples

Check out the Examples folder for jupyter notebooks using the functions `PyPl8.Barcodes.BarcodeMethods.Rename()`, `PyPl8.ProcessImage()`, `PyPl8.ProcessBatch()`, `PyPl8.ParallelProcessBatch()`, and `PyPl8.TestProcessImage()`.


## Functions

`PyPl8.Barcodes.BarcodeMethods.Rename(image_folder, master_sheet, column_list, code='', delimiter='_', datetime_delimiter='-', datetime=True)`

> You can use the `Rename()` function from `PyPl8.Barcodes.BarcodeMethods` to rename a folder of images. The function will first make a list of the .jpg files in the input folder. Then it will load the provided excel or csv file and convert it to a data frame. The data frame will be used to map from the barcode numbers to the relevent information to be used in the new name. For the function to work correctly, the barcodes must be in the first column of the excel or csv file and have the column title "Barcode". The other column names can be whatever you choose, but should not contain spaces. Once the reference data frame has been built, the function will loop through each image on the file list and 
> * Load the image
> * Detect and decode the barcode using a function from pyzbar. This function can detect many different barcode types. See the [pyzbar documentation](https://pypi.org/project/pyzbar/) for more info.
> * If the barcode is not successfully detected or decoded the image's original filename will be printed to the screen along with an error message and it will remain unmodified.
> * After successful barcode detection, a new name will be built for the image from the corresponding row of the data frame and the image will be renamed accordingly in place.
> * If the detected barcode is not included in the reference sheet, the image's original filename will be printed to the screen along with an error message and it will remain unmodified.
#### Parameters
* **image_folder:** *string (required)* <br> path to the folder containing .jpg images to be renamed
* **master_sheet:** *string (required)* <br> the name of the file containing the barcode and naming information. The file should be located in the current working directory where the `Rename()` function is called. Either excel or comma-separated-value files can be used. For the function to work correctly, the barcodes must be in the first column of the excel or csv file and have the column title "Barcode". 
* **column_list:** *list of strings (required)* <br> list containing the titles of columns to be included in the new image name. List should be ordered according to the order you want entries be included in the new name.
* **code:** *string (optional)* <br> This is a bonus parameter that can be used to append an addiitional string to all image names in the folder. For example, for a folder of images taken 24 hours after pinning, you might want to use code = '24h'. The default is to leave this out of the image name.
* **delimiter:** *string (optional)* <br> The delimiter will be used to separate the info from each column included in the new image name. The default is to use an underscore.  
* **datetime:** *boolean (optional)* <br> The boolean value, either True or False indicates whether to append the date time information to the end of the image name. The default value is True, and the new image name will include the hr-min-sec extracted from the image metadata.
* **datetime_delimiter:** *string (optional)* <br> The datetime_delimiter is used to separate the hours, minutes and seconds at which the image was taken. The default value is a single hyphen. If you want to use hyphens as the regular delimiter, you may want to change this. 

#### Returns
None. Files will be renamed inplace.

```
df, tiles, masks, corners = PyPl8.ProcessImage(file, sourcefolder, outputfolder,
                                               crop_method = 'Auto', crop_param = None, adjust = True, rotate = False, 
                                               s = 200, array_dimensions = (8,12), 
                                               pin_size = 25, features = 'size', save = True, 
                                               display = False, calibrate = False)
```
> You can use the function `ProcessImage()` to segment and extract quantititative values from a single plate image. The default is to extract only size features, which include the patch area, average pixel intensity, sum of pixel intensities, and perimeter. However, you can also extract texture features which include the variance of pixel intensities, the "complexity score" of the patch, and 10 [local binary pattern scores](https://scikit-image.org/docs/stable/auto_examples/features_detection/plot_local_binary_pattern.html) reflecting performing the LBP transform with a neighborhood of 9 pixels. The complexity score is calculated by taking the sobel transform twice, summing over the patch area and then dividing by the patch area.

#### Parameters
- **file string:** *string (required)* Name of image to be processed including file extension
- **sourcefolder:** *string (required)* Path to folder containing images to be processed
- **outputfolder:** *string (required)* Path to desired location for function output to be saved. If the folder does not exist, it will be created during processing as long as it is a valid path. If you are using save = False, then you can provide a dummy variable like [] in place of a folder path. 
- **crop_method:** *string (optional)* There are 3 possible methods for pre-processing the images. The default value is `'Auto'`, which detects the agar plate by thresholding the whole image and then estimates pin locations based on the plate shape. This method generally works well when plates are placed parallel to the edges of the photo and the majority of patches have significant growth. It relies fairly heavily on the autoadjustment after initial guess, so if lots of patches are not growing well it fails because there is not a good reference point to adjust to. A second option is `'Grid'`, in which the user inputs the position of the center of patch A1 either through `crop_param` or upon viewing the image in the notebook. On a windows or mac operating system, you can also use the '`Click`' option, which will open the image in another window and you can click on the A1 location to provide the necessary reference point. See example notebook for more information on how to use the `Click` option.
- **features:** *string (optional)* The default value is `'size'`, which will extract the area, average pixel intensity, total pixel sum, and perimeter of each patch. If you want to additionally extract texture features, set `features = 'all'`.
- **pin_size:** *integer (optional)* Estimated minimum patch radius in pixels, which corresponds to the radius of the pin used to place cells. The default value is 25, which is the lowest size that has fit experimental data from the Dudley lab. For the funnel cross data, a pin size of 28 was used. If you set pin_size = 0, then during the segmentation step, otsu thresholding alone will be used and circle detection will be skipped. 
- **crop_param:** *tuple of integers (optional)* When using the `'Grid'` crop method you can enter an estimate of the location of the center of patch A1 in the form (row, column) instead of using the image display step. By default the value of crop_param is None, but a reference location of A1 = (600,600) is used. Note that the location (0,0) indicates the top left corner of the image.
- **s:** *integer (optional)* The side length of desired square regions of interest in pixels. The default value is 200 pixels.
- **array_dimensions:** *tuple of integers (optional)* The dimensions of the patch lay out on the plate in the form (number of rows, number of columns). The default value is (8,12). 
- **adjust:** *boolean (optional)* The default value is True. When True, adjust will perform a preliminary segmentation of each ROI and shift it so that the ROI is centered on the largest object in that intial area. If an ROI does not contain any detectable objects at this initial pass, it will be recentered based on the mean change in other patches in that row and column. For tricky images with lots of null growth I suggest carefully calibrating the reference point for the `Grid` cropping option, perhaps with a widget as shown below, and setting `adjust = False`. 
- **rotate:** *boolean (optional)* The default value is `False`. When `True`, plate images will be rotated 180 degrees before being processed. 
- **save:** *boolean (optional)* The default value is `True`. When `True`, the dataframe of quantitative outputs will be saved to the output folder as a csv file and the segmented image will be saved to the output folder as a jpg file. If `False`, nothing will be saved.
- **display:** *boolean (optional)* The default value is `False`. When true, the segmented image will be displayed to the screen after processing. 
- **calibrate:** *boolean (optional)* The default value is `False`. If using `Grid` crop, you can set `calibrate = True` in order to see the image displayed in line and enter the location of the center of patch A1. Note that the location (0,0) indicates the top left corner of the image. 

#### Returns
- **dataframe:** *pandas dataframe* If you want to explore the output from image processing in the jupyter notebook, pandas can be useful. Each row corresponds to a patch and each column contains the specified features. 
- **tiles:** *list of grayscale images* In case you want to reference the images that correspond to the data points in the data frame, you can use this list of tiles. They are ordered the same way as the dataframe. 
- **masks:** *list of binary images* To segment the tiles and look at the segmentation that corresponds to each data point, multiply the masks and tiles together. 
- **corners:** *list of tuples* This is a list of the location of the top left corner of each tile within the original image. It is used when reconstructing the segmented images. 
