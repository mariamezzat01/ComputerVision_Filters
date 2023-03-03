# imports
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy import ndimage
from skimage import io
from scipy import ndimage
import PIL
from PIL import Image
import pandas as pd
from skimage.io import imshow, imread
from skimage.color import rgb2gray
from skimage import img_as_ubyte, img_as_float
from skimage.exposure import histogram, cumulative_distribution
from IPython.display import display, Math, Latex
import matplotlib.image as mpimg
import random



# ------------------ IMAGE FUNCTIONS -------------------------------------

# function for displaying image
def display(img):
    plt.figure(figsize=(5,5))
    plt.imshow(img, cmap='gray')
    plt.axis('off')
    plt.show()

#function gray scale 
def rgbtogray(image):
    r,g,b=image[:,:,0],image[:,:,1],image[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray
# -----------------------NOISE ------------------------------------------


def salt_and_paper(img):
    row , col = img.shape
    g = np.zeros((row,col), dtype=np.float32)
    salt=0.95
    pepper=0.1
    for i in range(row):
        for j in range(col):
            rdn = np.random.random()
            if rdn < pepper:
                g[i][j] = 0
            elif rdn > salt:
                g[i][j] = 1
            else:
                g[i][j] = img[i][j]
    return g

#low : lower boundry of output interval
#high: Upper boundary of the output interval. All values generated will be less than or equal to high. The high limit may be included in the returned array of floats due to floating-point rounding in the equation low + (high-low) * random_sample(). The default value is 1.0.
def uniform_noise(img):
    row,col=img.shape
    low = 0
    high = 1
    uni = np.zeros((row,col), dtype=np.float64)
    for i in range(row):
        for j in range(col):
            uni[i][j] = np.random.uniform(low,high)
    img=img+uni
    return img

def gaussion_noise(img):
    row,col=img.shape
    mean=0
    var=0.1
    sigma=var**0.5
    gaussion_noise = np.random.normal(loc=mean, scale=sigma, size=(row,col))
    img=img+gaussion_noise
    return img

def median_filter(noise_image):
    row,col=noise_image.shape
    filtered_image=np.zeros([row,col])
    #loop on every window 3*3 in the image
    for i in range (1,row-1):
        for j in range (1,col-1):
            image=[noise_image[i-1, j-1],
                   noise_image[i-1, j],
                   noise_image[i-1, j + 1],
                   noise_image[i, j-1],
                   noise_image[i, j],
                   noise_image[i, j + 1],
                   noise_image[i + 1, j-1],
                   noise_image[i + 1, j],
                   noise_image[i + 1, j + 1]]
            image=sorted(image)
            filtered_image[i, j]=image[4]
    filtered_image = filtered_image.astype(np.uint8)
    return filtered_image

# ------------------ LOW PASS FILTER -------------------------------------

def GaussianLowFilter(img):
    
    # transform the image into frequency domain, f --> F
    F = np.fft.fft2(img)
    Fshift = np.fft.fftshift(F)
    
    # Create Gaussin Filter: Low Pass Filter
    M,N = img.shape
    H = np.zeros((M,N), dtype=np.float32)
    D0 = 10
    for u in range(M):
        for v in range(N):
            D = np.sqrt((u-M/2)**2 + (v-N/2)**2)
            H[u,v] = np.exp(-D**2/(2*D0*D0))
            
    # Image Filters
    Gshift = Fshift * H
    G = np.fft.ifftshift(Gshift)
    g = np.abs(np.fft.ifft2(G))
    return g

def idealLowPass(img):
        # image in frequency domain
    F = np.fft.fft2(img)
    Fshift = np.fft.fftshift(F)

    # Filter: Low pass filter
    M,N = img.shape
    H = np.zeros((M,N), dtype=np.float32)
    D0 = 50
    for u in range(M):
        for v in range(N):
            D = np.sqrt((u-M/2)**2 + (v-N/2)**2)
            if D <= D0:
                H[u,v] = 1
            else:
                H[u,v] = 0

    # Ideal Low Pass Filtering
    Gshift = Fshift * H

    # Inverse Fourier Transform
    G = np.fft.ifftshift(Gshift)
    g = np.abs(np.fft.ifft2(G))
    return g

def meanLowPass(img):
    # Obtain number of rows and columns 
    # of the image
    m, n = img.shape

    # Develop Averaging filter(3, 3) mask
    mask = np.ones([3, 3], dtype = int)
    mask = mask / 9

    # Convolve the 3X3 mask over the image 
    img_new = np.zeros([m, n])

    for i in range(1, m-1):
        for j in range(1, n-1):
            temp = img[i-1, j-1]*mask[0, 0]+img[i-1, j]*mask[0, 1]+img[i-1, j + 1]*mask[0, 2]+img[i, j-1]*mask[1, 0]+ img[i, j]*mask[1, 1]+img[i, j + 1]*mask[1, 2]+img[i + 1, j-1]*mask[2, 0]+img[i + 1, j]*mask[2, 1]+img[i + 1, j + 1]*mask[2, 2]

            img_new[i, j]= temp

    img_new = img_new.astype(np.uint8)
    return img_new


# ------------------ HIGH PASS FILTER -------------------------------------

def IdealHighPass(img):
    # image in frequency domain
    F = np.fft.fft2(img)
    Fshift = np.fft.fftshift(F)

    # Filter: Low pass filter
    M,N = img.shape
    H = np.zeros((M,N), dtype=np.float32)
    D0 = 50
    for u in range(M):
        for v in range(N):
            D = np.sqrt((u-M/2)**2 + (v-N/2)**2)
            if D <= D0:
                H[u,v] = 1
            else:
                H[u,v] = 0             
    # Filter: High pass filter
    H = 1 - H
    # Ideal High Pass Filtering
    Gshift = Fshift * H
    # Inverse Fourier Transform
    G = np.fft.ifftshift(Gshift)
    g = np.abs(np.fft.ifft2(G))
    return g

def sobel(img):
    # sobel kernel
    sobel_x = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]])

    sobel_y = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]])
    # partial derivative in x-direction
    edge_x = cv2.filter2D(src=img, ddepth=-1, kernel=sobel_x)
    edge_x[edge_x != 0] = 255


    # partial derivative in y-direction
    edge_y = cv2.filter2D(src=img, ddepth=-1, kernel=sobel_y)
    edge_y[edge_y != 0] = 255


    # combinte the x and y edge
    add_edge = edge_x + edge_y
    add_edge[add_edge != 0] = 255
    return add_edge

