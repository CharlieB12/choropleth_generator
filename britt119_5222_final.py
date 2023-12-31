'''
Final Project
GEOG 5222

Charlie Britt
12/13/2023

Project #2: Choropleth Map
'''
import sys
sys.path.append('C:\\Users\\cbrit\\gisalgs')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from geom.shapex import *
import json

# custom errors to catch faulty user inputs
class PathError(Exception) :
    pass
class ClassifierError(Exception):
    pass
class PropError(Exception):
    pass


# function for equal interval classification
def equalInterval(val, numClass):
    maxV = max(val)
    minV = min(val)
    sze = (maxV - minV) / numClass
    intervals = []
    for i in range(numClass + 1):
        intervals.append(minV + i * sze)
    return intervals

# function for quantile classification.
def quantile(val, numClass): 
    intervals = []
    length = len(val)

    for i in range(numClass + 1):
        index = int(i * length / numClass)
        index = min(index, length - 1)
        intervals.append(val[index])

    return intervals

# extracts features depending on file
def get_features(path):
    if '.shp' in path:
        shp = shapex(path)
        features = shp
    elif '.geojson' in path:
        with open(path, 'r') as file:
            geojson_data = json.load(file)
        features = geojson_data['features']
    else:
        raise PathError()
    return features

# generates choropleth map
def choropleth(path, attribute, numClass, classMethod):

    features = get_features(path)

    # used for try, except block. if user input attribute is not in the file, raise error
    prop = features[0]['properties'].get(attribute)
    if prop is not None:
        # gets all the quantitative values from feature
        attribute_vals = [feature['properties'].get(attribute, 0) for feature in features]
    else:
        raise PropError()
    

    # decides which classification method will be used
    if classMethod == 'equal_interval':
        intervals = equalInterval(attribute_vals, numClass)
    elif classMethod == 'quantile':
        intervals = quantile(attribute_vals, numClass)
    else:
        raise ClassifierError()

    # color values
    colors = [ '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#006d2c', '#00441b']

    # creates figure and axis
    fig, ax = plt.subplots()

    # plots feature
    for feature in features:
        geometry = feature['geometry']

        # grabs value of specific attribute
        val = feature['properties'].get(attribute, 0)

        # decides which interval to put value in
        interval_idx = None
        for j in range(len(intervals) - 1):
            if intervals[j] <= val <= intervals[j + 1]:
                interval_idx = j
                break
        if interval_idx is None:
            interval_idx = len(intervals) - 2
            
        # grab coordinate data from feature
        coordinates = geometry['coordinates']

        # create polygon based on its type, assign color based on interval
        if geometry['type'] == 'MultiPolygon':
            for coords in coordinates:
                polygon = Polygon(coords[0], edgecolor='black', facecolor=colors[interval_idx])
                ax.add_patch(polygon)
        elif geometry['type'] == 'Polygon':
            polygon = Polygon(coordinates[0], edgecolor='black', facecolor=colors[interval_idx])
            ax.add_patch(polygon)

    # create boundary of plot
    ax.autoscale()
    # sort the intervals list so they are ascending on legend
    intervals.sort()
    
    # create legend based on intervals
    rectangles = []
    labels = []
    for i in range(numClass):
        rectangles.append(plt.Rectangle((0, 0), 1, 1, color=colors[i]))
        labels.append(f'{intervals[i]:.2f} - {intervals[i + 1]:.2f}')
    plt.legend(rectangles, labels, title = attribute, loc='lower right')

    plt.show()

    if '.shp' in path:
        features.close()

path = input('Enter the path to a .shp or .geojson file: ')
print()

# gets a list of attributes in file
feature = get_features(path)
properties = feature[0]['properties']
keys = properties.keys()
print('Atrributes: ',", ".join(keys))

attributes = input('Enter a quantitative attribute to classify: ')
classes = int(input('Enter the number of classes (1-6): '))
method = input('Enter the classsification method (equal_interval or quantile): ')

try:
    choropleth(path, attributes, classes, method)
except IndexError:
    print('Too many classes, try again')
except PropError:
    print("The attribute was not found")
except PathError:
    print("Unsupported file format. Use either .shp or .geojson")
except ClassifierError:
    print("Error: Use either 'equal_interval' or 'quantile'")

# Test scenarios
'''
# Test 1 (geojson):
Enter the path to a .shp or .geojson file: C:\\Users\\cbrit\\gisalgs\\data\\blockgrps_pop_franklin_2.geojson
Enter a quantitative attribute to classify: White
Enter the number of classes (1-6): 4
Enter the classsification method (equal_interval or quantile): quantile
# Output: A choropleth map with the population of white individuals in franklin county
# with 4 classes in quantile intervals.

# Test 2 (shp):
Enter the path to a .shp or .geojson file: C:\\Users\\cbrit\\gisalgs\\data\\blockgrps_pop_franklin_2.shp
Enter a quantitative attribute to classify: Black
Enter the number of classes (1-6): 6
Enter the classsification method (equal_interval or quantile): equal_interval
# Output: A choropleth map with the population of black individuals in franklin county
# with 6 classes in equal_intervals.

# Test 3 (fualty path):
Enter the path to a .shp or .geojson file: C:\\Users\\cbrit\\gisalgs\\data\\test.txt
Enter a quantitative attribute to classify: White
Enter the number of classes (1-6): 4
Enter the classsification method (equal_interval or quantile): quantile
# Output: Unsupported file format. Use either .shp or .geojson

# Test 4 (unkown attribute)
Enter the path to a .shp or .geojson file: C:\\Users\\cbrit\\gisalgs\\data\\blockgrps_pop_franklin_2.shp
Enter a quantitative attribute to classify: apple
Enter the number of classes (1-6): 4
Enter the classsification method (equal_interval or quantile): quantile
# Output: The attribute was not found

# Test 5 (Too many classes)
Enter the path to a .shp or .geojson file: C:\\Users\\cbrit\\gisalgs\\data\\blockgrps_pop_franklin_2.shp
Enter a quantitative attribute to classify: White
Enter the number of classes (1-6): 12
Enter the classsification method (equal_interval or quantile): quantile
# Output: 'Too many classes, try again'

# Test 6 (unknown classification method)
Enter the path to a .shp or .geojson file: C:\\Users\\cbrit\\gisalgs\\data\\blockgrps_pop_franklin_2.shp
Enter a quantitative attribute to classify: White
Enter the number of classes (1-6): 4
Enter the classsification method (equal_interval or quantile): gfjkl
# Output: Error: Use either 'equal_interval' or 'quantile'
'''










