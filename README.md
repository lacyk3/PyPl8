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