def robert(img):
    roberts_cross_v = np.array( [[ 0, 0, 0 ],
                             [ 0, 1, 0 ],
                             [ 0, 0,-1 ]] )

    roberts_cross_h = np.array( [[ 0, 0, 0 ],
                             [ 0, 0, 1 ],
                             [ 0,-1, 0 ]] )
    vertical = ndimage.convolve( img, roberts_cross_v )
    horizontal = ndimage.convolve( img, roberts_cross_h )
    edged_img = np.sqrt( np.square(horizontal) + np.square(vertical))
    return edged_img

def prewit(img):
    #define horizontal and Vertical sobel kernels
    Hx = np.array([[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]])
    Hy = np.array([[-1, -1, -1],[0, 0, 0],[1, 1, 1]])
    #normalizing the vectors
    pre_x = convolve(img, Hx) / 6.0
    pre_y = convolve(img, Hy) / 6.0
    #calculate the gradient magnitude of vectors
    pre_out = np.sqrt(np.power(pre_x, 2) + np.power(pre_y, 2))
    # mapping values from 0 to 255
    pre_out = (pre_out / np.max(pre_out)) * 255
    return pre_out

# ------------------ APPLYING FILTER -------------------------------------

def convolve(X, F):
    # height and width of the image
    X_height = X.shape[0]
    X_width = X.shape[1]
    
    # height and width of the filter
    F_height = F.shape[0]
    F_width = F.shape[1]
    
    H = (F_height - 1) // 2
    W = (F_width - 1) // 2
    
    #output numpy matrix with height and width
    out = np.zeros((X_height, X_width))
    #iterate over all the pixel of image X
    for i in np.arange(H, X_height-H):
        for j in np.arange(W, X_width-W):
            sum = 0
            #iterate over the filter
            for k in np.arange(-H, H+1):
                for l in np.arange(-W, W+1):
                    #get the corresponding value from image and filter
                    a = X[i+k, j+l]
                    w = F[H+k, W+l]
                    sum += (w * a)
            out[i,j] = sum
    #return convolution  
    return out


