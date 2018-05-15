#!/usr/bin/env python2
# -*- coding: utf-8 -*-

""" A custom modification of the RatingScale class from psychopy: Get numeric ratings"""
from psychopy import visual
from psychopy import core, event
import time
from numpy import median

class RatingScaleMin():
	""" Creates a single screen with a Likert rating scale that accepts keyboard inputs
	and returns the last choice and the total response time in seconds.
	A title text, instructions and labels can be assigned and customized.
	The accept and response keys can be modified.
	"""
	def __init__(self,
				win,
				acceptKey=['return'],
				respKeys=['1', '2', '3', '4', '5', '6', '7'],
				scaleTitleText = '',
				extraText = '',
				scaleInstructions = '',
				labelsList = [''],
				labelsText = '',
				choiceText = '',
				acceptText='accept?',
				low = '1',
				high = '7',
				markerColor = 'green'):
		self.win = win
		self.acceptKey = acceptKey
		self.respKeys = respKeys
		self.scaleTitleText = scaleTitleText
		self.extraText = extraText
		self.scaleInstructions = scaleInstructions
		self.labelsList = labelsList
		self.labelsText = labelsText
		self.choiceText = choiceText
		self.acceptText = acceptText
		self.low = int(low)
		self.high = int(high)
		self.timer = core.Clock()
		self.xLeft = -0.8
		self.xRight = 0.8
		self.markerColor = markerColor
		self.lineLength = self.xRight- self.xLeft
		self.tickNumber = range(int(self.low), int(self.high)+1)
		self.x_pos_step = round(self.lineLength/(len(self.tickNumber)-1),3)
		self.x_pos_labels_step = round(self.lineLength/(len(self.labelsList)-1),3)
		self.tickList = [round((self.x_pos_step*i)-abs(self.xLeft),3) for i in range(self.high)]
		self.labelsPosList = [round((self.x_pos_labels_step*i)-abs(self.xLeft),3) for i in range(len(self.labelsList))]
		self.xMid = median(self.tickList)
		self.savedUnits = self.win.units
		self.win.setUnits(u'norm', log=None)

	def _initScaleTitle(self, pos = (0, 0.75), height = 0.15, color = 'DimGray', bold = True):
		self.pos = pos
		self.height = height
		self.color = color
		self.bold = bold

		self.scale_title = visual.TextStim(self.win,
							 pos = self.pos,
							 text = self.scaleTitleText,
							 units = 'norm',
							 height = self.height,
							 color = self.color,
							 bold = self.bold)

	def _initExtraText(self, pos = (0, 0.5), height = 0.13, color = 'black', bold = True):
		self.pos = pos
		self.height = height
		self.color = color
		self.bold = bold

		self.scale_extra_text = visual.TextStim(self.win,
									 pos = self.pos,
									 text = self.extraText,
									 units = 'norm',
									 height = self.height,
									 color = self.color,
									 bold = self.bold)

	def _initScaleInstruct(self, pos = (0, 0.2), height = 0.1, wrapWidth = 1.9, color = 'black', alignHoriz = 'center', bold = True):
		self.pos = pos
		self.height = height
		self.wrapWidth = wrapWidth
		self.color = color
		self.alignHoriz = alignHoriz
		self.bold = bold

		self.scale_instr_text = visual.TextStim(self.win,
							 pos = self.pos,
							 text = self.scaleInstructions,
							 units = 'norm',
							 height = self.height,
							 wrapWidth = self.wrapWidth,
							 color = self.color,
							 alignHoriz = self.alignHoriz,
							 bold = self.bold)

	def _initLine(self, start, end, lineColor = 'black', lineWidth = 1.5):
		self.start = start
		self.end = end
		self.lineColor = lineColor
		self.lineWidth = lineWidth

		self.scale_line = visual.Line(self.win,
								start = self.start,
								end   =  self.end,
								units = 'norm',
								lineColor = self.lineColor,
								lineWidth = self.lineWidth)

	def _initScaleMarker(self, fillColor, vertices = [ [-0.05, 0.05], [0.05, 0.05], [0, -0.05] ], lineColor = 'black'):
		self.vertices = vertices
		self.lineColor = lineColor
		self.fillColor = fillColor
		self.scale_marker = visual.ShapeStim(self.win,
								units = 'norm',
								vertices = self.vertices,
								lineColor = self.lineColor, 
								fillColor = self.fillColor)

	def _initTickMarks(self, lineColor= 'black', lineWidth=1):
		self.lineColor = lineColor
		self.lineWidth = lineWidth	
		self.tick_marks = visual.Line(self.win,
								lineColor = self.lineColor,
								lineWidth = self.lineWidth)

	def _initlabelsList(self, height = 0.08, color = 'black'):
		self.height = height
		self.color = color

		self.scale_labels = visual.TextStim(self.win,
							 units = 'norm',
							 height = self.height,
							 color = self.color)

	def _initlabelsText(self, pos = (0, -0.3), height = 0.08, wrapWidth = 1.9, color = 'black', alignHoriz = 'center'):
		self.pos = pos
		self.height = height
		self.wrapWidth = wrapWidth
		self.color = color
		self.alignHoriz = alignHoriz

		self.scale_labels_text = visual.TextStim(self.win,
							 pos = self.pos,
							 text = self.labelsText,
							 units = 'norm',
							 height = self.height,
							 wrapWidth = self.wrapWidth,
							 color = self.color,
							 alignHoriz = self.alignHoriz)

	def _initChoiceText(self, pos = (0, -0.6), height = 0.13, color = 'green', bold = True):
		self.pos = pos
		self.height = height
		self.color = color
		self.bold = bold

		self.choice_text = visual.TextStim(self.win,
									 pos = self.pos,
									 units = 'norm',
									 height = self.height,
									 color = self.color,
									 bold = self.bold)

	def _initAcceptText(self, pos = (0, -0.8), height = 0.13, color = 'DarkRed', bold = True):
		self.pos = pos
		self.height = height
		self.color = color
		self.bold = bold

		self.accept_text = visual.TextStim(self.win,
									 pos = self.pos,
									 text = self.acceptText,
									 units = 'norm',
									 height = self.height,
									 color = self.color,
									 bold = self.bold)

	def RatingScale(self):
		""" Draws the Rating Scale with the desired setup and takes keyboard input
		while there is no response, wait for keyboard input, once there is, press acceptKey to accept
		returns Response and response time
		"""
		self.timer.reset()
		self.respKey = []
		self.choice = []
		self.final_choice = []
		self.keyList = self.respKeys + self.acceptKey
		self.hit_accept = False
		self.y = -0.2 # labels y position

		self._initScaleTitle()
		self._initExtraText()
		self._initScaleInstruct()
		self._initLine(start = (self.xLeft, -0.05), end = (self.xRight,-0.05))
		self._initScaleMarker(fillColor= self.markerColor)
		self._initTickMarks()
		self._initlabelsList()
		self._initlabelsText()
		self._initChoiceText()
		self._initAcceptText()

		self.scale_marker.setPos((self.xMid,0), log=None)

		self.scale_title.draw()
		self.scale_extra_text.draw()
		self.scale_instr_text.draw()
		self.scale_line.draw()
		self.scale_marker.draw()
		self.scale_labels_text.draw()

		for label in self.labelsList:
			self.scale_labels.setText(label)
			self.x = self.labelsPosList[self.labelsList.index(label)]
			self.scale_labels.setPos((self.x, self.y),log=None)
			self.scale_labels.draw()

		for tick in self.tickList:
			self.tick_marks.setStart((tick,-0.05), log=None)
			self.tick_marks.setEnd((tick,-0.1), log=None)
			self.tick_marks.draw()

		self.win.flip()

		while self.hit_accept == False or self.choice == []:
			self.respKey = event.getKeys(keyList = self.keyList)
			if self.respKey != [] and set(self.respKey).issubset(self.respKeys):
				self.keyIndex = self.respKeys.index(self.respKey[-1])
				self.xPos = self.tickList[self.keyIndex]
				self.choice = self.tickNumber[self.keyIndex]
				self.choice_text.setText(self.choiceText + str(self.choice))
				self.scale_title.draw()
				self.scale_extra_text.draw()
				self.scale_instr_text.draw()
				self.scale_line.draw()
				self.scale_marker.setPos((self.xPos,0), log=None)
				self.scale_marker.draw()
				self.scale_labels_text.draw()
				self.choice_text.draw()
				self.accept_text.draw()
				for label in self.labelsList:
					self.scale_labels.setText(label)
					self.x = self.labelsPosList[self.labelsList.index(label)]
					self.scale_labels.setPos((self.x, self.y),log=None)
					self.scale_labels.draw()
				for tick in self.tickList:
					self.tick_marks.setStart((tick,-0.05), log=None)
					self.tick_marks.setEnd((tick,-0.1), log=None)
					self.tick_marks.draw()
				self.win.flip()
			if self.respKey != [] and set(self.respKey).issubset(self.acceptKey):
				if self.choice != []:
					self.hit_accept = True
			time.sleep(0.2)
		self.response_time = round(self.timer.getTime(),2)
		self.win.setUnits(self.savedUnits, log=None)
		event.clearEvents('keyboard')
		return(self.choice, self.response_time)
