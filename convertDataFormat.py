import os
import cv2
import json
import numpy as np
import urllib.request


def load_json_from_scalabel():
    scalabel_path = '/Users/spaceman/Downloads/Car/'  # path to directory containing .json files
    with open(os.path.join(scalabel_path, '2019-01_vehicle_damages_Results.json')) as f:
        data = json.load(f)
    return data


def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def download_images_from_s3():
    scalabel_data = load_json_from_scalabel()
    for i, img in enumerate(scalabel_data):
        image = url_to_image(img['name'])
        image_name = img['name'].replace('/', '_')
        cv2.imwrite(image_name, image)


def extract_height_and_width_from_scalabel(img):
    img_path = ''
    height = 0
    width = 0
    try:
        for _ in img['labels']:
            image_name = img['name'].replace('/', '_')
            img = cv2.imread(img_path + image_name)
            height, width = img.shape[:2]
    except:
        pass
    return height, width


def extract_label_and_vertices_from_scalabel(img):
    label = []
    vertices = []
    try:
        for i in img['labels']:
            label.append(i['category'])
            poly2d_data = i['poly2d']
            for p in poly2d_data:
                vertices.append(p['vertices'])
    except:
        pass
    return label, vertices


def convert_vertices_to_points(img):
    label, vertices = extract_label_and_vertices_from_scalabel(img)
    h, w = extract_height_and_width_from_scalabel(img)
    array = np.array(vertices)
    points = []
    shape = [h, w]
    try:
        for i, _ in enumerate(label):
            result = np.divide(array[i], shape)
            points.append(result.tolist())
    except:
        pass
    return label, points


def convert_scalabel_to_dataturks(img):
    h, w = extract_height_and_width_from_scalabel(img)
    label, points = convert_vertices_to_points(img)
    name = img['name']
    annotate = []
    try:
        for i in range(len(label)):
            labels = {'label': [label[i]], 'shape': 'polygon', 'points': points[i]}
            annotate.append(labels)
            labels.update({'notes': '', 'imageWidth': w, 'imageHeight': h})
    except:
        pass
    metadata = {'first_done_at': '', 'last_updated_at': '', 'sec_taken': 0, 'last_updated_by': '', 'status': '',
                'evaluation': 'CORRECT'}
    dataturk = {}
    dataturk['content'] = name
    dataturk['annotation'] = annotate
    dataturk.update({'extras': None, 'metadata': metadata})
    return dataturk


def main():
    download_images_from_s3()
    # Create a new empty json file
    data = ''
    with open('/Users/spaceman/PycharmProjects/DataPreprocessing/data.json', 'w', encoding='utf-8') as file:
        file.write(data)
    # Open the new file and add content into it
    f = open('/Users/spaceman/PycharmProjects/DataPreprocessing/data.json', 'a', encoding='utf-8')
    scalabel_data = load_json_from_scalabel()
    for _, img in enumerate(scalabel_data):
        dataturk = convert_scalabel_to_dataturks(img)
        dataturk = json.dumps(dataturk, separators=(',', ':'))
        f.write(dataturk)
        f.write('\n')
    f.close()


main()
