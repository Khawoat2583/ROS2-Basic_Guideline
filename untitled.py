# =====================================================
# !! Main_ROS2SouceCode MISSION !!
# =====================================================

# =====================================================
# SETUPS FOR ROS2
# =====================================================

# นำเข้า library หลักของ ROS2
import rclpy
# นำเข้าตัวควบคุมการนำทาง Nav2 และ enum ผลลัพธ์การนำทาง
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
# PoseStamped = ข้อความบอกตำแหน่ง+ทิศทาง, Twist = ข้อความควบคุมความเร็ว
from geometry_msgs.msg import PoseStamped, Twist
# Int32 = ข้อความตัวเลขจำนวนเต็ม ใช้ส่งคำสั่งมุม Servo
from std_msgs.msg import Int32
# Image = ข้อความภาพจากกล้อง ROS2
from sensor_msgs.msg import Image
# PointArray = ข้อความ custom ของ Yahboom รับผลจาก MediaPipe
from yahboomcar_msgs.msg import PointArray
# ใช้อ่านไฟล์ .yaml ที่เก็บข้อมูล waypoint
import yaml
# ใช้ time.sleep() หน่วงเวลา และ time.time() จับเวลา
import time
# library ตรวจจับ AprilTag
import apriltag
# library ประมวลผลภาพ
import cv2
# ใช้แปลงภาพจาก ROS Image format → OpenCV format
from cv_bridge import CvBridge


