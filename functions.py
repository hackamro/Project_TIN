import numpy as np
import os
import io
# ****************************************************************************
def Convert_fig_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

# ----------------------------------------------------------------------
def Convert_3d_2d_Array(imgArray):
    if len(imgArray.shape) == 2:
        # print("------------------------------------------------- Array 2d")
        n_line = imgArray.shape[0]
        n_cols = imgArray.shape[1]
        return imgArray
    
    elif len(imgArray.shape) == 3:
        # print("------------------------------------------------- Array 3d")
        n_line = imgArray.shape[0]
        n_cols = imgArray.shape[1]
        matrix2D = np.zeros((n_line,n_cols), np.uint64)
        for i in range(0,n_line):
            for j in range(0,n_cols):
                val= int((imgArray[i,j,0]+imgArray[i,j,1]+imgArray[i,j,2])/3)
                matrix2D[i,j]= val   
        return matrix2D
    else:
        print("len(imgArray.shape):",len(imgArray.shape))
# ----------------------------------------------------------------------
def ReadImage2d_Array(_path):
    image = Image.open(_path)
    imgArray = np.array(image)  
    return Convert_3d_2d_Array(imgArray)
# ----------------------------------------------------------------------
from PIL import Image
def Convert_Array2Image(_imgArray):
    return Image.fromarray(_imgArray.astype(np.uint8))
# ---------------------------------------------------------------------- Contrast
def ContrastLinear_Array(imgArray,_b,_a):
    imgArray =  imgArray.copy()
    for i in range(0,imgArray.shape[0]):
        for j in range(0,imgArray.shape[1]):
            imgArray[i][j]= int(imgArray[i][j]*_b+_a)
            if imgArray[i][j] > 255:
                imgArray[i][j] = 255
            elif imgArray[i][j] <0:
                imgArray[i][j] = 0
    return imgArray

# ---------------------------------------------------------------------- Contrast
def ContrastInvers_255_Array(imgArray):
    return 255- imgArray

# ---------------------------------------------------------------------- Contrast
def ContrastInvers_BiC_Array(imgArray):
    return 1- imgArray

# ---------------------------------------------------------------------- Contrast
def ContrastLog_Array(imgArray):
    return np.abs(np.log(imgArray+1.1)*255 /
               np.log(np.max(imgArray+1.1)))

# ---------------------------------------------------------------------- Contrast
def ContrastRange_Array(imgArray,_min,_max): 
    imgArray =  imgArray.copy()
    for i in range(0,imgArray.shape[0]):
        for j in range(0,imgArray.shape[1]):
            imgArray[i][j]= int(255/(_max-_min) * (imgArray[i][j] - _min ))
            if imgArray[i][j] > 255:
                imgArray[i][j] = 255
            elif imgArray[i][j] <0:
                imgArray[i][j] = 0
    return imgArray

# ----------------------------------------------------------------------  Egalisation d’histogramme
def Histogram_Array(imgArray):
    from matplotlib.figure import Figure
    y = np.zeros(256, np.uint32)
    for i in range(0,imgArray.shape[0]):
        for j in range(0,imgArray.shape[1]):
            y[imgArray[i,j]] += 1
    
    fig = Figure()
    ax = fig.subplots()
    ax.set_xlabel("value of pixel")
    ax.set_ylabel("nomber repitition")   
    ax.set_title('histogram')
    ax.plot(range(0,256),y,'black');

    img = Convert_fig_img(fig)
    return img;

# ---------------------------------------------------------------------- Lissage des images
def Filter_Array(_arrayIn,_filter3x3):
    arrayOut = np.zeros(_arrayIn.shape,np.uint8) 
    for ligne in range(1,_arrayIn.shape[0]-1):
        for col in range(1,_arrayIn.shape[1]-1):
            # On calcule la somme 
            somme = 0
            for l in range(3):
                for c in range(3):
                    somme += _filter3x3[l,c]*_arrayIn[ligne-1+l,col-1+c]
            arrayOut[ligne,col] = somme
    return arrayOut

