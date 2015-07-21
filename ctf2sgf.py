#ctf2sgf
#Written by cth
#https://github.com/sorokinpf/ctf2sgf

def findInArray(arr,sample):
	for i in range(len(arr)):
		if arr[i].find(sample)!=-1:
			return i 	
	return -1
	
class PositionSample:
	colors = {1:'b',2:'w',0:'X'} #(white,black,mark)	
	def __init__(self,st):
		brac1 = st.find('[')
		brac2 = st.find(']')
		type = st[:brac1]
		type = int(type)
		if type <=2:
			self.color = self.colors[type]
			self.isMark = False
		elif type == 5 or type ==6:
			self.isMark = True
			self.mark = '0'
			self.color = self.colors[type-4]			
		else:
			self.isMark = True
			self.mark = chr(type)
			self.color = 'X'
		self.point = st[brac1+1:brac2]
	def __str__(self):
		return self.color + '[' + self.point + ']' #error!
		
class GoMove:	
	def __init__(self,st):
		self.color = st[0]
		self.point = st[2:4]
	def __str__(self):
		return self.color+'['+self.point +']'
	
class GoFragment:
		
	def GetInfo(self):
		self.infoLine = findInArray(self.content,'#')-1		
		self.info = self.content[1:self.infoLine+1]
		
	def GetPosition(self):
		positionLine1 = findInArray(self.content[self.infoLine:],'(')
		positionLine2 = findInArray(self.content[self.infoLine:],')')
		self.positionLines = self.content[self.infoLine+positionLine1+1:self.infoLine+positionLine2]
		self.positionEndLine = positionLine2+self.infoLine
		self.position = []
		for line in self.positionLines:
			self.position.append(PositionSample(line))
		
	def GetMoves(self):
		self.movesCount = int(self.content[self.positionEndLine+1])
		self.moves = []
		for i in range(self.movesCount):
			self.moves.append(GoMove(self.content[self.positionEndLine+2+i]))
	
	def PrintInfo(self):
		result = ''
		for st in self.info[1:-1]:
			if st[0] == '\\':
				ind = st.find(' ')
				if ind == -1:
					st = ''
				else:
					st = st[ind+1:]
			result += st + '\n'
		result.strip()
		return result
			
	def ToSGF(self):
		result = '(;'
		black = []
		white = []
		marks = []
		specialMarks = []
		for sample in self.position:
			if sample.isMark == False:
				if sample.color == 'w':
					white.append(sample)
				if sample.color == 'b':
					black.append(sample)
			else:
				if sample.color == 'X':
					marks.append(sample)
				else:
					if sample.color == 'w':
						white.append(sample)
					if sample.color == 'b':
						black.append(sample)
					specialMarks.append(sample)
		if len(specialMarks)!=0:
			result+= 'CR'
			for sample in specialMarks:
				result += '[' + sample.point + ']' 
		if len(white)!=0:
			result+= 'AW'
			for sample in white:
				result += '[' + sample.point + ']'
		if len(black)!=0:
			result+= 'AB'
			for sample in black:
				result += '[' + sample.point + ']'
		if len(marks)!=0:
			result+= 'LB'
			for sample in marks:
				result += '[' + sample.point + ':' + sample.mark + ']'
		
		for move in self.moves:
			result+= '\n;' + move.color + '[' + move.point + ']';
		i = 1
		result+= 'LB'
		for move in self.moves:
			result+= '[%s:%d]'%(move.point,i) 
			i+=1
		for sample in marks:
			result += '[' + sample.point + ':' + sample.mark + ']'
		if len(specialMarks)!=0:
			result+= 'CR'
			for sample in specialMarks:
				result += '[' + sample.point + ']' 
		result+= 'C[' + self.preambula + '\n\n' + self.PrintInfo() + ']'		
		result += ')\n'
		return result
		
		
	
	def __init__(self,_content):
		self.content = _content
		self.preambula = self.content[0]
		self.GetInfo()
		self.GetPosition()
		self.GetMoves()
		print 'Fragment readed successfully'
		
		
		
		
			
class GoGameFile:
	
	def __init__(self,filename):
		file = open(filename)
		data = file.read()
		lines = data.split('\n');
		#striping removing empty strings:
		content = []
		for line in lines:
			line = line.strip()
			if len(line)>0: content.append(line)
		print '%d lines in %s' % (len(content),filename)
		self.boardSize = int(content[0][2:])
		print 'Board size is:%d' %self.boardSize
		self.fragmentsNumber = int(content[1])
		print 'File contains %d fragments' % self.fragmentsNumber
		#fragments begins at line before [{
		parseData = content[2:]
		self.fragments = []
		while True:			
			nextFragmentStart = findInArray(parseData[2:],'[{')			
			if nextFragmentStart == -1:
				self.fragments.append(GoFragment(parseData))
				break
			nextFragmentStart += 2
			self.fragments.append(GoFragment(parseData[:nextFragmentStart-1]))
			parseData = parseData[nextFragmentStart-1:]
		if len(self.fragments)!= self.fragmentsNumber:
			print 'Number of fragments error'
		print 'File read OK';
		
	def SaveAsSGF(self,filename):
		intro = """"(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]
RU[Japanese]SZ[19]KM[0.00]
PW[White]PB[Black]\n"""
		result = intro
		result += 'C[Converted by ctf2sgf.\n\n https://github.com/sorokinpf/ctf2sgf]\n'
		for fragment in self.fragments:
			result+=fragment.ToSGF()
		result += ')'
		file = open(filename,'w')
		file.write(result)
		print 'Saved as %s' % filename
		
import sys

def main():
	if len(sys.argv)<2:
		print 'Usage:\npython ctf2sgf.py [input filename] [output filename]\nIf output filename is not specified result writes to "out.sgf"'
		return
	input = sys.argv[1]
	output = 'out.sgf' if len(sys.argv)<3 else sys.argv[2]
	file = GoGameFile(input)
	file.SaveAsSGF(output)
	
	
if __name__ == '__main__':
	main()
