import json
import xml.etree.ElementTree as ET
import copy

import numpy as np
from skimage.measure import points_in_poly

np.random.seed(0)


class Polygon(object):
    """
    Polygon represented as [N, 2] array of vertices
    """
    def __init__(self, name, vertices):
        """
        Initialize the polygon.
        Arguments:
            name: string, name of the polygon
            vertices: [N, 2] 2D numpy array of int
        """
        self._name = name
        self._vertices = vertices

    def __str__(self):
        return self._name

    def inside(self, coord):
        """
        Determine if a given coordinate is inside the polygon or not.
        Arguments:
            coord: 2 element tuple of int, e.g. (x, y)
        Returns:
            bool, if the coord is inside the polygon.
        """
        return points_in_poly([coord], self._vertices)[0]

    def vertices(self):

        return np.array(self._vertices)

class Annotation(object):
    """
    Annotation about the regions within WSI in terms of vertices of polygons.
    """
    def __init__(self):
        self._json_path = ''
        self._polygons_positive = []
        self._polygons_negative = []

    def __str__(self):
        return self._json_path

    def from_json(self, json_path):
        """
        Initialize the annotation from a json file.
        Arguments:
            json_path: string, path to the json annotation.
        """
        self._json_path = json_path
        with open(json_path) as f:
            annotations_json = json.load(f)

        for annotation in annotations_json['positive']:
            name = annotation['name']
            vertices = np.array(annotation['vertices'])
            polygon = Polygon(name, vertices)
            self._polygons_positive.append(polygon)

        for annotation in annotations_json['negative']:
            name = annotation['name']
            vertices = np.array(annotation['vertices'])
            polygon = Polygon(name, vertices)
            self._polygons_negative.append(polygon)

    def inside_polygons(self, coord, is_positive):
        """
        Determine if a given coordinate is inside the positive/negative
        polygons of the annotation.
        Arguments:
            coord: 2 element tuple of int, e.g. (x, y)
            is_positive: bool, inside positive or negative polygons.
        Returns:
            bool, if the coord is inside the positive/negative polygons of the
            annotation.
        """
        if is_positive:
            polygons = copy.deepcopy(self._polygons_positive)
        else:
            polygons = copy.deepcopy(self._polygons_negative)

        for polygon in polygons:
            if polygon.inside(coord):
                return True

        return False

    def polygon_vertices(self, is_positive):
        """
        Return the polygon represented as [N, 2] array of vertices
        Arguments:
            is_positive: bool, return positive or negative polygons.
        Returns:
            [N, 2] 2D array of int
        """
        if is_positive:
            return list(map(lambda x: x.vertices(), self._polygons_positive))
        else:
            return list(map(lambda x: x.vertices(), self._polygons_negative))

class Formatter(object):
    """
    Format converter e.g. CAMELYON16 to internal json
    """
    def camelyon16xml2json(inxml, outjson):
        """
        Convert an annotation of camelyon16 xml format into a json format.
        Arguments:
            inxml: string, path to the input camelyon16 xml format 某一特定xml文件的文件路径
            outjson: string, path to the output json format  特定的某一json文件的保存路径
        """
        root = ET.parse(inxml).getroot()
        annotations_tumor = \
            root.findall('./Annotations/Annotation[@PartOfGroup="Tumor"]')
        annotations_0 = \
            root.findall('./Annotations/Annotation[@PartOfGroup="_0"]')
        annotations_1 = \
            root.findall('./Annotations/Annotation[@PartOfGroup="_1"]')
        annotations_2 = \
            root.findall('./Annotations/Annotation[@PartOfGroup="_2"]')
        annotations_positive = \
            annotations_tumor + annotations_0 + annotations_1
        annotations_negative = annotations_2

        json_dict = {}
        json_dict['positive'] = []
        json_dict['negative'] = []

        for annotation in annotations_positive:
            X = list(map(lambda x: float(x.get('X')),
                     annotation.findall('./Coordinates/Coordinate')))
            Y = list(map(lambda x: float(x.get('Y')),
                     annotation.findall('./Coordinates/Coordinate')))
            vertices = np.round([X, Y]).astype(int).transpose().tolist()
            name = annotation.attrib['Name']
            json_dict['positive'].append({'name': name, 'vertices': vertices})

        for annotation in annotations_negative:
            X = list(map(lambda x: float(x.get('X')),
                     annotation.findall('./Coordinates/Coordinate')))
            Y = list(map(lambda x: float(x.get('Y')),
                     annotation.findall('./Coordinates/Coordinate')))
            vertices = np.round([X, Y]).astype(int).transpose().tolist()
            name = annotation.attrib['Name']
            json_dict['negative'].append({'name': name, 'vertices': vertices})

        with open(outjson, 'w') as f:
            json.dump(json_dict, f, indent=1)



    def json2camelyon16xml(self, dict, xml_path, group_color):

        group = ["_" + str(i) for i in range(len(group_color))]
        group_keys = dict.keys()

        assert len(group_keys) == len(group_color)
        # root and its two sub element
        root = ET.Element('ASAP_Annotations')
        sub_01 = ET.SubElement(root, "Annotations")
        sub_02 = ET.SubElement(root, "AnnotationGroups")

        # part of group. e.g. 2 color -- 2 part
        self.partofgroup(sub_02, group_color)

        # for vertices
        for i, key in enumerate(group_keys):
            group_ = group[i]
            cor_ = group_color[i]
            self.plot_area(sub_01, dict[key], group_, cor_)

        tree = ET.ElementTree(root)
        tree.write(xml_path)

    def partofgroup(self, father_node, group_color):

        cor = group_color
        for i in range(len(group_color)):
            title = ET.SubElement(father_node, "Group")
            title.attrib = {"Color": cor[i], "PartOfGroup": "None",
                            "Name": "_" + str(i)}
            ET.SubElement(title, "Attributes")

    def plot_area(self, father_node, all_area, group_, cor_):

        for i in range(len(all_area)):
            # print(all_area)
            dict_ = all_area[i]
            title = ET.SubElement(father_node, "Annotation")
            title.attrib = {"Color": cor_, "PartOfGroup": group_,
                            "Type": "Polygon", "Name": "_"+str(i)}

            coordinates = ET.SubElement(title, "Coordinates")
            dict_point = dict_["vertices"] # all vertices of the i area

            for j in range(len(dict_point)):
                X = dict_point[j][0]
                Y = dict_point[j][1]
                coordinate = ET.SubElement(coordinates, "Coordinate")
                coordinate.attrib = {"Y": str(Y), "X": str(X), "Order": str(j)}
