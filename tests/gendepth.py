# Copyright 2017-present, DrifterFun.
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


def gendp():
    img = env.render(RenderMode.INVDEPTH)
    img_16 = img.astype(np.uint16)
    inverse_depth_16 = img_16[:, :, 0] * 256 + img_16[:, :, 1]
    PIXEL_MAX = np.iinfo(np.uint16).max 
    NEAR = 0.3 # has to match minDepth parameter
    depth_float = NEAR * PIXEL_MAX / inverse_depth_16.astype(np.float)
    #depth_float_3 = depth_float[depth_float > 3.0] = 3.0
    depth_float_3 = np.minimum(depth_float, 3.0, depth_float)
    #depth_float_3 = int()
    return depth_float_3  #返回的是小于3m的浮点值
    




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

    for i in range(100):
        gx, gy = random.choice(con)
        x, y = env.house.to_coor(gx, gy, True)
        loc.append([x,y])
        print([gx,gy,x,y])

    #print(loc)
    #print (env.cam.pos)

    for i in range(len(loc)):
        env.cam.pos.x = loc[i][0]
        env.cam.pos.y = env.house.robotHei
        env.cam.pos.z = loc[i][1]

        #mat = cv2.cvtColor(env.render_cube_map(), cv2.COLOR_BGR2RGB)
        mat = env.debug_render()
        rgb = env.render(RenderMode.RGB)
        semantic = env.render(RenderMode.SEMANTIC)
        print(gendp())
        #depth = np.array(int(gendp()*65535/3)).astype(np.uint16)
        depth = (gendp()*65535/3).astype(np.uint16)      #将浮点型数据转化为uint16
        print(depth)


        #cv2.imwrite('depth.png',depth)
        cv2.imshow("aaa", mat)
        cv2.waitKey(0)
        cv2.imshow("bbb", depth)
        cv2.waitKey(0)