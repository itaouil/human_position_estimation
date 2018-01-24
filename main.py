#!/usr/bin/env python

"""
    Main.

    Listens to in-coming data and
    handles the logic.
"""

# Modules
from __future__ import print_function
from __future__ import division
import rospy
import sys
import cv2
import os
import tf
import random
import math

# Message data type
from sensor_msgs.msg import Image

# Modules
from modules import PersonDetection

class HARN:

    def __init__(self):
        """ Class constructor """

        # Data
        self.img_raw = None

        # Object instances
        self.pd = PersonDetection()

        # Image subscribtion
        self.image_raw = rospy.Subscriber('camera/rgb/image_raw', Image, self.set_raw_image)

    def detect(self):
        """
            The routine calls the detection
            module and shows the detections.

            Arguments:
                image: The robots raw image
        """
        try:
            # Run detection and show
            frame = self.pd.detect(self.img_raw)
            cv2.imshow("Detections", frame)
            key = cv2.waitKey(1) & 0xFF

            # Stop execution when q pressed
            if key == ord("q"):
                break
        except Exception as e:
            raise

    def set_raw_image(self, data):
        """
            Sets the incoming camera
            data to a global variable.

            Arguments:
                param1: Raw image data
        """
        self.img_raw = data


def main(args):

    # Initialise node
    rospy.init_node('human_aware_robot_navigation', anonymous=True)

    try:

        # Application instance
        harn = HARN()

        # Let data flow
        rospy.loginfo("Getting data...")
        rospy.sleep(3)

        # Run the logic
        harn.detect()

        # Spin it baby !
        rospy.spin()

    except KeyboardInterrupt as e:
        print('Error during main execution' + e)

# Execute main
if __name__ == '__main__':
    main(sys.argv)
