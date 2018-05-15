#!/usr/bin/env python2
# -*- coding: utf-8 -*-
		#######################################
		### Code experience affect in music ###
		#######################################
from psychopy import visual
from psychopy import gui
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from psychopy import core, event, info
import time, os, csv, pickle
import numpy as np
import pandas as pd
import pyaudio, wave
from RatingScaleClass import RatingScaleMin

version = "03-05"
#%% DECLARE VARIABLES AND FUNCTIONS
subject_info = {'Number':'',
                'Age': '',
                'Sex': [u'f', u'm'],
                'Music_experience': [u'< 3 ans', u'> 3 ans'],
                'Group': '',
                'Total_time': '0h 00m 00s'}

dictDlg = gui.DlgFromDict(dictionary=subject_info,
                title="Experiment v." + version, fixed=['Total_time', 'Group'], order=['Number', 'Age', 'Sex', 'Music_experience', 'Group', 'Total_time'])
if dictDlg.OK:
	if subject_info['Number'].isdigit() == False:
		print(subject_info['Number'] + ' is not a valid participant number. Please start again')
		sys.exit()
	if subject_info['Age'].isdigit() == False:
		print(subject_info['Age'] + ' is not a valid age. Enter only integer numbers. Please start again')
		sys.exit()
else:
	print('User Cancelled. Please start again')
	sys.exit()

group =  (int(subject_info['Number']) % 2) +1     # Group 1 for even participant numbers, group 2 for odd participant numbers
subject_info['Group'] = group                     # Group 1 evaluates 1st stim, group 2 evaluates 2nd stim               
																 
blocks = range(4)                                 # Blocks : training, music, speech, scream
skip_training = False
only_first_block = False
only_second_block = False
only_third_block = False
numPad = True
dummy_test = False
dummy = 6
pause_time = 300
pause_multiple = 70                               # Number of trials before a forced pause. Must be an integer multiple of total trials
start_e = core.getAbsTime()                       # Experiment start time for savefile
general_clock = core.Clock()                      # initialize clock
start_r = general_clock.getTime()                 # experiment start time in relative time
instructions = []
output_data = []
sounds_all = []
RS_valence = []
RS_arousal = []
RT_valence = []
RT_arousal = []

if numPad:
	respKeys = ['num_1','num_2','num_3','num_4','num_5','num_6','num_7']
else:
	respKeys = ['1', '2', '3', '4', '5', '6', '7']
acceptKey = ['return', 'num_enter']

ValenceTitleText = u"Première échelle"
ArousalTitleText = u"Deuxième échelle"
extraText = "Jugez l'extrait " + str(group) + "\n" + u"par rapport à l'extrait " + str(3-group)
scaleInstructions =  u"Évaluez l'extrait à l'aide de l'échelle suivante :"
labelsList = ['1', '2', '3', '4', '5', '6', '7']
Valence_labels = u"plus négatif					aucune différence					plus positif"
Arousal_labels = u"plus calme					aucune différence					plus énergique"
choiceText = "Choix : "
acceptText = "Valider ?" 

def play_wav(wav_filename, audio_order, chunk_size=1024):
	'''
	Play (on the attached system sound device) the WAV file
	Input: absolute_path + wav_filename.wav
	chunk_size = buffer size (integer)
	'''
	try:
		#print 'Playing file ' + wav_filename
		wf = wave.open(wav_filename, 'rb')
	except IOError as ioe:
		sys.stderr.write('IOError on file ' + wav_filename + '\n' + \
		str(ioe) + '. Skipping.\n')
		return
	except EOFError as eofe:
		sys.stderr.write('EOFError on file ' + wav_filename + '\n' + \
		str(eofe) + '. Skipping.\n')
		return
	# Instantiate PyAudio.
	p = pyaudio.PyAudio()
	# Open stream.
	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
									channels=wf.getnchannels(),
									rate=wf.getframerate(),
									output=True)
	# Read chunks in stream
	data = wf.readframes(chunk_size)
	while len(data) > 0:
		stream.write(data)
		data = wf.readframes(chunk_size)
		if audio_order==1:
			audio_1_text.draw()
		if audio_order==2:
			audio_2_text.draw()
		win.flip()
	# Stop stream.
	stream.stop_stream()
	stream.close()
	# Close PyAudio.
	p.terminate()

def sound_duration(soundfile):
	""" DURATION OF ANY WAV FILE
	Input   : path of a wav file (string)
	Returns : duration in seconds (float)
	"""
	import wave
	audio = wave.open(soundfile)
	sr = audio.getframerate()               # Sample rate [Hz]
	N = audio.getnframes()                  # Number of frames (int) 
	duration = round(float(N)/float(sr),2)  # Duration (float) [s]
	return duration

