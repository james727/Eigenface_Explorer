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
import process_image
import pickle

def get_eigenfaces():
    # get sklearn faces data set
    lfw_people = fetch_lfw_people(min_faces_per_person=70, resize=1.0)
    n_samples, h, w = lfw_people.images.shape
    np.random.seed(42)

    # get face data
    print "Getting LFW people data from SKLearn..."
    X = lfw_people.data

    # subtract average row from each row
    print "Normalizing image array..."
    mean_image = np.mean(X, axis = 0)
    arr_norm = np.zeros([n_samples, h*w])
    arr_norm = X - mean_image

    # run pca using the signular value decomposition
    print "Running PCA of input image set. This may take a few moments."
    pca = PCA()
    pca.fit(arr_norm)
    eigenfaces = pca.components_

    # Save images
    print "Saving eigenfaces..."
    path = 'static/eigenface_images/'
    for i, face in enumerate(eigenfaces[:50]):
        process_image.save_image_vector(path,str(i),face)
    print "Complete! Saving pickle files..."

    input_data = {'mean_image': mean_image, 'eigenfaces': eigenfaces, 'arr_norm': arr_norm}
    f = open('eigenface_data.p', 'wb')
    pickle.dump(input_data, f)
    f.close()
    print "Pickle files saved. Shutting up shop now."

if __name__=="__main__":
    get_eigenfaces()
