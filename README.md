<h1 align="left"># ROS2-Basic_Guideline</h1>
<p align="left">This guideline is used to guide the basic way to configure, control, etc., for ROS2 (Robot Operating System).</p>
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
			-Terminal#2 :
			bash -i -c "python3 ~/microROS-X_Example/start_up_robot/watchdog.py; exec bash"
			-Terminal#4 :
			bash -i -c "sh ~/microROS-X_Example/start_up_robot/start_Camera_computer.sh; exec bash"
			-Terminal#5 :
			bash -i -c "sh ~/microROS-X_Example/start_up_robot/start_agent_computer.sh; exec bash"
			
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

## Section: "{Setup for "Map Scanning" by using "Slam map" in ROS2!!}"
<p align="left">
<a>

	#(start terminal to microROS(start up file) for config the robot)
	#(run the agent 3 terminals for ROS2 check log (Update log))
	#(Before start the process need to place the ROS2 at the start point)
	START 
	1. (To Setup "Map Scanning" by using "Slam Map" for ROS2):
		1.) start new terminal #(3rd terminal!!)
		
		2.) go to file path: microROS-X_Example/slam_map/
		
		3.) run python file with ROS2 launch: ros2 launch map_slamtoolbox_launch.py
		
	2. (To Ctrl and Save Current Map for ROS2):
		1.) start new terminal #(4th terminal!!)
		
		2.) go to file path: microROS-X_Example/slam_map/
		
		3.) run python file: python3 ctrl_robot_save_map.py
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
			    s : SAVE Current map (to my_robot_map.pgm/.yaml)

			CTRL-C to quit

			currently:	speed 0.15	turn 0.80
			
			"""
			【i】：เดินหน้า 【,】：ถอยหลัง
			【l】：หมุนขวา 【j】：หมุนซ้าย
			【u】：เลี้ยวซ้าย 【o】：เลี้ยวขวา
			【m】：ถอยซ้าย 【.】：ถอยขวา
			【p】：ทดสอบสั่งงาน Servo ID 1
			"""
		"""
		4.) move around the map to recorded(scan) the map and that save the map	
	END	
</a>
</p>

## Section: "{Setup for set the "Waypoint" & "Automatic moving process" in ROS2!!}"
<p align="left">
<a>
	
	#(start terminal to microROS(start up file) for config the robot)
	#(run the agent 3 terminals for ROS2 check log (Update log))
	#(Before start the process need to place the ROS2 at the start point)
	START 
	1. (To Setup to set&get "Waypoint" for ROS2):
		1.) start new terminal #(5th terminal!!)
		
		2.) go to file path: microROS-X_Example/navigator_map
		
		3.) run python file with ROS2 launch: ros2 launch nav2_launch.py
		
		4.) start new terminal #(6th terminal!!)
		
		5.) go to file path: microROS-X_Example/navigator_map
		
		6.) run python file: python3 ctrl_robot_get_waypoint.py
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
			
			Special Actions:
			    p : Run Servo Sequence (Step -40 then 0)
			    s : SAVE Current Pose as Waypoint (to nav_waypoints.yaml)

			CTRL-C to quit

			currently:	speed 0.15	turn 0.80

			"""
			【i】：เดินหน้า 【,】：ถอยหลัง
			【l】：หมุนขวา 【j】：หมุนซ้าย
			【u】：เลี้ยวซ้าย 【o】：เลี้ยวขวา
			【m】：ถอยซ้าย 【.】：ถอยขวา
			【p】：ทดสอบสั่งงาน Servo ID 1
			"""
		"""
		
		7.) ctrl move: from starter point to every waypoint and save
			{ex}:
			7.1) move from starter point to 1st waypoint and than save it(1st)
			7.2) move from 1st waypoint to 2nd waypoint and than save it(2nd)
			7.3) move from 2nd waypoint to starter point
		8.) open nav_waypoint.yaml to edit and record the current possition
	
	2. (To make ROS2 automatic moving process for ROS2):
		#(if outliner has been error: need to reset the ROS2 & place at starter point!!)
		1.) close/canceled the ctrl robot terminal >> #(5th terminal)
		#(to not interruption while automatic process from manual
		(normal by ctrl from user)process ctrl)
		
		2.) start new terminal #(6th terminal!!)
		
		3.) go to file path: microROS-X_Example/navigator_map
		
		4.) run python file: python3 navigator_script.py
		#(it will show the pos that recorded before)\
		
		5.)now you can custom the step in waypoint 
		{ex} : 1st(home>1>2>home) custom(home>2>1>home)
	END
</a>
</p>