# ------------------ PLOTTING -------------------------------------

def histogram(img):
    # convert our image into a numpy array
    img = np.asarray(img)

    # put pixels in a 1D array by flattening out img array
    flat = img.flatten()

    # show the histogram
    plt.hist(flat, bins=50)


def cumm_dist(img):
    plt.hist(img.ravel(), bins = 256, cumulative = True)
    plt.xlabel('Intensity Value')
    plt.ylabel('Count') 
    plt.show()



    # create our own histogram function
def get_histogram(image, bins):
    # array with size of bins, set to zeros
    histogram = np.zeros(bins)
    
    # loop through pixels and sum up counts of pixels
    for pixel in image:
        histogram[pixel] += 1
    
    # return our final result
    return histogram

# create our cumulative sum function
def cumsum(a):
    a = iter(a)
    b = [next(a)]
    for i in a:
        b.append(b[-1] + i)
    return np.array(b)



# ------------------ EQUALIZATION AND NORMALIZATION -------------------------------------

def equalization(path):
    img = Image.open(path)

    # convert image into a numpy array
    img = np.asarray(img)
    # put pixels in a 1D array by flattening out img array
    flat = img.flatten()
    # re-normalize cumsum values to be between 0-255
    hist = get_histogram(flat, 256)
    cs = cumsum(hist)
    # numerator & denomenator
    nj = (cs - cs.min()) * 255
    N = cs.max() - cs.min()



    # re-normalize the cdf
    cs = nj / N
    # cast it back to uint8 since we can't use floating point values in images
    cs = cs.astype('uint8')
    # get the value from cumulative sum for every index in flat, and set that as img_new
    img_new = cs[flat]
    # put array back into original shape since we flattened it
    img_new = np.reshape(img_new, img.shape)
    # set up side-by-side image display
    fig = plt.figure()
    fig.set_figheight(15)
    fig.set_figwidth(15)

    fig.add_subplot(1,2,1)
    plt.imshow(img, cmap='gray')

    # display the new image
    fig.add_subplot(1,2,2)
    plt.imshow(img_new, cmap='gray')

    plt.show(block=True)    

    
def normalize(path):
    img = cv2.imread(path)
    norm_img = np.zeros((800,800))
    final_img = cv2.normalize(img,  norm_img, 0, 255, cv2.NORM_MINMAX)
    cv2.imshow('Normalized Image', final_img)
    cv2.imwrite('city_normalized.jpg', final_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
# ------------------ THRESHOLDING -------------------------------------

def globalThresholding(img, n):
    img_shape = img.shape
    height = img_shape[0]
    width = img_shape[1]
    for row in range(width):
        for column in range(height):
            if img[column, row] > n:
                img[column, row] = 0
            else:
                img[column, row] = 255
    return img   


def localThresholding(img, radius):
    image = np.zeros_like(img)
    max_row, max_col = img.shape
    for i, row in enumerate(img):
        y_min = max(0, i - radius)
        y_max = min(max_row, i + radius + 1)
        for j, elem in enumerate(row):
            x_min = max(0, j - radius)
            x_max = min(max_col, j + radius + 1)
            window = img[y_min:y_max, x_min:x_max]
            if img[i, j] >= np.median(window):
                image[i, j] = 255
    return image


