import numpy as np
import astropy.io.fits as ap
from datetime import datetime
import os

# Set up
obs_path = "D:/Astro/data/obs_2019_5_07/"
exposure = "60sec"

# flat -->
flat_exposure = "5sec"

# clean -->
target = "sombrero"
cor_folder = "corrected/"

# align
coordinate_file_name = "align_coords.txt"

# filters
filters = ['r', 'g', 'b', 'ha', 'o3']

def main():

    #darks()
    
    # rgb
    for i in range(3):
        flats(filters[i])
        clean(filters[i])

    #flats(filters[3])
    #clean(filters[3])

def darks():

    # Gets list of dark file names
    dark_file_list = []
    for dark_file in os.listdir(obs_path):
        if dark_file.endswith("_" + exposure + ".fit") and dark_file.endswith("dark", 0, 4):
            dark_file_list.append(dark_file)
    
    # If there aren't any files, quits program
    if len(dark_file_list) <= 0:
        print("No dark files available")
        return

    # Gets list of dark data
    dark_images = [ap.getdata(obs_path + file) for file in dark_file_list]

    # create the master dark file by median combining the dark images
    master = np.median(dark_images, axis=0)
    master_dark = ap.PrimaryHDU(master)

    master_dark.writeto(obs_path + "master_dark_" + exposure + ".fits", overwrite=True)
    print("Master dark written successfully")


# Master Flats
def flats(img_filter):
    # Gets list of flat file names

    flat_file_list = []
    for flat_file in os.listdir(obs_path):
        if flat_file.endswith("_" + img_filter + "_" + flat_exposure + ".fit") and flat_file.endswith("flat", 0, 4):
            flat_file_list.append(flat_file)

    # If there aren't any files, quits program
    if len(flat_file_list) <= 0:
        print("No flat files available")
        return

    # Gets list of flat data
    raw_flat_images = [ap.getdata(obs_path + file) for file in flat_file_list]

    # Gets master dark
    master_dark = ap.getdata(obs_path + "master_dark_" + exposure + ".fits")

    # Subtracts master dark from each raw flat image for un-normalized flat image
    sub = []
    for img in raw_flat_images:
        sub.append(np.subtract(img, master_dark))
        
    un_master_flat = np.median(sub, axis=0)
    mean = np.mean(un_master_flat)
    master_flat = np.divide(un_master_flat, mean)
    master_flat = ap.PrimaryHDU(master_flat)

    # Writes to master file
    master_flat.writeto(obs_path + "master_flat_" + img_filter + "_" + flat_exposure + ".fits", overwrite=True)
    print("Master flat written successfully")


# Gets clean image from raw image using dark and flat masters
def clean(img_filter):

    # Gets list of file names
    img_file_list = []
    for img_file in os.listdir(obs_path):
        if img_file.endswith("_" + img_filter + "_" + exposure + ".fit") and img_file.endswith(target, 0, len(target)):
            img_file_list.append(img_file)

    # If there aren't any files, quits program
    if len(img_file_list) <= 0:
        print("No images available")
        return

    # Gets list of image data
    raw_images = [ap.getdata(obs_path + file) for file in img_file_list]

    # Gets master dark
    master_dark = ap.getdata(obs_path + "master_dark_" + exposure + ".fits")

    # Gets master flat
    master_flat = ap.getdata(obs_path + "master_flat_" + img_filter + "_" + flat_exposure + ".fits")

    # Subtracts master dark from each raw image and divides by master flat for corrected image
    cor_image_data = [np.divide(np.subtract(raw_img, master_dark), master_flat) for raw_img in raw_images]

    cor_images = [ap.PrimaryHDU(img_data) for img_data in cor_image_data]

    # Writes corrected file
    for i in range(len(cor_images)):
        cor_images[i].writeto(obs_path + cor_folder + "cor_" + str(img_file_list[i]), overwrite=True)

    print("Corrected images written successfully")


# Aligns stack of corrected images
def align(img_filter):
    
    # Collects files matching setup parameters
    img_files = []
    for file in os.listdir(obs_path):
        if file.endswith("_" + img_filter + "_" + exposure + ".fit") and file.endswith("cor_" + target, 0, len(target) + 4):
            img_files.append(file)
            
    # If there aren't any files, quits program
    if len(img_files) <= 0:
        print("No images available")
        return
            
    # List containing image data of files
    images = [ap.getdata(obs_path + file) for file in img_files]


main()
