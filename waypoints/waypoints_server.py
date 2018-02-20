#! /usr/bin/env python

"""
    Action server.

    Actionlib server that handles
    the navigation between the various
    waypoints.
"""

# Modules
import tf
import sys
import math
import rospy
import actionlib
import networkx as nx

# Routines
from gotopose import GoToPose

# Messages
import geometry_msgs.msg
from std_msgs.msg import String
from move_base_msgs.msg import *

# Custom server action message
from human_aware_robot_navigation.msg import WaypointsAction

# Topological map
from ./graphs/logik import graph

class WaypointServer:

    def __init__(self, name):
        """
            Constructor.

            Arguments:
                param1: server namespace
        """
        # Flag
        self.success = True

        # Movebase object
        self.gtp = GoToPose()

        # Frequency rate
        self.r = rospy.Rate(1)

        # Server namespace
        self.action_name = name

        # Action server object
        self.action_server = actionlib.SimpleActionServer(self.action_name,
                                                          WaypointsAction,
                                                          execute_cb = self.execute_cb,
                                                          auto_start = False)

        # Spin server and set callback
        self.action_server.start()

    def execute_cb(self):
        """
            Action server callback
            function. It gets called
            every time the client sends
            a goal and pipes it through.
        """
        # Hold goal
        goal = self.action_server.accept_new_goal().end_node

        # Check if node is valid
        if goal in graph.nodes():
            # Successful node
            rospy.loginfo("Setting the following goal %s", goal)

            # Found closest node
            current_node = self.getClosestPoint()

            # Compute shortest path to goal
            path = dijkstra_path(graph, current_node, goal)

            # Move along computed path
            move_along_path(path)

        else:
            rospy.loginfo("Node %s not found in the map!", goal)

    def move_along_path(self, path):
        """
            Logic to move along the
            shortest computed path.

            Arguments:
                param1: djikstra path
        """
        # Path iterator
        i = 0

        # Send robot to closest
        # node until it reaches
        # the goal (iteratively)
        while i < len(path)-1:
            # Send goal
            result = self.gtp.goto(path[i][0], path[i][1], 0)

            # If goal successful
            if result:
                # Succesfully reached state
                rospy.loginfo("Reached intermediate goal: %s", path[i][2])

                # Move to next goal
                i += 1
            else:
                # TODO: Check if human in front.
                # Keep going
                continue

    def getClosestPoint(self):
        """
            Finds closest point
            in the topological map.

            Returns:
                node: closest node in the topological map
        """
        # Check if base_link transform
        # is valid
        if self.getPose():
            # Set closest node
            closest_node = None

            # Get robot's current position
            (pose, _) = self.getPose()

            # Find minimum difference
            min_distance = sys.maxsize

            # Compute least squared
            for node in graph.nodes():
                x_diff = node[0] - pose.x
                y_diff = node[1] - pose.y
                distance = math.sqrt(x_diff**2 + y_diff**2)

                # Update distance if needed
                if distance < min_distance:
                    min_distance = distance
                    closest_node = node

            return closest_node

    def getPose(self):
        """
            Returns the base_link position
            in relation to the map.

            Returns:
                list: trans and quaternion of the ar marker (in the map)
        """
        try:
            return self.tf_listener.lookupTransform('/map', 'base_link', rospy.Time(0))
        except(tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
            rospy.loginfo("getPose function lookup EXCEPTION: %s", e)
