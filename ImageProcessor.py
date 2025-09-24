import numpy as np
from cv2 import cvtColor, COLOR_BGR2GRAY, Laplacian, CV_64F, imencode,IMWRITE_JPEG_QUALITY
from threading import Thread
import time
from BRISQUE import BRISQUE

brisque = BRISQUE()

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)

        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return

class ImageProcessor:
    def __init__(self):
        pass
    def divideImage(self,img):
        divisions=[]
        row=img.shape[0]
        col=img.shape[1]
        r_inc=int(row/4)
        curr_r=0
        while(curr_r<=(row-r_inc)):
            curr_c=0
            c_inc=int(col/4)
            while(curr_c<=(col-c_inc)):
                divisions.append([curr_r,(curr_r+r_inc),curr_c,(curr_c+c_inc)])
                if(curr_c+c_inc>col):
                    c_inc=col-curr_c
                curr_c+=c_inc
            if(curr_r+r_inc>row):
                r_inc=row-curr_r
            curr_r+=r_inc
        return divisions
    
    #This function returns blurrness of the image using Laplacian Filter
    def getBlurrinessScore(self,image):
        image = cvtColor((image), COLOR_BGR2GRAY)
        fm = Laplacian(image, CV_64F).var()
        return fm

    def getBlurrinessMatrix(self,img,divisions):
        blurriness_mat=[]
        for division in divisions:
            segment=img[division[0]:division[1],division[2]:division[3]]
            blurriness=self.getBlurrinessScore(segment)
            blurriness_mat.append([blurriness,division[0],division[1],division[2],division[3]])
        blurriness_mat=np.array(blurriness_mat)
        blurriness_mat=blurriness_mat[blurriness_mat[:,0].argsort()]
        shape=blurriness_mat.shape
        s=shape[0]
        i=0
        while(i<s):
            if(i>=3 and i<s-3):
                blurriness_mat=np.delete(blurriness_mat,i,0)
                s-=1
                i-=1
            i+=1
        return blurriness_mat

    def getQuality(self,blurriness_mat,img):
        quality_score=[]
        threads=[]
        for i in blurriness_mat:
            img_segment=img[int(i[1]):int(i[2]),int(i[3]):int(i[4])]
            p=ThreadWithReturnValue(target=brisque.getScore,kwargs={'img':img_segment})
            threads.append(p)
        for thread in threads:
            thread.start()
        for thread in threads:
            quality_score.append(thread.join())
        quality_score=np.array(quality_score)
        return np.mean(quality_score)
    def reduceSize(self, image):
        divisions = self.divideImage(image.copy())
        blurriness_mat=self.getBlurrinessMatrix(image,divisions)
        mean_quality=self.getQuality(blurriness_mat,image)
        success, encoded_image = imencode('.jpeg', image, [IMWRITE_JPEG_QUALITY, int(mean_quality)])
        if success:
            return encoded_image
        raise Exception("Failed to encode image")