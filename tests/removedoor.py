import json
import os

DOORMODELID = ['368','369','370','371','372','373','374','375','376','379','722','775','777','s_2358','s_2362',#fence
               '778','779','780', #arch
               '122','133','214','246','247','326','327','331','238','73','756','757','758','759','760','761','762','763','764','765','768','769','770','771','s_1762','s_1763','s_1764','s_1765','s_1766','s_1767','s_1768','s_1769','s_1770','s_1771','s_1772','s_1773'#door
               ]


def process_json(input_json_file, output_json_file):
    file_in = open(input_json_file, "r")
    file_out = open(output_json_file, "w")
    # load数据到变量json_data
    json_data = json.load(file_in)

    # 修改json中的数据
    for i in json_data['levels']:
        for j in i['nodes']:
            if j.get('modelId') in DOORMODELID:
                    j["valid"] = 0

    
    # 将修改后的数据写回文件
    file_out.write(json.dumps(json_data))
    file_in.close()
    file_out.close()


if __name__ == '__main__':
    #process_json("/home/fred/zyf/SUNCG_DIR/house/0a2f9f9b603e3960459f332c5635051e/house.json", "/home/fred/zyf/SUNCG_DIR/house/0a2f9f9b603e3960459f332c5635051e/house_change.json")
    list_dirs = os.walk('/home/fred/zyf/SUNCG_DIR/house/') 
    for root, dirs, files in list_dirs: 
        for d in dirs:
            #if 'house.json' not in d: 
            #    print (os.path.join(root, d, 'house_change.json'))
            #    os.mknod(os.path.join(root, d, 'house_change.json'))
            #if 'house.json' in d: 
                #print (os.path.join(root, d, 'house_change.json'))
            print (os.path.join(root, d))
            process_json(os.path.join(root, d, 'house.json'), os.path.join(root, d, 'house_change.json'))
                #os.mknod(os.path.join(root, d, 'house_change.json'))          
        #for f in files: 
            #print (os.path.join(root, f)) 