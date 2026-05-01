# =====================================================
# Waypoint + ตรวจจับภาพ + หมุนหาภาพ + Servo (แก้ Servo ทำงาน)
# =====================================================

import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import Int32
from yahboomcar_msgs.msg import PointArray

import yaml
import time


class TaskNavigator:

    def __init__(self):

        self.nav = BasicNavigator()

        # publisher servo
        self.pub_servo = self.nav.create_publisher(
            Int32,
            '/servo_s1',
            10
        )

        # publisher cmd_vel
        self.cmd_vel_pub = self.nav.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # ตัวแปรตรวจจับภาพ
        self.detected = False

        # subscriber mediapipe
        self.sub_points = self.nav.create_subscription(
            PointArray,
            '/mediapipe/points',
            self.listener_callback,
            10
        )

    # =================================================
    # เมื่อเจอภาพ
    # =================================================
    def listener_callback(self, msg):

        if len(msg.points) > 0:
            self.detected = True

    # =================================================
    # สั่ง Servo (แก้ให้ทำงานจริง)
    # =================================================
    def servo_action(self):

        print("✅ ตรวจพบภาพ -> สั่ง Servo")

        val = Int32()

        # ไปตำแหน่ง -40
        val.data = -40

        for _ in range(5):
            self.pub_servo.publish(val)
            rclpy.spin_once(self.nav, timeout_sec=0.1)

        time.sleep(1)

        # กลับตำแหน่ง 0
        val.data = 0

        for _ in range(5):
            self.pub_servo.publish(val)
            rclpy.spin_once(self.nav, timeout_sec=0.1)

        time.sleep(1)

        print("✅ Servo เสร็จสิ้น")

    # =================================================
    # หมุนหาภาพจนกว่าจะเจอ
    # =================================================
    def detect_image(self):

        self.detected = False

        twist = Twist()

        print("🔍 เริ่มหมุนหาภาพจนกว่าจะเจอ")

        while rclpy.ok():

            # หมุนช้า ๆ
            twist.angular.z = 0.2 #เลขยิ่งมากขึ้นยิ่งหมุนเร็วขึ้น
            self.cmd_vel_pub.publish(twist)

            rclpy.spin_once(self.nav, timeout_sec=0.1)

            # ถ้าเจอภาพ
            if self.detected:

                print("🎯 เจอภาพแล้ว")

                # หยุดหมุน
                twist.angular.z = 0.0
                self.cmd_vel_pub.publish(twist)

                time.sleep(0.5)

                self.servo_action()
                return True

    # =================================================
    # ภารกิจหลังถึง waypoint
    # =================================================
    def perform_task(self, waypoint_name):

        print(f"\n📍 ถึงจุด {waypoint_name}")

        if waypoint_name.upper() == "HOME":

            print("🏠 HOME : พักระบบ")
            time.sleep(2)

        else:
            self.detect_image()

        print(f"✔ เสร็จภารกิจ {waypoint_name}\n")


# =====================================================
# MAIN
# =====================================================
def main():

    rclpy.init()

    task_nav = TaskNavigator()
    nav = task_nav.nav

    print("กำลังรอ Nav2...")
    nav.waitUntilNav2Active()

    while rclpy.ok():

        # โหลด waypoint
        try:
            with open("nav_waypoints.yaml", "r") as f:
                data = yaml.safe_load(f)
                all_waypoints = data["waypoints"]

        except Exception as e:
            print(e)
            break

        # แสดงรายการ waypoint
        print("\n========== WAYPOINT ==========")

        for i, wp in enumerate(all_waypoints):
            print(f"[{i+1}] {wp['task']}")

        print("[0] Exit")

        user_input = input("เลือกลำดับ เช่น 1,3,2 : ")

        if user_input == '0':
            break

        try:
            order_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            planned_waypoints = [all_waypoints[i] for i in order_indices]

        except:
            print("ใส่เลขผิด")
            continue

        # =============================================
        # วิ่งทีละ waypoint
        # =============================================
        for wp in planned_waypoints:

            goal_pose = PoseStamped()

            goal_pose.header.frame_id = 'map'
            goal_pose.header.stamp = nav.get_clock().now().to_msg()

            goal_pose.pose.position.x = wp['x']
            goal_pose.pose.position.y = wp['y']

            goal_pose.pose.orientation.z = wp['orientation']['z']
            goal_pose.pose.orientation.w = wp['orientation']['w']

            print(f"🚗 ไปที่ {wp['task']}")

            nav.goToPose(goal_pose)

            while not nav.isTaskComplete():
                time.sleep(0.1)

            result = nav.getResult()

            # ถึง waypoint สำเร็จ
            if result == TaskResult.SUCCEEDED:

                task_nav.perform_task(wp['task'])

            elif result == TaskResult.CANCELED:

                print("❌ ถูกยกเลิก")
                break

            elif result == TaskResult.FAILED:

                print("❌ ไปไม่ถึง")
                break

        print("✅ วิ่งครบแผนงานแล้ว")

    rclpy.shutdown()


if __name__ == '__main__':
    main()
