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
        h = highlight_faces(im,loc)
        #hi_im_list.append(h)

        success,image = vidcap.read()
        count += 1

        print(count,"total time",time.time()-st)
    # Define the codec and create VideoWriter object
    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #out = cv2.VideoWriter('output.avi',fourcc, 20.0, sz)
    #for hi_im in hi_im_list:
        #TODO: make a function that converts im to numpy array
        #out.write(hi_im)
    #out.release()
    #cv2.destroyAllWindows()


def im_to_numpy_array(im):
    lst = []
    numpy_array = np.array(lst)
    return numpy_array


def flatlist_to_tuplelist(image):

    flatlist = image.flatten().tolist()
    n = len(flatlist)
    res = []

    st = time.time()
    for i in range(0,n,3):
        res.append(tuple((flatlist[i+2],flatlist[i+1],flatlist[i],255)))
    print("---convert image to tuple list:",(time.time()-st))

    return res

def image_to_byte_array(image):
    imgByteArr = io.BytesIO()

    st = time.time()
    image.save(imgByteArr, format=image.format)
    print("---image_to_byte_array:",time.time()-st)

    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def detect_face(im, max_results=4):
    """
    Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of Face objects with information about the picture.
    """
    client = vision.ImageAnnotatorClient()
    im.format = "PNG"
    content = image_to_byte_array(im)
    image = types.Image(content=content)

    st = time.time()
    res = client.face_detection(image=image, max_results=max_results).face_annotations
    print("---client:",time.time()-st)

    return res

def highlight_faces(im, output_filename=None):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
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
        print("---saving photo:",time.time()-st)
        return None
    else:
        return im

def blur_faces(im, output_filename,filter_width=16):
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
    for face in detect_face(im):
        box = [(vertex.x, vertex.y)
               for vertex in face.bounding_poly.vertices]
        x_left = box[0][0]
        x_right = box[1][0]
        y_top = box[0][1]
        y_bottom = box[2][1]
        res = []
        for h in range(y_top,y_bottom+1):
            row = []
            for w in range(x_left,x_right+1):
                row.append(pix_val[h][w])
            res.append(row)
        res = blur_region(res,filter_width)
        for h in range(0,y_bottom+1-y_top):
            for w in range(0,x_right+1-x_left):
                pix_val[h+y_top][w+x_left] = res[h][w]
    pxl = list(itertools.chain.from_iterable(pix_val))
    im2 = Image.new(im.mode, im.size)
    im2.putdata(pxl)
    im2.save(output_filename)

def blur_region(pixel_list,filter_width):

    def average_rgb(pixel_list):
        n = len(pixel_list)
        r_sum = 0
        g_sum = 0
        b_sum = 0
        for px in pixel_list:
            r_sum = r_sum + px[0]
            g_sum = g_sum + px[1]
            b_sum = b_sum + px[2]
        r = int(r_sum/n)
        g = int(g_sum/n)
        b = int(b_sum/n)
        return (r,g,b,255)

    for i in range(0,len(pixel_list),filter_width):
        for j in range(0,len(pixel_list[0]),filter_width):
            l = []
            r_sum = 0
            g_sum = 0
            b_sum = 0
            for x in range(0,filter_width):
                if i+x<len(pixel_list):
                    for y in range(0,filter_width):
                        if j+y<len(pixel_list[0]):
                            r_sum = r_sum + pixel_list[i+x][j+y][0]
                            g_sum = g_sum + pixel_list[i+x][j+y][1]
                            b_sum = b_sum + pixel_list[i+x][j+y][2]
            val = average_rgb(l)
            for x in range(0,filter_width):
                if i+x<len(pixel_list):
                    for y in range(0,filter_width):
                        if j+y<len(pixel_list[0]):
                            pixel_list[i+x][j+y] = val
    return pixel_list



input_file = dir + "fake_ai_faces.0.png"

output_file = dir + "out_3.png"

movie = dir + "movie.mp4"

im = Image.open(input_file)

#highlight_faces(im,output_file)

video_to_frames(movie)
