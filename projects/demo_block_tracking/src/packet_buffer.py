'''
数据帧缓冲队列 - JOHO串口总线舵机 Python SDK 
--------------------------------------------------
- 作者: 阿凯爱玩机器人@成都深感机器人
- Email: xingshunkai@qq.com
- 更新时间: 2021-12-19
--------------------------------------------------
'''
import logging
import struct
from .packet import Packet

class PacketBuffer:
	'''Packet中转站'''
	def __init__(self, is_debug=False):
		self.is_debug = is_debug
		self.packet_bytes_list = []
		# 清空缓存区域
		self.empty_buffer()
	
	def update(self, next_byte):
		'''将新的字节添加到Packet中转站'''
		
		# < int > 转换为 bytearray
		next_byte = struct.pack(">B", next_byte)
		# print(f"next_byte = {next_byte}")
		if not self.header_flag:
			
			# 接收帧头
			if len(self.header) < Packet.HEADER_LEN:
				# 向Header追加字节
				self.header += next_byte
				if len(self.header) == Packet.HEADER_LEN and self.header == Packet.HEADERS[Packet.PKT_TYPE_RESPONSE]:
					# print(f"recv header: {self.header}")
					self.header_flag = True
			elif len(self.header) == Packet.HEADER_LEN:
				# 首字节出队列
				self.header = self.header[1:] + next_byte
				# 查看Header是否匹配
				if self.header == Packet.HEADERS[Packet.PKT_TYPE_RESPONSE]:
					# print('header: {}'.format(self.header))
					self.header_flag = True
		elif not self.servo_id_flag:
			# 接收舵机ID
			self.servo_id += next_byte
			self.servo_id_flag = True
			# print(f"servo_id : {self.servo_id}")
		elif not self.data_size_flag:
			# 填充参数尺寸
			self.data_size += next_byte
			self.data_size_flag = True 
			# 参数长度
			self.param_len = struct.unpack('>B', self.data_size)[0] - 2
			# print(f"参数长度:  {self.param_len}")
			if self.param_len == 0:
				self.param_bytes_flag = True
		elif not self.servo_status_flag:
			# 舵机状态
			self.servo_status += next_byte
			self.servo_status_flag = True
			# print(f"servo_status: {self.servo_status}")
		elif not self.param_bytes_flag:
			# 填充参数
			if len(self.param_bytes) < self.param_len:
				self.param_bytes += next_byte
				if len(self.param_bytes) == self.param_len:
					self.param_bytes_flag = True
		else:
			# 计算校验和
			tmp_packet_bytes = self.header + self.servo_id + self.data_size + self.servo_status + self.param_bytes + next_byte
			# print(f"tmp_packet_bytes : {tmp_packet_bytes}")
			ret, result = Packet.is_response_legal(tmp_packet_bytes)
			if ret:
				self.checksum_flag = True
				# 将新的Packet数据添加到中转列表里
				self.packet_bytes_list.append(tmp_packet_bytes)
			# 重新清空缓冲区
			self.empty_buffer()
		
	def empty_buffer(self):
		# 数据帧是否准备好
		self.param_len = None
		# 帧头
		self.header = b''
		self.header_flag = False
		# 舵机ID
		self.servo_id = b''
		self.servo_id_flag = False
		# 数据长度
		self.data_size = b''
		self.data_size_flag = False
		# 舵机状态
		self.servo_status = b''
		self.servo_status_flag = False
		# 参数
		self.param_bytes = b''
		self.param_bytes_flag = False
	
	def has_valid_packet(self):
		'''是否有有效的包'''
		return len(self.packet_bytes_list) > 0
	
	def get_packet(self):
		'''获取队首的Bytes'''
		return self.packet_bytes_list.pop(0)