# ---------------------------------------------------------------------- Opérations morphologiques
def Convert_BiColor_Array(imgArray,_thresholding):
    return np.where(imgArray > _thresholding, 1, 0)
# ---------------------------------------------------------------------- Opérations morphologiques
def Erosion_Array(image, kernel):
    img_operated = image.copy() #this will be the image
    vertical_window = image.shape[0] - kernel.shape[0] #final vertical window position
    horizontal_window = image.shape[1] - kernel.shape[1] #final horizontal window position
    vertical_pos = 0
    while vertical_pos <= vertical_window:
        horizontal_pos = 0
        while horizontal_pos <= horizontal_window:
            erosion_flag = False
            for i in range(kernel.shape[0]):      # <<< MODIFIED
                for j in range(kernel.shape[1]):  # <<< MODIFIED
                    if kernel[i][j] == 1:         # <<< ADDED
                        if image[vertical_pos+i][horizontal_pos+j] == 0:  # <<< MODIFIED
                            erosion_flag = True                            # <<< MODIFIED
                            break
                if erosion_flag:         # <<< MODIFIED
                    img_operated[vertical_pos, horizontal_pos] = 0  # <<< ADDED
                    break

            horizontal_pos += 1
        vertical_pos += 1
    return img_operated

# ---------------------------------------------------------------------- Opérations morphologiques
def Dilation_Array(image, kernel):
    img_operated = image.copy() #this will be the image  # <<< ADDED
    vertical_window = image.shape[0] - kernel.shape[0] #final vertical window position
    horizontal_window = image.shape[1] - kernel.shape[1] #final horizontal window position
    vertical_pos = 0
    while vertical_pos <= vertical_window:
        horizontal_pos = 0
        while horizontal_pos <= horizontal_window:
            dilation_flag = False
            for i in range(kernel.shape[0]):      # <<< MODIFIED
                for j in range(kernel.shape[1]):  # <<< MODIFIED
                    if kernel[i][j] == 1:  
                        if image[vertical_pos+i][horizontal_pos+j] == 1:  # <<< MODIFIED
                            dilation_flag = True
                            break
                if dilation_flag:       # <<< FIXED
                    img_operated[vertical_pos, horizontal_pos] = 1
                    break
            horizontal_pos += 1
        vertical_pos += 1
    return img_operated
# ---------------------------------------------------------------------- Segmentation
def pupil(_imgArray,_seullage = 50, valeuFind = 0):
    n_columns =_imgArray.shape[1]
    n_rows =_imgArray.shape[0]
    
    imgBiC = np.where(_imgArray > _seullage, 1, 0)
        
    sumX = 0
    sumY = 0
    sumN = 0
    for y in range(0,n_rows):
        for x in range(0,n_columns):
            if imgBiC[y][x] == valeuFind:
                sumX = sumX + x
                sumY = sumY + y
                sumN = sumN + 1
    
    X = int(sumX/sumN)
    Y = int(sumY/sumN)
    R = int(np.sqrt(sumN/np.pi) ) #Area of a disk =  πr^2
    return X,Y,R
# ---------------------------------------------------------------------- Segmentation
def iris(_imgArray,_seullage = 50, valeuFind = 0):
    x,y,r =pupil(_imgArray,_seullage,valeuFind)
    return x,y,r*2.5
# ---------------------------------------------------------------------- Segmentation
def zeroExternalArray(_array,_x,_y,_r): #  معادلة قرص
    _array = _array.copy()
    for i in range(0,_array.shape[0]):
        for j in range(0,_array.shape[1]):
            if( (j-_x)**2 + (i-_y)**2 ) >= _r**2:
                _array[i][j]=0
    return _array
