from PIL import Image
from flask import url_for
from os import urandom
import random
from sklearn.datasets import fetch_lfw_people
import numpy as np
from sklearn.decomposition import PCA
import copy
import math
from os import mkdir
import pickle

def crop_and_save_image(image_url, x1, y1, x2, y2, w, h):
    # takes an image address and cropping coordinates and does the following:
    #   1. Crops the image to the desired coordinates
    #   2. Converts the image to B&W
    #   3. Resizes the image to 37x50
    #   4. Saves the new image in the static folder as a random hex string
    im = Image.open(str(image_url)[1:])
    im = im.convert(mode='L')
    w0, h0 = im.size
    scaling_factor = (w0+0.0)/int(w)
    x1 = int(int(x1)*scaling_factor)
    y1 = int(int(y1)*scaling_factor)
    x2 = int(int(x2)*scaling_factor)
    y2 = int(int(y2)*scaling_factor)
    filename = 'static/' + urandom(8).encode('hex')+'.jpg'
    im.crop((x1,y1,x2,y2)).resize((94,125)).save(filename)
    return filename

def save_image_vector(path,name,image):
    # Saves an input array as an immage in greyscale at the location path+name
    filename = path+name+'.jpg'
    im_rescaled = (255.9*(image-image.min())/(image.max()-image.min())).astype(np.uint8)
    im_array = np.reshape(im_rescaled,[125,94])
    im = Image.fromarray(im_array)
    im = im.convert('RGB')
    im.save(filename)

def eigenface_components(cropped_image_url):
    im = Image.open(cropped_image_url)
    im_vector = np.array(list(im.getdata()))

    # get eigenfaces and normalized input faces
    lfw_data = pickle.load(open('eigenface_data.p','rb'))
    arr_norm = lfw_data['arr_norm']
    mean_image = lfw_data['mean_image']
    eigenfaces = lfw_data['eigenfaces']

    # get PCA projection of input image img_idx
    img_idx = 1
    n_components = eigenfaces.shape[0]
    scores = np.dot(arr_norm[:,:], eigenfaces.T)
    score = np.dot(eigenfaces, im_vector)

    img_proj = []
    for i in range(n_components):
        proj = np.dot(score[i],eigenfaces[i,:])
        img_proj.append(proj)

    faces = mean_image
    face_list = []
    face_list.append(mean_image)
    for i in range(len(img_proj)):
        faces = np.add(faces, img_proj[i])
        face_list.append(faces)

    face_array = np.asarray(face_list)

    images_to_save_array = face_array[range(0,600,40)]
    path = 'static/'+urandom(8).encode('hex')+'/'
    mkdir(path)
    for index, image in enumerate(images_to_save_array):
        save_image_vector(path,str(40*index),image)

    return path