#%% PATH DEFINITION
folder_type = ("01_Vox", "02_Mix", "03_Speech", "04_Mix_violin", "05_Scream") # Folders containing audio (corresponding to each 'condition')
sound_type = ("Vox", "Mix", "Speech", "Mix_violin", "Scream")              # Filename prefix
tags = ["NM", "up", "down", "smile", "unsmile", "vib", "angus"]  # Filename suffix
subFold = []
snd_path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join('.','Data')

for i in range(14):
	subFold.append(str(i+1).zfill(2))                            # subfolder strings to concatenate in path
for condition in range(5):
	# Define path to the mixes
	sounds = {i : {j : os.path.join(snd_path, folder_type[condition], subFold[i] , sound_type[condition] + "_" + tags[j] + ".wav")for j in range(len(tags))} for i in range (len(subFold))}
	sounds_all.append(sounds)
del(sounds_all[4][12]) # Delete non existing sound (13) from sounds_all[scream]
del(sounds_all[4][13]) # Delete non existing sound (14) from sounds_all[scream]

#%% Create results filename
output_file_name = str(subject_info['Number']) + '_' + time.strftime("%d_%m_%y-%H_%M", time.localtime(start_e))
output_file_name = os.path.join(data_dir , output_file_name)

with open(output_file_name + '_subject_data.csv', 'wb') as f:
	w = csv.DictWriter(f, subject_info.keys())
	w.writeheader()
	w.writerow(subject_info)

# save_to_txt function
def file_write(file_name, text_list):
	# useful file writer function
	# takes filename and list as inputs and outputs txt file
	file_handler = open(file_name, 'a')
	thing = u''
	for item in text_list:
		thing = thing + (unicode(item)+'\t')
	thing = thing + '\n'
	file_handler.write(thing.encode('utf-8'))
	file_handler.close()

file_write(output_file_name + '.txt', 
	['rt_A', 'eval', 'gp', 'rs_V', 'stim_1', 'stim_2', 'excpt', 'effect', 'rt_V', '#tr', 'lang', '#ID', 'gen_s', 'dur', 'cond', 'rs_A']) # headers
		
#%% LOAD LISTS CONTAINING ALL STIMULI COMBINATIONS ORDER FOR EACH BLOCK

with open(os.path.join(snd_path, "utils", "order_block_1" + "_group_" + str(group) + '.csv'), 'rb') as csvfile:
	order_iter = csv.reader(csvfile, delimiter=',')
	order_block_1 = [data for data in order_iter]
with open(os.path.join(snd_path, "utils", "order_block_2" + "_group_" + str(group) + '.csv'), 'rb') as csvfile:
	order_iter = csv.reader(csvfile, delimiter=',')
	order_block_2 = [data for data in order_iter]
with open(os.path.join(snd_path, "utils", "order_block_3" + "_group_" + str(group) + '.csv'), 'rb') as csvfile:
	order_iter = csv.reader(csvfile, delimiter=',')
	order_block_3 = [data for data in order_iter]

# GET TRAINING TRIALS
training_block = 5 # One for each condition in blocks
order_training = np.reshape([order_block_1[np.random.randint(0,69)],
							order_block_1[np.random.randint(70,139)],
							order_block_1[np.random.randint(140,209)],
							order_block_2[np.random.randint(0,69)],
							order_block_3[np.random.randint(0,59)]
							],(training_block,len(order_block_1[0])))

# SHUFFLE THE CONTENT OF THE LISTS
np.random.shuffle(order_block_1) # Randomly shuffle the order of the songs, conditions and configurations
np.random.shuffle(order_block_2) # Randomly shuffle the order of the speech, conditions and configurations
np.random.shuffle(order_block_3) # Randomly shuffle the order of the screams, conditions and configurations

# Save a csv in order to save the intended order
with open(output_file_name + "_b1" + "_g" + str(group) + '.csv', 'wb') as f:
	w = writer = csv.writer(f)
	writer.writerows(order_block_1)
with open(output_file_name + "_b2" + "_g" + str(group) + '.csv', 'wb') as f:
	w = writer = csv.writer(f)
	writer.writerows(order_block_2)
with open(output_file_name + "_b3" + "_g" + str(group) + '.csv', 'wb') as f:
	w = writer = csv.writer(f)
	writer.writerows(order_block_3)