class TaskNavigator:
    def __init__(self):
        # สร้าง navigator object ซึ่งเป็น ROS2 Node ใช้สั่งนำทางทุกอย่าง
        self.nav = BasicNavigator()

        # สร้าง Publisher ส่งคำสั่งมุม Servo ไปยัง topic /servo_s1
        self.pub_servo = self.nav.create_publisher(Int32, '/servo_s1', 10)

        # สร้าง Publisher ส่งความเร็วหมุนไปยัง topic /cmd_vel
        self.cmd_vel_pub = self.nav.create_publisher(Twist, '/cmd_vel', 10)

        # flag บอกว่าตรวจพบภาพจาก MediaPipe หรือยัง ("Boolean")
        self.detected_mediapipe = False
        # flag บอกว่าตรวจพบ AprilTag หรือยัง ("Boolean")
        self.detected_apriltag  = False

        # เก็บหมายเลข ID ของ AprilTag ที่ตรวจพบ
        self.apriltag_id        = None

        # สร้าง CvBridge สำหรับแปลง ROS Image → OpenCV
        self.bridge = CvBridge()

        # สร้าง AprilTag detector สำหรับตรวจจับ tag จากภาพ
        self.at_detector = apriltag.Detector()

        # สร้าง Subscriber รับผลจาก MediaPipe ที่ topic /mediapipe/points
        # เมื่อมีข้อมูลใหม่จะเรียก mediapipe_callback อัตโนมัติ
        self.sub_points = self.nav.create_subscription(
            PointArray,
            '/mediapipe/points',
            self.mediapipe_callback,
            10
        )

        # ✅ แก้ไข #6 : เปลี่ยนชื่อ topic กล้องให้ตรงกับระบบจริง
        # ตรวจสอบชื่อ topic จริงด้วยคำสั่ง: ros2 topic list
        # แล้วแก้ไข CAMERA_TOPIC ให้ตรงกับชื่อ topic ของกล้องในระบบ
        CAMERA_TOPIC = '/camera/image_raw'  # ← แก้ตรงนี้ถ้าชื่อต่างออกไป

        # สร้าง Subscriber รับภาพดิบจากกล้อง
        # เมื่อมีภาพใหม่จะเรียก apriltag_callback อัตโนมัติ
        self.sub_image = self.nav.create_subscription(
            Image,
            CAMERA_TOPIC,
            self.apriltag_callback,
            10
        )

    # =================================================
    # Callback mediapipe
    # =================================================
    def mediapipe_callback(self, msg):
        # ถ้า array ของจุดที่ส่งมามีอย่างน้อย 1 จุด แปลว่าตรวจพบวัตถุ
        if len(msg.points) > 0:
            # เซต flag ว่าเจอภาพ MediaPipe แล้ว
            self.detected_mediapipe = True

    # =================================================
    # Callback AprilTag (ตรวจจากภาพกล้อง)
    # =================================================
    def apriltag_callback(self, msg):
        try:
            # แปลง ROS Image เป็น OpenCV format สี BGR
            cv_image   = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # แปลงภาพสีเป็น Grayscale เพราะ AprilTag detector ต้องการภาพขาวดำ
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # ตรวจจับ AprilTag ทั้งหมดในภาพ
            detections = self.at_detector.detect(gray_image)

            # ถ้าตรวจพบ tag อย่างน้อย 1 อัน
            if len(detections) > 0:
                # ✅ แก้ไข #4 : เซต apriltag_id ก่อน แล้วค่อยเซต flag
                # เพื่อป้องกัน race condition (ให้ id พร้อมก่อนที่ detect_image จะอ่าน flag)
                self.apriltag_id       = detections[0].tag_id  # เซต ID ก่อน
                self.detected_apriltag = True                   # เซต flag หลัง

        except Exception as e:
            # แสดง error ถ้าเกิดปัญหาระหว่างประมวลผลภาพ
            print(f"⚠️ AprilTag callback error: {e}")

    # =================================================
    # รีเซตตัวแปรตรวจจับทั้งหมด
    # =================================================
    def reset_detection(self):
        # รีเซต flag MediaPipe กลับเป็น False
        self.detected_mediapipe = False
        # รีเซต flag AprilTag กลับเป็น False
        self.detected_apriltag  = False
        # ล้างค่า ID ของ AprilTag
        self.apriltag_id        = None

    # =================================================
    # สั่ง Servo
    # =================================================
    def servo_action(self):
        print("✅ ตรวจพบภาพ (MediaPipe) -> สั่ง Servo")
        # สร้าง object ข้อความ Int32 สำหรับใส่ค่ามุม Servo
        val = Int32()

        # กำหนดค่ามุม Servo เป็น -40 องศา (หมุนไปทางซ้าย/ลง)
        val.data = -40
        # ส่งคำสั่งซ้ำ 5 ครั้ง เพื่อให้แน่ใจว่า Servo ตอบสนอง
        for _ in range(5):
            # ✅ แก้ไข #5 : เช็ค rclpy.ok() ก่อน publish ทุกครั้ง
            # ป้องกัน Exception กรณี ROS2 ปิดระหว่าง loop
            if not rclpy.ok():
                break
            # publish ค่ามุมไปยัง topic /servo_s1
            self.pub_servo.publish(val)
            # ให้ ROS2 ประมวลผล callback ที่ค้างอยู่ 1 รอบ
            rclpy.spin_once(self.nav, timeout_sec=0.1)
        # รอ 1 วินาที ให้ Servo เคลื่อนที่ถึงตำแหน่ง
        time.sleep(1)

        # กำหนดค่ามุม Servo กลับตำแหน่ง 0 (กลางสุด)
        val.data = 0
        # ส่งคำสั่งกลับตำแหน่ง 0 ซ้ำ 5 ครั้ง
        for _ in range(5):
            # ✅ แก้ไข #5 : เช็ค rclpy.ok() ก่อน publish ทุกครั้ง
            if not rclpy.ok():
                break
            # publish ค่ามุมไปยัง topic /servo_s1
            self.pub_servo.publish(val)
            # ให้ ROS2 ประมวลผล callback ที่ค้างอยู่ 1 รอบ
            rclpy.spin_once(self.nav, timeout_sec=0.1)
        # รอ 1 วินาที ให้ Servo เคลื่อนที่กลับถึงตำแหน่ง
        time.sleep(1)

        print("✅ Servo เสร็จสิ้น")

    # =================================================
    # หยุดการหมุน
    # =================================================
    def stop_rotation(self):
        # สร้าง Twist object ค่าเริ่มต้นทุกอย่างเป็น 0
        twist = Twist()
        # กำหนดความเร็วเชิงมุมแกน Z เป็น 0 (หยุดหมุน)
        twist.angular.z = 0.0
        # ส่งคำสั่งหยุดหมุนไปยังหุ่นยนต์
        self.cmd_vel_pub.publish(twist)
        # รอ 0.5 วินาที ให้หุ่นยนต์หยุดนิ่งสนิท
        time.sleep(0.5)

    # =================================================
    # หมุนหาภาพ (mediapipe หรือ apriltag) นาน 5 วินาที
    # คืนค่า : 'mediapipe' | 'apriltag' | None
    # =================================================
    def detect_image(self):
        # รีเซต flag ทั้งหมดก่อนเริ่มหาใหม่ทุกครั้ง
        self.reset_detection()

        # สร้าง Twist object สำหรับสั่งหมุน
        twist       = Twist()
        # บันทึกเวลาเริ่มต้นสำหรับจับเวลา timeout
        start_time  = time.time()
        # กำหนด timeout สูงสุด 5 วินาที
        TIMEOUT_SEC = 5.0

        print("🔍 เริ่มหมุนหาภาพ (timeout 5 วินาที)")

        # วนลูปตลอดจนกว่า ROS2 จะปิด หรือเจอภาพ หรือหมดเวลา
        while rclpy.ok():
            # คำนวณเวลาที่ผ่านไปตั้งแต่เริ่มหมุน
            elapsed = time.time() - start_time

            # ---- ตรวจสอบ timeout ----
            if elapsed >= TIMEOUT_SEC:
                # หมดเวลา 5 วินาที ยังไม่เจอภาพ
                print("⏰ หมดเวลา 5 วินาที ไม่พบภาพ")
                # หยุดหมุนก่อน return
                self.stop_rotation()
                # คืนค่า None = ไม่พบภาพ (หมดเวลา)
                return None

            # กำหนดความเร็วเชิงมุม 0.2 rad/s (หมุนทวนนาฬิกา)
            twist.angular.z = 0.2
            # ส่งคำสั่งหมุนไปยังหุ่นยนต์
            self.cmd_vel_pub.publish(twist)
            # ให้ ROS2 ประมวลผล callback (mediapipe/apriltag) 1 รอบ
            rclpy.spin_once(self.nav, timeout_sec=0.1)

            # ---- ตรวจสอบ AprilTag ก่อน (ให้ priority สูงกว่า) ----
            if self.detected_apriltag:
                print(f"🏷️  เจอ AprilTag แล้ว (ID: {self.apriltag_id})")
                # หยุดหมุนก่อน return
                self.stop_rotation()
                # คืนค่า 'apriltag' = พบ AprilTag
                return 'apriltag'

            # ---- ตรวจสอบ MediaPipe ----
            if self.detected_mediapipe:
                print("🎯 เจอภาพ MediaPipe แล้ว")
                # หยุดหมุนก่อน return
                self.stop_rotation()
                # คืนค่า 'mediapipe' = พบภาพ MediaPipe
                return 'mediapipe'

        # ✅ แก้ไข #2 : เพิ่ม stop_rotation() และ return
        # กรณี rclpy.ok() เป็น False (ROS2 ถูกปิด) ให้หยุดหมุนก่อนเสมอ
        # ป้องกันหุ่นหมุนค้างเมื่อ ROS2 ปิดกะทันหัน
        self.stop_rotation()
        return None

    # =================================================
    # ภารกิจหลังถึง waypoint
    # =================================================
    def perform_task(self, waypoint_name):
        print(f"\n📍 ถึงจุด {waypoint_name}")

        # ถ้าชื่อ waypoint คือ HOME (ไม่สนตัวพิมพ์เล็ก/ใหญ่)
        if waypoint_name.upper() == "HOME":
            print("🏠 HOME : พักระบบ")
            # พักระบบ 2 วินาที ไม่ต้องหาภาพ
            time.sleep(2)
        else:
            # waypoint อื่น ๆ → หมุนหาภาพ 5 วินาที
            result = self.detect_image()

            # กรณีที่ 1 : เจอภาพ MediaPipe → สั่ง Servo
            if result == 'mediapipe':
                self.servo_action()

            # กรณีที่ 2 : เจอ AprilTag → print ID
            elif result == 'apriltag':
                print(f"Apriltag : {self.apriltag_id}")

            # ✅ แก้ไข #3 : แยก None เป็น 2 กรณีให้ชัดเจน
            elif result is None:
                # กรณี 3a : ROS2 ถูกปิดระหว่างหาภาพ
                if not rclpy.ok():
                    print("⚠️ ROS2 ถูกปิดระหว่างการทำงาน")
                # กรณี 3b : หมดเวลา 5 วินาที ไม่พบภาพ
                else:
                    print(f"🚫 ไม่พบภาพที่จุด {waypoint_name} → ไป Waypoint ถัดไป")

        print(f"✔ เสร็จภารกิจ {waypoint_name}\n")


