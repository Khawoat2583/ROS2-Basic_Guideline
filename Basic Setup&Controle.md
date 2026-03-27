<h1 align="left"># ROS2-Basic_Guideline</h1>
<p align="left">This guideline is used to guide the basic way to configure, control, etc., for ROS2.</p>
<h2 align="left">(Guideline: ALL PROCESS FOR BASIC ROS2)</h2>

## Section: "{Basic Setup&Controle!!}"
<p align="left">
<a>
  
  	START	
  
	1. (TO Config ROS2):
  
		1.) start terminal #(1st terminal!!)
		
		2.) go to file path: microROS-X_Example/start_up_robot
		
		3.) run python file: python3 config_robot.py
		
		4.) run the the terminal preferences for 3 terminals to check log and status
			#(Update log & status)
			-
			-
			-
			
	2. (To Ctrl ROS2):
		1.) start new terminal #(2nd terminal!!)
		
		2.) go to file path: microROS-X_Example/start_up_robot
		
		3.) run python file: python3 ctrl_robot.py
		"""
		Ctrl Path log:
			Control Your Yahboom Robot & Servo!
			----------------------------------
			Moving around:
			    u    i    o
			    j    k    l
			    m    ,    .
		
			q/z : increase/decrease max speeds by 10%
			w/x : increase/decrease only linear speed by 10%
			e/c : increase/decrease only angular speed by 10%

			Servo Control:
			    p : Press to -40, Release to 0 (Servo ID 1)

			CTRL-C to quit

			currently:	speed 0.15	turn 1.00
			
			"""
			【i】：เดินหน้า 【,】：ถอยหลัง
			【l】：หมุนขวา 【j】：หมุนซ้าย
			【u】：เลี้ยวซ้าย 【o】：เลี้ยวขวา
			【m】：ถอยซ้าย 【.】：ถอยขวา
			【p】：ทดสอบสั่งงาน Servo ID 1
			"""
		"""
	END	
</a>
</p>
