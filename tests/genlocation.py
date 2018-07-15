# Copyright 2018-present, DrifterFun.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import tqdm
import cv2


import random
from House3D import objrender, Environment, load_config
from House3D.objrender import Camera, RenderMode



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
        depth = env.render(RenderMode.DEPTH)
        infmask = depth[:, :, 1]
        depth = depth[:, :, 0] * (infmask == 0)


        cv2.imwrite('depth.png',depth)
        cv2.imshow("aaa", mat)
        cv2.waitKey(0)