# commandHelper 
An addon for NVDA that provides a alternative method for executing scripts for people who have difficulty pressing complicated key combinations. 

### USAGE 

First you need to configure a method to invoke the wizard. A keyboard gesture can be assigned in NVDA preferences> Input gestures. You can also configure the control key in the addon preferences (see below).

When the wizard is invoked a layer of keyboard commands is activated with the following options: 

* Right and left arrows to select a category. 
* Up and down arrows to select a command from the selected category. 
* Space bar to apply a filter by voice. 
* Enter to execute the command. 
* Shift+enter runs the command as if its gesture had been pressed twice quickly. 
* Control+enter runs the command as if its gesture had been pressed three times. 
* Any letter A-Z to jump to the category with that initial letter. 
* F1 announces the gesture corresponding to the selected command. 
* Escape   leaves the command layer and restores normal keyboard operation. 

### Settings 

The gesture to activate the command helper can be modified in NVDA preferences> Input gestures. 



Some other keys can be customized in NVDA preferences> Options> Command Helper. 

* Enable / disable the use of the control key to launch the command helper. 
* Choose  key to quit the helper. 
* Choose key to anounce the gesture associated with a command. 
* Activate / deactivate the handling of the helper through the numeric keyboard. 


#### Using the control key to launch the helper 

With this option activated, the helper is launched by pressing the control key five times in a row. This is useful for people who find it difficult to press combinations of several keys at the same time. However, it can sometimes cause unintentional helper activation when you press the control key for other uses, for example control + C and control + V to copy and paste. To avoid this, you must reduce the repetition speed of the keyboard. This is configured in the Windows control panel. In the preferences dialog of the addon there is a button that pressing it takes you directly to it. It can also be opened by pressing Windows key + R and typing control.exe keyboard in the Windows run box. In the slider "Repetition rate" you have to set a value as low as possible. By setting it to zero you ensure that you will not have problems but the activation of the assistant will stop working by holding down the control key, which could be inconvenient for some users with reduced mobility who find it difficult to make repeated quick keystrokes and they prefer to launch the helper in this way. There is no universal configuration, each user must find the most suitable for their needs or preferences. 

#### Numpad keyboard

With this option enabled, the helper can be used with the numeric keypad keys. 

* 4 and 6 to choose a category. 
* 2 and 8 to select a command from the chosen category. 
* 5 to report the gesture corresponding to the selected command. 
* Enter to execute the command. 
* Plus  runs the command as if its gesture had been pressed twice quickly. 
* Minus  runs the command as if its gesture had been pressed three times. 
* Delete leaves the command layer and restores normal keyboard functionality. 

#### Filter through voice
 
In the virtual menu, press the space bar and speak to the microphone. The menu will show only the commands that match the spoken words. If the result is not satisfactory, press space again to perform another search or escape to return to the full menu.
 
for it to work it is necessary to have an internet connection.

Note about compatibility: The addon is ready to work with previous versions of NVDA. The oldest one that has been tested is 2018.1 but it should work with even older ones. However, no future support will be provided for specific issues that may arise in those versions. 