#%% WINDOW CONFIGURATION
#screen size
screen_width = 1920 #1910x
screen_height = 1080 #1070
wrap_width = 1.8

####### PREPARE INSTRUCTIONS AND QUESTIONS ######## 

# prepare window, instructions and stims    
win = visual.Window([screen_width, screen_height],
							fullscr = True,
							pos = (0,0),
							allowGUI = False,
							monitor='testMonitor',
							units='norm',
							screen = 0,
							color = [200, 200, 200],
							colorSpace = 'rgb255')#,
							#UseRetina = True) # window
 
# Read instructions from files
for block in blocks:
	instructions_file = os.path.join(".","utils","instructions_group_" + str(group) + "_block_" + str(block) + ".txt")
	with open(instructions_file, 'r') as textfile:
		instructions.append (textfile.read())

instruction_text = visual.TextStim(win,
							 pos = (-0.9, 0.9),
							 height = 0.07,
							 wrapWidth = wrap_width,
							 color = 'black',
							 alignVert= 'top',
							 alignHoriz ='left')

instruction_text_3 = visual.TextStim(win,
                             pos = (0.0, -0.9),
                             text = "Quand vous serez prêt, appuyez sur la barre 'espace'.",
                             height = 0.07,
                             color = 'black')
image_block3 = os.path.join(".","utils","scream_examples.png")
instruction_image = visual.ImageStim(win,
							image=image_block3,
							units='norm',
							pos=(0.0, -0.3),
							size=(1.5, 1.0))

block_number_text = visual.TextStim(win,
							 pos = (0, 0.2),
							 height = 0.25,
							 color = 'DimGray',
							 bold = True)

pause_text = visual.TextStim(win,
							 pos = (0, 0.1),
							 text = """\n Vous avez fini une partie du bloc. Vous pouvez faire une pause maintenant.
\n \n \n
ou si vous ne souhaitez pas faire une pause, appelez l'expérimentateur.""",
							 height = 0.15,                                   
							 wrapWidth = wrap_width,
							 color = 'DimGray',
							 bold = True)
pause_countdown_text = visual.TextStim(win,
							 height = 0.15,                                   
							 wrapWidth = wrap_width,
							 color = 'DarkRed')

block_part_text = visual.TextStim(win,
							 pos = (0, 0.1),
							 height = 0.2,                                   
							 wrapWidth = wrap_width,
							 color = 'DimGray',
							 bold = True)

resumption_text = visual.TextStim(win,
							 pos = (0, 0.1),
							 text = "La pause est terminée, appuyez sur la barre 'espace' pour continuer.",
							 height = 0.2,                                   
							 wrapWidth = wrap_width,
							 color = 'DimGray',
							 bold = True)

trial_number_text = visual.TextStim(win,
							 pos = (0, 0.2),
							 text = "Préparez-vous",
							 height = 0.15,                                   
							 wrapWidth = wrap_width,
							 color = 'DarkRed',
							 bold = True)
fixation_cross = visual.Rect(win,
							 width= 0.0625,
							 height = 0.125,
							 lineWidth= 10)

acknowledgement_text = visual.TextStim(win,
							 pos = (0, 0.2),
							 text = "L'expérience est terminée.\nMerci de votre participation !",
							 height = 0.2,                                   
							 wrapWidth = wrap_width,
							 color = 'black',
							 bold = True)

audio_1_text = visual.TextStim(win,
							 pos = (0, 0.2),
							 text = "Extrait 1",
							 height = 0.2,
							 color = 'green')

audio_2_text = visual.TextStim(win,
							 pos = (0, 0.2),
							 text = "Extrait 2",
							 height = 0.2,
							 color = 'green')

audio_bet_text = visual.TextStim(win,
							 pos = (0, 0.2),
							 text = "...",
							 height = 0.2,
							 color = 'green')

RS_V = RatingScaleMin(win = win,
					acceptKey=acceptKey,
					respKeys=respKeys,
					scaleTitleText = ValenceTitleText,
					extraText = extraText,
					scaleInstructions = scaleInstructions,
					labelsList = labelsList,
					labelsText = Valence_labels,
					choiceText = choiceText,
					acceptText= acceptText,
					low = '1',
					high = '7',
					markerColor = 'green')

RS_A = RatingScaleMin(win = win,
					acceptKey=acceptKey,
					respKeys=respKeys,
					scaleTitleText = ArousalTitleText,
					extraText = extraText,
					scaleInstructions = scaleInstructions,
					labelsList = labelsList,
					labelsText = Arousal_labels,
					choiceText = choiceText,
					acceptText= acceptText,
					low = '1',
					high = '7',
					markerColor = 'green')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
