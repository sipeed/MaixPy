'''
数据帧 - JOHO串口总线舵机 Python SDK 
--------------------------------------------------
- 作者: 阿凯爱玩机器人@成都深感机器人
- Email: xingshunkai@qq.com
- update in 2024-04-26 by joho
--------------------------------------------------
'''
import logging
import struct

# 设置日志等级
class Packet:
	'''数据包'''
	# 使用pkt_type来区分请求数据还是响应数据
	PKT_TYPE_REQUEST = 0 # 请求包
	PKT_TYPE_RESPONSE = 1 # 响应包
	HEADER_LEN = 2 # 帧头校验数据的字节长度
	HEADERS = [b'\xff\xff', b'\xff\xf5']
	
	CODE_LEN = 1 # 功能编号长度
	ID_LEN = 1 # 舵机ID的长度
	SIZE_LEN = 1 # 字节长度
	STATUS_LEN = 1 # 舵机状态长度
	CHECKSUM_LEN = 1 # 校验和长度

	@classmethod
	def calc_checksum_request(cls, servo_id, data_size, cmd_type, param_bytes):
		'''计算请求包的校验和'''
		bytes_buffer = struct.pack('>BBB', servo_id, data_size, cmd_type) + param_bytes
		return 0xFF - (sum(bytes_buffer) & 0xFF)

	@classmethod
	def calc_checksum_response(cls, servo_id, data_size, servo_status, param_bytes):
		'''计算响应包的校验和'''
		bytes_buffer = struct.pack('>BBB', servo_id, data_size, servo_status) + param_bytes
		return 0xFF - (sum(bytes_buffer) & 0xFF)

	@classmethod
	def is_response_legal(cls, packet_bytes):
		'''检验响应包是否合法'''
		# 获取帧头
		header = cls.HEADERS[cls.PKT_TYPE_RESPONSE]
		# 帧头检验
		if packet_bytes[:cls.HEADER_LEN] != cls.HEADERS[cls.PKT_TYPE_RESPONSE]:
			return False, None
		# 提取ID, 数据长度
		idx_status = cls.HEADER_LEN + cls.ID_LEN + cls.SIZE_LEN + cls.STATUS_LEN
		
		#2024更新判断字符长度
		if len(packet_bytes) <= (idx_status):
			return False, None
		
		servo_id, data_size, servo_status = struct.unpack('<BBB', packet_bytes[cls.HEADER_LEN : idx_status])
		
		# 长度校验
		param_bytes = packet_bytes[idx_status: -cls.CHECKSUM_LEN]
		if (len(param_bytes) + 2) != data_size:
			print("param size not match")
			return False, None

		# 校验和检验
		checksum1 = packet_bytes[-cls.CHECKSUM_LEN]
		checksum2 = cls.calc_checksum_response(servo_id, data_size, servo_status, param_bytes)
  
		# 校验和检查
		if checksum1 != checksum2:
			print(f"checksum1: {checksum1}  checksum2: {checksum2}")
			return False, None
		# 数据检验合格
		return True, [servo_id, data_size, servo_status, param_bytes]

	@classmethod
	def pack(cls, servo_id, cmd_type, param_bytes=b''):
		'''数据打包为二进制数据'''
		data_size = len(param_bytes) + 2
		checksum = cls.calc_checksum_request(servo_id, data_size, cmd_type, param_bytes)
		frame_bytes = cls.HEADERS[cls.PKT_TYPE_REQUEST] + struct.pack('<BBB', servo_id, data_size, cmd_type) + param_bytes + struct.pack('<B', checksum)
		return frame_bytes
	
	@classmethod
	def unpack(cls, packet_bytes):
		'''二进制数据解包为所需参数'''
		ret, result =  cls.is_response_legal(packet_bytes)
		if not ret:
			# 数据非法
			return None
		return result
