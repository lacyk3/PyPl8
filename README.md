# PyPl8

Image analysis package for segmenting images of microbial communities and extracting quantitative features automatically. 

## Background
This package makes use of the cv2 and sci-kit image libraries. 

It was developed in the Dudley lab at Pacific Northwest Research Institute and currently is most useful for analyzing images of rectangularly arrayed
patches/colonies on omnitrays photographed against a dark background.

## Organization

* The function in the barcode methods can be used to rename images based on a barcode visible in the image if an excel spreadsheet 
relating barcode numbers to relevant plate information is provided.

* The functions in the preprocessing methods are used to crop each image to relevant areas of interest

* The file process_images.py contains the main functions for processing a single image or a batch of images

## Dependencies

This package was developed with the following versions of dependencies:
* python 3.10.1
* Ipython 7.29.0
* matplotlib 3.5.0
* numpy 1.19.2
* opencv-python 4.2.0.32
* pandas 1.3.4
* pyzbar 0.1.8
* scikit-image 0.18.3
* scipy 1.6.2

