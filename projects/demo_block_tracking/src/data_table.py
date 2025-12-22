'''
常量与数据表定义 - JOHO串口总线舵机 Python SDK 
--------------------------------------------------
- 作者: 阿凯爱玩机器人@成都深感机器人
- Email: xingshunkai@qq.com
- 更新时间: 2021-12-19
--------------------------------------------------
'''
# 广播地址
SERVO_ID_BRODCAST = 0xFE
# 舵机状态掩码
STATUS_MASK_UNDER_VOLTAGE = 1			# 欠压保护
STATUS_MASK_OVER_VOLTAGE = 1 << 1		# 过压保护
STATUS_MASK_OVER_TEMPERATURE = 1 << 2	# 过温保护
STATUS_MASK_OVER_ELEC_CURRENT = 1 << 3	# 过流保护
STATUS_MASK_STALL_PROTECTION = 1 << 4	# 堵转保护
# 电机模式
MOTOR_MODE_SERVO = 0x01 # 舵机模式
MOTOR_MODE_DC = 0x00 	# 直流电机模式
# 电机旋转方向
DC_DIR_CCW = 0x01		# 电机顺时针旋转
DC_DIR_CW = 0x00		# 电机逆时针旋转
# 波特率
BDR_USER_DEFINE = 0 	# 用户自定义波特率
BDR_9600 = 1			
BDR_38400 = 2
BDR_57600 = 3
BDR_76800 = 4
BDR_115200 = 5
BDR_128000 = 6
BDR_250000 = 7
BDR_500000 = 8
BDR_1000000 = 9
# 扭力开关
TORQUE_ENABLE = 0x01
TORQUE_DISABLE = 0x00
# 示教点
TEACHING_POINT_1 = 1
TEACHING_POINT_2 = 2
TEACHING_POINT_3 = 3

# 串口总线舵机数据表
UART_SERVO_DATA_TABLE = {
	'DATA_VERSION_A': (0x03, 'B'), 		# 版本号 A
	'DATA_VERSION_B': (0x04, 'B'), 		# 版本号 B
	'SERVO_ID' : (0x05, 'B'),			# 舵机ID
	'STALL_PROTECTION_S' : (0x06, 'B'), # 舵机堵转保护
	'ANGLE_LOWERB' : (0x09, 'H'), 		# 舵机角度最小值 
	'ANGLE_UPPERB' : (0x0B, 'H'), 		# 舵机角度最大值
	'TEMPERATURE_PROTECTION_THRESHOLD': (0x0D, 'B'), # 温度保护阈值
	'VOLTAGE_UPPERB' : (0x0E, 'B'), 	# 电压上限, 单位V
	'VOLTAGE_LOWERB' : (0x0F, 'B'), 	# 电压下限, 单位V
	'TORQUE_UPPERB' : (0x10, 'H'), 		# 最大扭矩，取值范围 [0, 1000]
	'MIDDLE_POSI_ADJUST' : (0x14, 'h'), # 中位调整
	'TEACHING_POINT_1' : (0X16, 'H'), 	# 示教点1
 	'TEACHING_POINT_2' : (0X18, 'H'), 	# 示教点2
	'TEACHING_POINT_3' : (0X1A, 'H'), 	# 示教点3
	'MOTOR_MODE' : (0x1C, 'B'), 		# 电机模式
	'MOTOR_DIR' : (0x1D, 'B'),			# 电机旋转方向
	'BAUDRATE' : (0x1E, 'B'), 			# 波特率
	'CONTROL_P_KP' : (0x1F, 'B'), 		# 位置环 Kp
	'CONTROL_P_KI' : (0x20, 'B'), 		# 位置环 Ki
 	'CONTROL_P_KD' : (0x21, 'B'), 		# 位置环 Kd
	'CONTROL_V_KP' : (0x22, 'B'), 		# 速度环 Kp
	'CONTROL_V_KI' : (0x23, 'B'), 		# 速度环 Ki
	'CONTROL_V_KD' : (0x24, 'B'), 		# 速度环 Kd
	'TORQUE_ENABLE' : (0x28, 'B'), 		# 扭力开关
	'TARGET_POSITION' : (0x2A, 'H'), 	# 目标位置, 取值范围 [0, 4095]
	'RUNTIME_MS' : (0x2C, 'H'), 		# 运行时间, 单位ms
	'ELECTRIC_CURRENT_MA' : (0x2E, 'H'),# 电流, 单位mA
 	'CURRENT_POSITION' : (0x38, 'H'), 	# 当前位置, 取值范围 [0, 4095]
	'CURRENT_VELOCITY' : (0x3A, 'H'), 	# 当前速度, 单位 °/s
	'GO2TECHING_POINT' : (0x3C, 'B'), 	# 运行到示教点
	'CURRENT_VOLTAGE' : (0x3E, 'B'), 	# 当前电压, 单位V
	'CURRENT_TEMPERATURE' : (0x3F, 'B'),# 当前温度, 单位摄氏度
	'REG_WRITE_FLAG' : (0x40, 'B'), 	# 寄存器异步写入标志位
	'MOTOR_SPEED' : (0x41, 'h'), 		# 电机PWM, 取值范围[0, 100]
}
