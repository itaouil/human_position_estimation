#!/usr/bin/env python

"""
    The following script converts
    the ROS std_msgs/Image type to
    OpenCV MAT format.
"""

# Modules
import os
import cv2
import sys
import rospy
import math
import message_filters

# Path library
from pathlib import Path

# OpenCV-ROS bridge
from cv_bridge import CvBridge, CvBridgeError

# Messages for requests and subscriptions
from sensor_msgs.msg import Image
from human_aware_robot_navigation.srv import *

def requestDetection(req):
    """
        Sends a service request to
        the person detection module.

        Arguments:
            param1: Request string (required by the msg)

        Returns:
            string: Service response (success or not)
    """
    # Wait for service to come alive
    rospy.wait_for_service('detection')

    try:
        # Build request
        request = rospy.ServiceProxy('detection', RequestDetection)

        # Get response from service
        response = request(req)

        # Access the response field of the custom msg
        rospy.loginfo("Detection service: %s", response.res)
        return response.res

    except Exception as e:
        rospy.loginfo("Error during human detection request: %s", e)

def store(cv_image):
    """
        Stores the converted raw image from
        the subscription and writes it to
        memory.

        Arguments:
            MAT: OpenCV formatted image
    """
    cv2.imwrite(str(Path(os.path.dirname(os.path.abspath(__file__))).parents[0]) + "/data/converted/image.png", cv_image)

def toMAT(rgb_image):
    """
        Converts raw RGB image
        into OpenCV's MAT format.

        Arguments:
            param1: raw_image (from camera feed)
    """
    try:
        cv_image = CvBridge().imgmsg_to_cv2(rgb_image, 'bgr8')
        return cv_image

    except Exception as CvBridgeError:
        print('Error during image conversion: ', CvBridgeError)

def processSubscriptions(rgb_image, depth_image):
    """
        Callback for the TimeSynchronizer
        that receives both the rgb raw image
        and the depth image, respectively
        running the detection module on the
        former and the mappin process on the
        former at a later stage in the chain.

        Arguments:
            sensor_msgs/Image: The RGB raw image
            sensor_msgs/Image: The depth image
    """
    # Check that subscriptions data are synchronized
    print("Received rgb and depth")
    # print(abs(rgb_image.header.stamp - depth_image.header.stamp))
    # print("Got some stuff in here.")

    # Processing the rgb image
    # rgb_cv_image = toMAT(rgb_image)
    # store(rgb_cv_image)

    # Request services
    # Send detection request on pre-processed image
    # rospy.loginfo("Requesting detection and mapping services")
    # requestDetection("req")

def main(args):

    # Initialise node
    rospy.init_node('subscriptions_sync', anonymous=True)

    try:
        # Subscriptions (via Subscriber package)
        rgb_sub   = message_filters.Subscriber("/xtion/rgb/image_raw", Image)
        depth_sub = message_filters.Subscriber("/xtion/depth/image", Image)

        # Synchronize subscriptions
        ats = message_filters.ApproximateTimeSynchronizer([rgb_sub, depth_sub], queue_size=5, slop=0.3)
        ats.registerCallback(processSubscriptions)

        # Spin it baby !
        rospy.spin()

    except KeyboardInterrupt as e:
        print('Error during main execution' + e)

# Execute main
if __name__ == '__main__':
    main(sys.argv)