# ---------------------------------------------------------------------- Segmentation             
def zeroInternalArray(_array,_x,_y,_r): #  معادلة قرص
    _array = _array.copy()    
    for i in range(0,_array.shape[0]):
        for j in range(0,_array.shape[1]):
            if( (j-_x)**2 + (i-_y)**2 ) <= _r**2:
                _array[i][j]=0
    return _array
              
def Segmentation(_imgArray):
    pupil_x,pupil_y,pupil_r = pupil(_imgArray)
    iris_x,iris_y,iris_r = iris(_imgArray)
    
    _imgArray = zeroExternalArray(_imgArray,iris_x,iris_y,iris_r)
    _imgArray = zeroInternalArray(_imgArray,pupil_x, pupil_y, pupil_r)
 
    return _imgArray,(pupil_x,pupil_y,pupil_r),(iris_x,iris_y,iris_r)
 
# ********************************************************************** Need opencv
# ---------------------------------------------------------------------- Détecteur SIFT
import cv2 as cv2
def Get_Keypoints_Des_Array(_imgArray):
    # Initiate SIFT detector
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp, des = sift.detectAndCompute(_imgArray,None)
    # # draw keypoint
    # imgOut = cv2.drawKeypoints(img,kp,None,color=(0,255,0), flags=0)
    return kp,des,_imgArray

# ---------------------------------------------------------------------- DescripteurDistance  SIFT
def GetMatching(des1,des2):
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    goodMatchs = []
    for m,n in matches:
        if m.distance < 0.8*n.distance:
            goodMatchs.append(m)
    return goodMatchs

# ---------------------------------------------------------------------- all in one
def GetMatchingImageValue_Array(_imgArray1,_imgArray2):
    kp1, des1 , img1 = Get_Keypoints_Des_Array(_imgArray1)
    kp2, des2 , img2 = Get_Keypoints_Des_Array(_imgArray2)
    good = GetMatching(des1,des2)

    # print ("matches found : %d" % (len(good)))
    imgOut = cv2.drawMatches(img1,kp1,img2,kp2,good,None ,**dict(matchColor = (0,255,0),flags = 0))
    return imgOut , len(good)

_listSIFT = []
def databaseCreate(_list):
    global _listSIFT
    sift = cv2.xfeatures2d.SIFT_create()
    for f in _list:
        try:
            numberP = os.path.basename(f)[0:3]
            imgArray = ReadImage2d_Array(f)
            kp, des = sift.detectAndCompute(imgArray,None)
            _listSIFT.append([numberP,f,des])
        except:
            print("Error read file:",f)
    return len(_listSIFT)
          
def Recognition(_path):
    try:
        global _listSIFT
        print(_path)
        # listO = load_object()
        imgArray = ReadImage2d_Array(_path)
        
        imgArray ,pupil,iris = Segmentation(imgArray)
        
        kp1, des1 , img1 = Get_Keypoints_Des_Array(imgArray)
        
        maxMatching =0
        index = 0
        pos = 0
        for v in _listSIFT:
            good = GetMatching(des1,v[2])
            if len(good) >= maxMatching:
                pos = index
                maxMatching = len(good)
                num = os.path.basename(v[0])
                print("name:",num,"SIFT:",maxMatching)
            index = index+1      
        
        print("name:",_listSIFT[pos][0],"SIFT Matching max:",maxMatching,"path:",_listSIFT[pos][1])
        
        path2 = _listSIFT[pos][1]
        imgArray2 = ReadImage2d_Array(path2)
        kp2, des2 , img2 = Get_Keypoints_Des_Array(imgArray2)
        good = GetMatching(des1,des2)
        imgArrayOut = cv2.drawMatches(img1,kp1,img2,kp2,good,None ,**dict(matchColor = (0,255,0),flags = 0))
        
        imgOut = Convert_Array2Image(imgArrayOut)
        return imgOut,maxMatching,path2
        
    except:
        print("Error Recon:")
# ****************************************************************************