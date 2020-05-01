import os
import cv2
import json
import numpy as np
import urllib.request

def load_json_from_scalabel():
    scalabel_data = []
    scalabel_path = '/Users/spaceman/Downloads/Car/'       # path to directory containing .json files
    for _ in sorted(os.listdir(scalabel_path)):
        with open(os.path.join(scalabel_path, '2019-01_vehicle_damages_Results.json')) as f:
            data = json.load(f)
            scalabel_data.extend(data)
    return scalabel_data
def getLength():
    global len
    scalabel_data = load_json_from_scalabel()
    for i, img in enumerate(scalabel_data):
        l = len(img)
    return l
def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image
def download_images_from_s3():
    scalabel_data = load_json_from_scalabel()
    for index, img in enumerate(scalabel_data):
        image = url_to_image(img['name'])
        image_name = img['name'].replace('/', '_')
        cv2.imwrite(image_name, image)
    print(index, len(scalabel_data))
def extract_params_from_scalabel(img):
    img_path = ''
    global h, w
    try:
        for _ in img['labels']:
            image_name = img['name'].replace('/', '_')
            img = cv2.imread(img_path + image_name)
            h, w = img.shape[:2] # This is imageHeight, imageWidth
    except:
        pass
    return h, w
def getLabelAndPoints(img):
    label = []
    points = []
    try:
        for i in img['labels']:
            label.append(i['category'])
            poly2d_data = i['poly2d']
            for p in poly2d_data:
                points.append(p['vertices'])
    except:
        pass
    return label, points
def convert_vertices_to_points(img):
    label, ver = getLabelAndPoints(img)
    h, w = extract_params_from_scalabel(img)
    v = np.array(ver)
    global result
    points = []
    shape = [h, w]
    try:
        for i,_ in enumerate(label):
            result = np.divide(v[i],shape)
            points.append(result.tolist())
    except:
        pass
    return label, points
def convert_scalabel_to_dataturks(img):
    height, width = extract_params_from_scalabel(img)
    label, points = convert_vertices_to_points(img)
    name = img['name']
    anno = []
    try:
        for i in range(len(label)):
            labels = {'label':[label[i]],'shape':'polygon','points':points[i]}
            anno.append(labels)
            labels.update({'notes':'','imageWidth':width,'imageHeight':height})
    except:
        pass
    dataturk = {}
    dataturk['content']=name
    dataturk['annotation']=anno
    metadata = {'first_done_at':'','last_updated_at':'','sec_taken': 0,'last_updated_by':'','status': '','evaluation':'CORRECT'}
    dataturk.update({'extras':None,'metadata':metadata})
    return dataturk
def main():
    data = ''
    with open('/Users/spaceman/PycharmProjects/DataPreprocessing/data.json', 'w', encoding='utf-8') as file:
        file.write(data)
    f = open('/Users/spaceman/PycharmProjects/DataPreprocessing/data.json', 'a', encoding='utf-8')
    scalabel_data = load_json_from_scalabel()
    l = getLength()
    for _, img in enumerate(scalabel_data):
        dataturk = convert_scalabel_to_dataturks(img)
        dtturk = json.dumps(dataturk, separators=(',',':'))
        f.write(dtturk)
        f.write('\n')
        if _ == len(scalabel_data)/(l+1)-1 :
            break
    f.close()
# download_images_from_s3()
main()
