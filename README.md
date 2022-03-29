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


