# Copyright 2018-present, DrifterFun.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import tqdm
import cv2
import numpy as np
import os
import queue
import time
import argparse
import random

from House3D import objrender, Environment, load_config, House
from House3D.objrender import RenderMode
from threading import Thread, Lock

def gentd():    #在大图中截取TopDown
    #x, y = env.cam.pos.x, env.cam.pos.z
    x, y = env.house.to_grid(env.cam.pos.x,env.cam.pos.z)
    x_max, y_max = env.house.to_grid(env.cam.pos.x+3.0, env.cam.pos.z+3.0)
    det = abs(x_max-x)
    x_min, y_min = env.house.to_grid(env.cam.pos.x-3.0, env.cam.pos.z-3.0)
    #print(x,y,x_min,y_min,x_max,y_max)
    obsMap_pad = np.pad(np.array(env.house.obsMap),((det, det),(det, det)),'constant',constant_values = (1,1))        #扩充obsMap
    locMap_tmp = obsMap_pad[x:x+2*det, y:y+2*det]
    return locMap_tmp



    """
    Produces and array that consists of the coordinates and intensities of each pixel in a line between two points

    Parameters:
        -P1: a numpy array that consists of the coordinate of the first point (x,y)
        -P2: a numpy array that consists of the coordinate of the second point (x,y)
        -img: the image being processed

    Returns:
        -it: a numpy array that consists of the coordinates and intensities of each pixel in the radii (shape: [numPixels, 3], row = [x,y,intensity])     
    """
def createLineIterator(P1, P2, img): 
   imageH = img.shape[0]#define local variables for readability
   imageW = img.shape[1]
   P1X = P1[0]
   P1Y = P1[1]
   P2X = P2[0]
   P2Y = P2[1]

   #difference and absolute difference between points
   #used to calculate slope and relative location between points
   dX = P2X - P1X
   dY = P2Y - P1Y
   dXa = np.abs(dX)
   dYa = np.abs(dY)

   #predefine numpy array for output based on distance between points
   itbuffer = np.empty(shape=(np.maximum(dYa,dXa),3),dtype=np.float32)
   itbuffer.fill(np.nan)

   #Obtain coordinates along the line using a form of Bresenham's algorithm
   negY = P1Y > P2Y
   negX = P1X > P2X
   if P1X == P2X: #vertical line segment
       itbuffer[:,0] = P1X
       if negY:
           itbuffer[:,1] = np.arange(P1Y - 1,P1Y - dYa - 1,-1)
       else:
           itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)              
   elif P1Y == P2Y: #horizontal line segment
       itbuffer[:,1] = P1Y
       if negX:
           itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
       else:
           itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
   else: #diagonal line segment
       steepSlope = dYa > dXa
       if steepSlope:
           slope = dX.astype(np.float32)/dY.astype(np.float32)
           if negY:
               itbuffer[:,1] = np.arange(P1Y-1,P1Y-dYa-1,-1)
           else:
               itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)
           itbuffer[:,0] = (slope*(itbuffer[:,1]-P1Y)).astype(np.int) + P1X
       else:
           slope = dY.astype(np.float32)/dX.astype(np.float32)
           if negX:
               itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
           else:
               itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
           itbuffer[:,1] = (slope*(itbuffer[:,0]-P1X)).astype(np.int) + P1Y

   #Remove points outside of image
   colX = itbuffer[:,0]
   colY = itbuffer[:,1]
   itbuffer = itbuffer[(colX >= 0) & (colY >=0) & (colX<imageW) & (colY<imageH)]

   #Get intensities from img ndarray
   itbuffer[:,2] = img[itbuffer[:,0].astype(np.uint),itbuffer[:,1].astype(np.uint)]

   return itbuffer



def td_process(loctd):       #将截取到的Top-Down做成真正能够用的TopDown
    loctd1 = loctd
    width, high = loctd1.shape
    
    cen_tmp = [int(width/2), int(high/2)]      #选取没有被占据的中心点
    cen_list = [cen_tmp,[cen_tmp[0]-1,cen_tmp[1]],[cen_tmp[0],cen_tmp[1]-1],[cen_tmp[0],cen_tmp[1]+1],[cen_tmp[0]+1,cen_tmp[1]]]
    cen_list_value = [loctd1[cen_list[0][0],cen_list[0][1]],loctd1[cen_list[1][0],cen_list[1][1]],loctd1[cen_list[2][0],cen_list[2][1]],loctd1[cen_list[3][0],cen_list[3][1]],loctd1[cen_list[4][0],cen_list[4][1]]]
    position = cen_list_value.index(0)
    cen = cen_list[position]


    for i in range(width):
        for j in range(high):
            if ([i,j] not in [cen,[cen[0]-1,cen[1]-1],[cen[0]-1,cen[1]],[cen[0]-1,cen[1]+1],[cen[0],cen[1]-1],[cen[0],cen[1]+1],[cen[0]+1,cen[1]-1],[cen[0]+1,cen[1]],[cen[0]+1,cen[1]+1]]):
                if (loctd1[i][j] == 1.0):
                    pass
                else:
                    line = createLineIterator(np.array(cen), np.array([i,j]), loctd)
                    if (np.max(line[:,2]) == 1.0):
                        loctd1[i][j] = 1.0
    return loctd1


if __name__ == '__main__':
    api = objrender.RenderAPI(w=600, h=450, device=0)   #随机地从obsMap中采样
    cfg = load_config('config.json')

    env = Environment(api, '00065ecbdd7300d35ef4328ffe871505', cfg)

    con = []
    loc = []

    for i in range(env.house.obsMap.shape[0]):
        for j in range(env.house.obsMap.shape[1]):
            if env.house.obsMap[i][j] == 0:
                con.append([i,j])

    for i in range(30):
        gx, gy = random.choice(con)
        x, y = env.house.to_coor(gx, gy, True)
        loc.append([x,y])



    for i in range(len(loc)):
        env.cam.pos.x = loc[i][0]
        env.cam.pos.y = env.house.robotHei
        env.cam.pos.z = loc[i][1]

        map_use = gentd()
        map_real_use = td_process(gentd())

        cv2.imshow("bbb", -(map_use-1)*255)
        cv2.imshow("ccc", -(map_real_use-1)*255)
        cv2.waitKey(0)