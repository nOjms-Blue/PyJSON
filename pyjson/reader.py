# フォーマットエラーの例外
class FormatErrorException(Exception):
	pass

class Reader:
	def __init__(self, text: str):
		self.__text = text
		self.__json = None
		
		self.__json = self.__read()
	
	# 空白、改行、タブ文字かどうか
	def __isSpace(self, _Char):
		if _Char == " " or _Char == "\t" or _Char == "\n":
			return True
		return False
	
	# リストか辞書型の中の値になるように変換
	def __readValue(self, textlist):
		type = None
		
		c = textlist[0]
		if c == None:
			return None
		elif not isinstance(c, str):
			if len(textlist) == 1:
				return c
			else:
				raise FormatErrorException("値を取得できませんでした。")
		elif (ord(c) >= ord("0") and ord(c) <= ord("9")) or c == ".":
			type = 0
		elif c == '"' or c == "'":
			type = c
		elif c.lower() == "t":
			if len(textlist) == 4:
				if textlist[1].lower() == "r" and textlist[2].lower() == "u" and textlist[3].lower() == "e":
					return True
		elif c.lower() == "f":
			if len(textlist) == 5:
				if textlist[1].lower() == "a" and textlist[2].lower() == "l" and textlist[3].lower() == "s" and textlist[4].lower() == "e":
					return False
		
		if type == None:
			return None
		
		if type == 0:
			temp = ""
			if textlist[0] == ".":
				temp = "0"
			for v in textlist:
				if (ord(v) < ord("0") or ord(v) > ord("9")) and v != ".":
					raise FormatErrorException("数値の値に使用できない文字が含まれていました。")
				temp = temp + v
			
			if "." in temp:
				return float(temp)
			else:
				return int(temp)
		elif type == '"' or type == "'":
			if textlist[-1] != type:
				raise FormatErrorException("文字列の開始と終了の引用符が異なりました。")
			
			temp = ""
			for v in textlist[1:-1]:
				if v == type:
					raise FormatErrorException("文字列の途中に引用符がありました。")
				temp = temp + v
			
			return temp
		
		return None
	
	# 単体のリストか辞書型を変換
	def __readListOrDict(self, textlist):
		mode = None
		if textlist[0] == "[" and textlist[-1] == "]":
			mode = "LIST"
			result = []
		elif textlist[0] == "{" and textlist[-1] == "}":
			mode = "DICT"
			result = {}
		
		if mode == None or result == None:
			raise FormatErrorException("リスト または 辞書型 ではありませんでした。")
		
		start = 1
		v_start = 1
		key = None
		in_quote = None
		next_waitsep = False
		is_waitsep = False
		for i in range(1, len(textlist) - 1, 1):
			c = textlist[i]
			
			if in_quote == None:
				if c == "'" or c =='"':
					in_quote = c
			else:
				if c == in_quote:
					in_quote = None
				continue
			
			if i == start:
				if self.__isSpace(c):
					start = i + 1
					v_start = start
					continue
			
			if mode == "DICT" and key == None:
				# 辞書型の場合、キーを取得
				if c == ":":
					end = i - 1
					while(self.__isSpace(textlist[end])):
						end = end - 1
						if end <= start:
							end = None
							break
					if end == None:
						raise FormatErrorException("辞書型のキーが存在しませんでした。")
					
					temp = textlist[start:i]
					if temp[0] == "'" or temp[0] == '"':
						if temp[-1] == temp[0]:
							if temp[0] in temp[1:-1]:
								raise FormatErrorException("辞書型のキーが決定できませんでした。")
							temp = temp[0:-1]
						else:
							raise FormatErrorException("辞書型のキーが決定できませんでした。")
					else:
						if "'" in temp or "'" in temp:
							raise FormatErrorException("辞書型のキーが決定できませんでした。")
					
					key = ""
					for v in temp:
						key = key + v
					
					v_start = i + 1
			else:
				# 値を取得
				if i == v_start:
					if self.__isSpace(c):
						v_start = v_start + 1
						continue
				
				if not is_waitsep:
					if self.__isSpace(c) or c == "," or i == (len(textlist) - 2):
						if self.__isSpace(c) or c == ",":
							temp = self.__readValue(textlist[v_start:i])
							is_waitsep = True
						else:
							temp = self.__readValue(textlist[v_start:i + 1])
							is_waitsep = False
						
						if mode == "LIST":
							result.append(temp)
						elif mode == "DICT":
							result[key] = temp
			
			# カンマを検出し、次の値へ
			if is_waitsep:
				if c == ",":
					start = i + 1
					v_start = start
					key = None
					is_waitsep = False
				elif not self.__isSpace(c):
					raise FormatErrorException("値の後に','がありませんでした。")
				continue
		
		return result
	
	# 変換開始
	def __read(self):
		lists = []
		for c in self.__text:
			lists.append(c)
		
		in_list = []
		in_string = None
		i = 0
		while(i < len(lists)):
			c = lists[i]
			
			if c == '"' or c == "'":
				if in_string != None:
					if c == in_string:
						in_string = None
				else:
					in_string = c
			elif c == "[":
				if in_string == None:
					in_list.append((i, "LIST"))
			elif c == "{":
				if in_string == None:
					in_list.append((i, "DICT"))
			elif c == "]":
				if in_string == None:
					if in_list[-1][1] == "LIST":
						value = self.__readListOrDict(lists[in_list[-1][0]:i + 1])
						
						lists = lists[:in_list[-1][0]] + [value] + lists[i + 1:]
						i = in_list[-1][0]
						del in_list[-1]
					else:
						raise FormatErrorException("開始文字が'['ではありませんでした。")
			elif c == "}":
				if in_string == None:
					if in_list[-1][1] == "DICT":
						value = self.__readListOrDict(lists[in_list[-1][0]:i + 1])
						
						lists = lists[:in_list[-1][0]] + [value] + lists[i + 1:]
						i = in_list[-1][0]
						del in_list[-1]
					else:
						raise FormatErrorException("開始文字が'{'ではありませんでした。")
			
			i = i + 1
		
		result = ""
		for v in lists:
			if not isinstance(v, str):
				if result != "":
					raise Exception("リスト または 辞書型 が複数存在しています。")
				
				result = v
		
		return result
	
	# 変換したJSON形式で取得
	def json(self):
		return self.__json
	
	# 変換元の文字列を取得
	def text(self):
		return self.text

# JSON形式として読み込む
def read(text: str):
	return Reader(text).json()