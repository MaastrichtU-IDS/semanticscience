from chimera import runCommand
frame = mdInfo['frame']
if frame == mdInfo['startFrame']:
	runCommand("roll y 3 40")
elif frame == 10:
	runCommand("color green")
elif frame == 50:
	runCommand("color orange")
	runCommand("rl :ala; color dodger blue :ala; rep stick :ala")
elif frame == 90:
	runCommand("~rl; rep wire :ala")
else:
	runCommand("color byhet")



