# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2022 replay file
# Internal Version: 2021_09_16-01.57.30 176069
# Run by inkcloudy on Tue Feb  6 19:48:23 2024
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(1.11979, 1.12269), width=164.833, 
    height=111.37)
session.viewports['Viewport: 1'].makeCurrent()
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
execfile('fcc_job_commit.py', __main__.__dict__)
#: Warning: Index 1 in the sequence is out of range

---------- RUNTIME EXCEPTION HAS OCCURRED ----------
*** ERROR: ABAQUS/ABQcaeK rank 0 encountered a SEGMENTATION FAULT

---------- RUNTIME EXCEPTION HAS OCCURRED ----------
*** ERROR: ABAQUS/ABQcaeK rank 0 received the ABORT signal
