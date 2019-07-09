from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import base64
import numpy as np
import itertools
import cv2
import os
import sys
import time
import io
client = vision.ImageAnnotatorClient()
print(cv2.__version__)


dir = "/Users/gabe/Desktop/autoanonymization/"

def video_to_frames(input_video_file):
    vidcap = cv2.VideoCapture(input_video_file)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    _,image = vidcap.read()
    count = 0
    success = True
    sz = (len(image[0]),len(image))
    im = Image.new("RGBA", sz)
    im.format = "PNG"
    hi_im_list = []
    while success:
        loc = dir + "frames/frame_"+str(count)+".png"

        st = time.time()

        image = flatlist_to_tuplelist(image)

        im.putdata(image)
        h = blur_faces(im)
        hi_im_list.append(h)

        success,image = vidcap.read()
        print(count,"total time",time.time()-st)
        count += 1
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, fps, sz)
    for hi_im in hi_im_list:
        #TODO: make a function that converts im to numpy array
        arr = im_to_numpy_array(hi_im)
        out.write(arr)
    out.release()
    cv2.destroyAllWindows()


def im_to_numpy_array(im):
    lst = []
    pix_val = list(im.getdata())
    width, height = im.size
    for w in range(0,len(pix_val),width):
        sublist = pix_val[w:w+width]
        #print("~~~~~~~~~~~~~~~~~~~")
        #print(sublist)
        lst.append(sublist)
    numpy_array = np.array(lst)
    return numpy_array


def flatlist_to_tuplelist(image):

    flatlist = image.flatten().tolist()
    n = len(flatlist)
    res = []

    st = time.time()
    for i in range(0,n,3):
        res.append(tuple((flatlist[i+2],flatlist[i+1],flatlist[i],255)))
    #print("---convert image to tuple list:",(time.time()-st))

    return res

def image_to_byte_array(image):
    imgByteArr = io.BytesIO()

    st = time.time()
    image.save(imgByteArr, format=image.format)
    #print("---image_to_byte_array:",time.time()-st)

    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def detect_face(im, max_results=100):
    """
    Uses the Vision API to detect faces in the given file.

    Args:
        im: A file-like object containing an image with faces.
        max_results:
    Returns:
        An array of Face objects with information about the picture.
    """
    client = vision.ImageAnnotatorClient()
    im.format = "PNG"
    content = image_to_byte_array(im)
    image = types.Image(content=content)

    st = time.time()
    res = client.face_detection(image=image, max_results=max_results).face_annotations
    #print("---client:",time.time()-st)

    return res

def highlight_faces(im, output_filename=None):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      output_filename: the name of the image file to be created, where the
          faces have polygons drawn around them.
    """
    draw = ImageDraw.Draw(im)
    faces = detect_face(im)

    for face in faces:
        box = [(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices]
        draw.line(box + [box[0]], width=5, fill='#00ff00')
        draw.text(((face.bounding_poly.vertices)[0].x,
                   (face.bounding_poly.vertices)[0].y - 30),
                  str(format(face.detection_confidence, '.3f')) + '%',
                  fill='#FF0000')
    if output_filename!=None:
        st = time.time()
        im.save(output_filename)
        #print("---saving photo:",time.time()-st)
        return None
    else:
        return im

def blur_faces(im, output_filename=None,filter_width=16):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
      output_filename: the name of the image file to be created, where the
          faces have polygons drawn around them.
    """
    pix_val = list(im.getdata())
    width, height = im.size
    res = []
    for w in range(0,len(pix_val),width):
        sublist = pix_val[w:w+width]
        res.append(sublist)
    pix_val = res
    # Sepecify the font-family and the font-size
    faces = detect_face(im)
    st = time.time()
    for face in faces:
        #corners
        box = [(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices]
        x_left = box[0][0]
        x_right = box[1][0]
        y_top = box[0][1]
        y_bottom = box[2][1]

        blur_region(pix_val,x_left,x_right,y_top,y_bottom,filter_width)

    #print(pix_val)
    pxl = list(itertools.chain.from_iterable(pix_val))
    im2 = Image.new(im.mode, im.size)
    im2.putdata(pxl)
    if output_filename==None:
        im2.save(output_filename)
        #print(time.time()-st)
    return im2

def blur_region(pix_val,x_left,x_right,y_top,y_bottom,filter_width):

    for h in range(y_top,y_bottom+1,filter_width):
        for w in range(x_left,x_right+1,filter_width):

            r_sum = 0
            g_sum = 0
            b_sum = 0
            n = 0
            for x in range(0,filter_width):
                if h+x<len(pix_val):
                    row = pix_val[h+x]
                    for y in range(0,filter_width):
                        pixel = row[w+y]
                        if w+y<len(pix_val[0]):
                            r_sum = r_sum + pixel[0]
                            g_sum = g_sum + pixel[1]
                            b_sum = b_sum + pixel[2]
                            n = n + 1
            val = (int(r_sum/n),int(g_sum/n),int(b_sum/n),255)
            for x in range(0,filter_width):
                if h+x<len(pix_val):
                    for y in range(0,filter_width):
                        if w+y<len(pix_val[0]):
                            pix_val[h+x][w+y] = val
    return pix_val



input_file = dir + "class_photo_2.jpg"

output_file = dir + "out_3.png"

movie = dir + "movie.mp4"

if os.path.exists(output_file):
    os.remove(output_file)

im = Image.open(input_file)



#blur_faces(im,output_file)

video_to_frames(movie)
