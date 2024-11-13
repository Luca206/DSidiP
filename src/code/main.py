#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose

class RobotMover(Node):
    def __init__(self):
        super().__init__('robot_mover')
        
        # Publisher für die Zielposition des Roboters
        self.publisher_ = self.create_publisher(Pose, '/mitsubishi_robot/pose_command', 10)
        
        # Zielposition (Punkt B) definieren
        self.target_pose = Pose()
        self.target_pose.position.x = 0.5  # Ziel-X-Position in Metern
        self.target_pose.position.y = 0.2  # Ziel-Y-Position in Metern
        self.target_pose.position.z = 0.3  # Ziel-Z-Position in Metern
        
        # Orientierung des Endeffektors (Quaternionen)
        self.target_pose.orientation.x = 0.0
        self.target_pose.orientation.y = 0.0
        self.target_pose.orientation.z = 0.0
        self.target_pose.orientation.w = 1.0
        
        # Timer starten, um die Nachricht zu senden
        self.timer = self.create_timer(1.0, self.move_to_target)

    def move_to_target(self):
        # Zielposition wird gesendet
        self.get_logger().info("Sende Zielposition an den Roboter: Punkt B")
        self.publisher_.publish(self.target_pose)
        self.get_logger().info("Zielposition wurde gesendet. Der Roboter sollte sich zu Punkt B bewegen.")

def main(args=None):
    # Initialisiere rclpy
    rclpy.init(args=args)
    
    # Erstelle einen Knoten
    robot_mover = RobotMover()
    
    # Spin, bis der Knoten beendet wird
    rclpy.spin(robot_mover)
    
    # Nach Beendigung
    robot_mover.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