###### START EXPERIMENT #######
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#

# Trial parameters
T_FIX = 1.0             # sec. time for fixation cross     
T_BETWEEN = 1           # sec. dur ation between audios
trial_no = 1            # initialize trial nº
if skip_training == True:
	blocks = range(1,4)
if only_first_block==True:
	if skip_training == True:
		blocks = range(1,2)
	else:
		blocks = [0,1]
if only_second_block==True:
	if skip_training == True:
		blocks = range(2,3)
	else:
		blocks = [0,2]
if only_third_block==True:
	if skip_training == True:
		blocks = range(3,4)
	else:
		blocks = [0,3]
### START MAIN LOOP ###
for block in blocks:	
	if block == 0:
		block_number_text.setText('Entrainement')
	else:
		block_number_text.setText('Bloc # '+ str(block))
	block_number_text.draw()
	win.flip()
	time.sleep(2.5)
	# DISPLAY INSTRUCTIONS
	instruction_text.setText(instructions[block])
	instruction_text.draw()
	if block == 3:
		instruction_image.draw()
		instruction_text_3.draw()
	win.flip()
	event.waitKeys(keyList = ['space'])
	# Define number of trials for each block
	if block == 0:
		length_block = training_block
	elif block == 1 and dummy_test == False:
		length_block = len(order_block_1)
	elif block == 2 and dummy_test == False:
		length_block = len(order_block_2)
	elif block == 3 and dummy_test == False:
		length_block = len(order_block_3)
	elif block != 0 and dummy_test == True:
		length_block = dummy
	total_parts = length_block/pause_multiple
	part_count = 1
	
	#### TRIAL LOOP ###
	for i in range(length_block):
	# Define sound files for each block
		# Block 0 ----- Training
		if block==0:
			i_excerpt       = int(order_training[i][0])
			i_condition_str = order_training[i][1]
			i_condition     = sound_type.index(i_condition_str)
			i_audio1_str    = order_training[i][2]
			i_audio2_str    = order_training[i][3]
			i_audio_1       = tags.index(i_audio1_str)
			i_audio_2       = tags.index(i_audio2_str)
			audio_1 = sounds_all[i_condition][i_excerpt][i_audio_1]
			audio_2 = sounds_all[i_condition][i_excerpt][i_audio_2]
		# Block 1 ----- Music
		if block==1:
			i_excerpt       = int(order_block_1[i][0])
			i_condition_str = order_block_1[i][1]
			i_condition     = sound_type.index(i_condition_str)
			i_audio1_str    = order_block_1[i][2]
			i_audio2_str    = order_block_1[i][3]
			i_gender        = order_block_1[i][4]
			i_language      = order_block_1[i][5]
			i_effect        = order_block_1[i][6]
			i_eval          = order_block_1[i][7]
			i_audio_1       = tags.index(i_audio1_str)
			i_audio_2       = tags.index(i_audio2_str)
			audio_1 = sounds_all[i_condition][i_excerpt][i_audio_1]
			audio_2 = sounds_all[i_condition][i_excerpt][i_audio_2]
		# Block 2 ----- Speech
		if block==2:
			i_excerpt       = int(order_block_2[i][0])
			i_condition_str = order_block_2[i][1]
			i_condition     = sound_type.index(i_condition_str)
			i_audio1_str    = order_block_2[i][2]
			i_audio2_str    = order_block_2[i][3]            
			i_gender        = order_block_2[i][4]
			i_language      = order_block_2[i][5]
			i_effect        = order_block_2[i][6]
			i_eval          = order_block_2[i][7]
			i_audio_1       = tags.index(i_audio1_str)
			i_audio_2       = tags.index(i_audio2_str) 
			audio_1 = sounds_all[i_condition][i_excerpt][i_audio_1]
			audio_2 = sounds_all[i_condition][i_excerpt][i_audio_2]
		# Block 3 ----- Scream
		if block==3:
			i_excerpt       = int(order_block_3[i][0])
			i_condition_str = order_block_3[i][1]
			i_condition     = sound_type.index(i_condition_str)
			i_audio1_str    = order_block_3[i][2]
			i_audio2_str    = order_block_3[i][3]            
			i_gender        = order_block_3[i][4]
			i_language      = order_block_3[i][5]
			i_effect        = order_block_3[i][6]
			i_eval          = order_block_3[i][7]
			i_audio_1       = tags.index(i_audio1_str)
			i_audio_2       = tags.index(i_audio2_str) 
			audio_1 = sounds_all[i_condition][i_excerpt][i_audio_1]
			audio_2 = sounds_all[i_condition][i_excerpt][i_audio_2]
		# Get sound_duration of evaluated files
		if group==1:
			i_duration = sound_duration(audio_1)
		elif group==2:
			i_duration = sound_duration(audio_2)
		# Display current and remaining parts in block
		if i % pause_multiple == 0 and block != 0 and block != 3:
			block_part_text.setText('Partie ' + str(part_count) + ' sur ' + str(total_parts))
			block_part_text.draw()
			win.flip()
			time.sleep(1)
			part_count += 1
		if block != 0:
			print "Start trial # {}".format(trial_no)
		# fixation cross
		trial_number_text.draw()
		fixation_cross.draw()
		win.flip()
		time.sleep(T_FIX)
		 
		# Play audio
		audio_1_text.draw()
		win.flip()
		play_wav(wav_filename=audio_1, audio_order=1)
		
		audio_bet_text.draw()    
		win.flip()
		time.sleep(T_BETWEEN)
		
		audio_2_text.draw()
		win.flip()
		play_wav(wav_filename=audio_2, audio_order=2)
				
		# Get Valence and Arousal Rating
		(i_RS_valence, i_RT_valence) = RS_V.RatingScale()
		RS_valence.append(i_RS_valence)
		RT_valence.append(i_RT_valence)
		(i_RS_arousal, i_RT_arousal) = RS_A.RatingScale()
		RS_arousal.append(i_RS_arousal)
		RT_arousal.append(i_RT_arousal)

		# PAUSE MECHANISM
		if block != 0: # prevent pauses in training block
			inside_block = (i+1) % pause_multiple == 0 and i!=length_block-1
			end_block = block!=3 and i==length_block-1 and only_first_block==False # Do not pause on final block
			if inside_block or end_block: # Pause on multiples of pause_multiple and at the end of block 1
				print("pause")
				event.clearEvents('keyboard')
				unlock_key = []
				stopwatch = core.CountdownTimer(pause_time)
				while stopwatch.getTime() > 0:
					unlock_key = event.getKeys(keyList = ['d'])
					if unlock_key != []:
						break
					pause_countdown_text.setText("Attendez : " + time.strftime("%Mm %Ss", time.gmtime(stopwatch.getTime())))
					pause_text.draw()
					pause_countdown_text.draw()
					time.sleep(1)
					win.flip()
				resumption_text.draw()
				win.flip()
				event.waitKeys(keyList = ['space'])
		
		########### END of trial loop ############      
		if block != 0:
			output_data.append({
				'# ID'       :subject_info[u'Number'],
				'#Group'     :group,
				'#Trial'     :trial_no,
				'Effect'     :i_effect,
				'Condition'  :i_condition_str,
				'Excerpt'    :i_excerpt+1,
				'Stim_1'     :i_audio1_str,
				'Stim_2'     :i_audio2_str,
				'Eval_stim'  :i_eval,
				'rs_Valence' :RS_valence[-1],
				'rs_Arousal' :RS_arousal[-1],
				'rt_Valence' :RT_valence[-1],
				'rt_Arousal' :RT_arousal[-1],
				'Duration'   :i_duration,
				'Gender'     :i_gender,
				'Language'   :i_language
				})   # Dictionary containing all the relevant data for the analysis
			file_write(output_file_name + '.txt', output_data[trial_no-1].values()) # data to txt (just to be shure)
			trial_no += 1

# SAVE DATA AS CSV AND PICKLE AFTER LOOP
output_data_series = pd.DataFrame(output_data)            # Create a pandas DataFrame to better visualize data
output_data_series.to_csv(output_file_name + '.csv',
						index=False,
						header=True)                    # Save as csv
# output_data_series.to_pickle(output_file_name + '.pkl') # Save as pickle
acknowledgement_text.draw()
win.flip()
time.sleep(2.5)
print "Experiment is over"
finish_r = general_clock.getTime()
total_time = round(finish_r - start_r,2)
total_time = time.strftime("%Hh %Mm %Ss", time.gmtime(total_time))
subject_info['Total_time'] = total_time
with open(output_file_name + '_subject_data.csv', 'wb') as f:
	w = csv.DictWriter(f, subject_info.keys())
	w.writeheader()
	w.writerow(subject_info)
print 'Total time of execution = {}'.format(total_time)
# QUIT PSYCHOPY PROPERLY
win.close()
core.quit()