# =====================================================
# MAIN
# =====================================================
def main():
    # เริ่มต้น ROS2 runtime (ต้องเรียกก่อนใช้งาน ROS2 ทุกอย่าง)
    rclpy.init()
    # สร้าง object TaskNavigator
    task_nav = TaskNavigator()
    # เก็บ navigator ไว้ตัวแปร nav เพื่อสะดวกในการเรียกใช้
    nav      = task_nav.nav

    print("กำลังรอ Nav2...")
    # หยุดรอจนกว่า Nav2 stack จะพร้อมใช้งาน
    nav.waitUntilNav2Active()

    # วนลูปหลัก ทำงานซ้ำได้เรื่อย ๆ จนกว่า ROS2 จะปิด
    while rclpy.ok():

        # โหลดไฟล์ waypoint ทุกรอบ เผื่อมีการแก้ไขไฟล์ระหว่างใช้งาน
        try:
            # เปิดไฟล์ nav_waypoints.yaml
            with open("nav_waypoints.yaml", "r") as f:
                # อ่านข้อมูล yaml ทั้งหมด
                data          = yaml.safe_load(f)
                # ดึง list ของ waypoint ทั้งหมด
                all_waypoints = data["waypoints"]
        except Exception as e:
            # ถ้าโหลดไฟล์ไม่ได้ให้แสดง error และหยุดโปรแกรม
            print(e)
            break

        # แสดงรายการ waypoint ทั้งหมดให้ผู้ใช้เลือก
        print("\n========== WAYPOINT ==========")
        # วนแสดงชื่อ waypoint โดยเริ่มนับจาก 1
        for i, wp in enumerate(all_waypoints):
            print(f"[{i+1}] {wp['task']}")
        # ตัวเลือก 0 สำหรับออกจากโปรแกรม
        print("[0] Exit")

        # รับ input จากผู้ใช้
        user_input = input("เลือกลำดับ เช่น 1,3,2 : ")
        # ถ้ากด 0 ให้ออกจากลูปหลัก
        if user_input == '0':
            break

        try:
            # แปลง input เป็น list ของ index (ลบ 1 เพราะผู้ใช้นับจาก 1)
            order_indices     = [int(x.strip()) - 1 for x in user_input.split(',')]
            # ดึง waypoint ตามลำดับที่ผู้ใช้เลือก
            planned_waypoints = [all_waypoints[i] for i in order_indices]
        except:
            # ถ้าแปลงตัวเลขไม่ได้ให้วนกลับไปถามใหม่
            print("ใส่เลขผิด")
            continue

        # =============================================
        # วิ่งทีละ waypoint ตามลำดับที่เลือก
        # =============================================
        for wp in planned_waypoints:
            # สร้าง goal pose สำหรับส่งให้ Nav2
            goal_pose = PoseStamped()
            # กำหนด coordinate frame เป็น map
            goal_pose.header.frame_id    = 'map'
            # ใส่ timestamp ปัจจุบัน
            goal_pose.header.stamp       = nav.get_clock().now().to_msg()
            # กำหนดพิกัด x จากไฟล์ yaml
            goal_pose.pose.position.x    = wp['x']
            # กำหนดพิกัด y จากไฟล์ yaml
            goal_pose.pose.position.y    = wp['y']
            # กำหนดทิศทาง (quaternion z) จากไฟล์ yaml
            goal_pose.pose.orientation.z = wp['orientation']['z']
            # กำหนดทิศทาง (quaternion w) จากไฟล์ yaml
            goal_pose.pose.orientation.w = wp['orientation']['w']

            print(f"🚗 ไปที่ {wp['task']}")
            # ส่ง goal ให้ Nav2 เริ่มนำทาง (non-blocking)
            nav.goToPose(goal_pose)

            # วนรอจนกว่าจะถึง goal หรือเกิด error ตรวจสอบทุก 0.1 วินาที
            while not nav.isTaskComplete():
                time.sleep(0.1)

            # ดึงผลลัพธ์การนำทาง
            result = nav.getResult()

            # ถ้าถึง waypoint สำเร็จ → ทำภารกิจ
            if result == TaskResult.SUCCEEDED:
                task_nav.perform_task(wp['task'])
            # ถ้าถูกยกเลิก → หยุดแผนงานปัจจุบัน
            elif result == TaskResult.CANCELED:
                print("❌ ถูกยกเลิก")
                break
            # ถ้านำทางล้มเหลว → หยุดแผนงานปัจจุบัน
            elif result == TaskResult.FAILED:
                print("❌ ไปไม่ถึง")
                break

        # แจ้งเมื่อวิ่งครบทุก waypoint ในแผนที่เลือก
        print("✅ วิ่งครบแผนงานแล้ว")

    # ปิด ROS2 runtime เมื่อออกจากลูปหลัก
    rclpy.shutdown()


# รัน main() เมื่อรันไฟล์นี้โดยตรง (ไม่ใช่ import)
if __name__ == '__main__':
    main()