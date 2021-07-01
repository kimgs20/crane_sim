#!/usr/bin/env python  

import rospy
import numpy as np

import tf2_ros

from sensor_msgs.msg import PointCloud2
from sensor_msgs import point_cloud2

from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

point_cloud_data = None

def velodyne_callback(data):
    global point_cloud_data
    point_cloud_data = data

rospy.init_node('min_dist', anonymous=False)

tfbuffer = tf2_ros.Buffer()
listener = tf2_ros.TransformListener(tfbuffer)

# velodyne_sub = rospy.Subscriber('/pcl_objects', PointCloud2, 
# velodyne_callback, queue_size=1)
velodyne_sub = rospy.Subscriber('/pcl_clusters', PointCloud2, 
velodyne_callback, queue_size=1)
pub_min_point = rospy.Publisher('/minimum_point', Point, queue_size=10)
rospy.loginfo('ready: collision warning')

rate = rospy.Rate(10) # 10Hz = pub 10 times at 1 second

while not rospy.is_shutdown():

    trans = tfbuffer.lookup_transform('world', 'load', rospy.Time(), rospy.Duration(1))
    # print(trans)
    load_x = trans.transform.translation.x
    load_y = trans.transform.translation.y
    load_z = trans.transform.translation.z
    # print(load_x, load_y, load_z)

    if point_cloud_data is not None:
        gen = point_cloud2.read_points(point_cloud_data, field_names=("x", "y", "z"), skip_nans=True)
        x = np.array([])
        y = np.array([])
        z = np.array([])

        for p in gen:
            # print(" x : %.3f  y: %.3f  z: %.3f" %(p[0],p[1],p[2]))
            dist = np.append(range,np.sqrt(p[0]**2+p[1]**2+p[2]**2))
            x = np.append(x, p[0])
            y = np.append(y, p[1])
            z = np.append(z, p[2])
            # print(x, y, z)
            dist = np.sqrt((x-load_x)**2 + (y-load_y)**2 + (z-load_z)**2)
            min_dist= np.min(dist)
            # print(min_dist)
            
            index = np.argmin(dist)
            # print(index)
            # print(x[index],y[index],z[index])

        # Publish position of minimum point to abstract map node
        min_point = Point()
        min_point.x = x[index]
        min_point.y = y[index]
        min_point.z = z[index]

        if min_dist<=1.5:
            pub_min_point.publish(min_point)
            print('warning: collision occurs')
        elif min_dist>1.5:
            min_point.x = 0.0
            min_point.y = 0.0
            min_point.z = -10.0
            pub_min_point.publish(min_point)
        rate.sleep()