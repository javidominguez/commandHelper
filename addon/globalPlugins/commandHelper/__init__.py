#!/usr/bin/python
#-coding: UTF-8 -*-

"""
command helper- NVDA addon

Provides a virtual menu where you can select any command to be executed without having to press its gesture.

This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright (C) 2021 Javi Dominguez <fjavids@gmail.com>
The keyboard command layer takes code from the Instant Translate addon by Alexy Sadovoy, Beqa Gozalishvili, Mesar Hameed, Alberto Buffolino and other NVDA contributors.

Third party licenses:

Module speech_recognition version 3.8.1 under license BSD
(C) Anthony Zhang (Uberi)
https://github.com/Uberi/speech_recognition

pyaudio, Python bindings for PortAudio, under the MIT License
Copyright (c) 2006 Hubert Pham
https://people.csail.mit.edu/hubert/pyaudio/#license

PortAudio Portable Cross-platform Audio I/O API
Copyright (c) 1999-2011 Ross Bencina and Phil Burk
www.portaudio.com/license.html
"""

from tones import beep
from functools import wraps
from keyboardHandler import KeyboardInputGesture
from logHandler import log
from . import parser
import addonHandler
import api
import appModuleHandler
import appModules
import baseObject
import braille
import brailleInput
import config
import globalCommands
import globalPluginHandler
import globalPlugins
import treeInterceptorHandler
import gui
import inputCore
import locale
import mouseHandler
import NVDAObjects
import scriptHandler
import speech
import subprocess
import time
import tones
import vision
import wx
import winInputHook

try:
	from . import speech_recognition
	log.info("Module speech_recognition version %s succesfully loaded\n(C) %s > license %s\nSee the file license.txt for more copyright details." % (speech_recognition.__version__, speech_recognition.__author__, speech_recognition.__license__))
except ImportError:
	speech_recognition = None
	log.warning("Import of the speech_recognition module failed. The speech recognition feature will not be available.")
except AttributeError:
	pass

# Settings compatibility with older versions of NVDA
from gui import settingsDialogs
try:
	from gui import NVDASettingsDialog
	from gui.settingsDialogs import SettingsPanel
except:
	SettingsPanel = object

confspec = {
	"controlKey":"boolean(default=True)",
	"exitKey":"string(default=escape)",
	"reportGestureKey":"string(default=F1)",
	"numpad":"boolean(default=False)"
}
config.conf.spec["commandHelper"]=confspec

mouseCallbackFunc = None

addonHandler.initTranslation()

# Below toggle code came from Tyler Spivey's code, with enhancements by Joseph Lee.

def finally_(func, final):
	"""Calls final after func, even if it fails."""
	def wrap(f):
		@wraps(f)
		def new(*args, **kwargs):
			try:
				func(*args, **kwargs)
			finally:
				final()
		return new
	return wrap(final)

def menuMessage(message):
	speech.speakMessage(message)
	braille.handler.message(message)

class Trigger():

	def __init__(self, keyNames, repetitions=5, timelapse=1.0):
		self.gestures = [KeyboardInputGesture.fromName(g).identifiers for g in keyNames]
		self.repetitions = repetitions
		self.timelapse = timelapse
		self.buffer = []

	def __call__(self, gesture):
		return self.check(gesture)

	def check(self, gesture):
		setattr(gesture, "timestamp", time.time())
		self.buffer.append(gesture)
		if len(self.buffer) < self.repetitions: return False
		if len(self.buffer) > self.repetitions: self.buffer.pop(0)
		if self.buffer[0].identifiers in self.gestures\
		and self.buffer[-1].timestamp-self.buffer[0].timestamp < self.timelapse\
		and len(set([g.identifiers for g in self.buffer])) == 1:
			return True
		return False

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = _("Command helper")

	speechOnDemand = {"speakOnDemand": True} if hasattr(speech.SpeechMode, "onDemand") else {}

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if hasattr(settingsDialogs, 'SettingsPanel'):
			NVDASettingsDialog.categoryClasses.append(CommandHelperPanel)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
			#TRANSLATORS: The configuration option in NVDA Preferences menu
			self.CommandHelperSettingsItem = self.prefsMenu.Append(wx.ID_ANY, u"Command helper...", _("Command Helper settings"))
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCommandHelperMenu, self.CommandHelperSettingsItem)
		self.toggling = False
		self.categories = []
		self.catIndex = 0
		self.commands = []
		self.commandIndex = 0
		self.recentCommands = {}
		self.firstTime = True
		self.__trigger__ = Trigger(("rightControl","leftControl"))
		self.cancelSpeech = True
		self.allowedBrailleGestures = set()
		self.oldGestureBindings = {}
		self.flagFilter = False

	def onCommandHelperMenu(self, evt):
		# Compatibility with older versions of NVDA
		gui.mainFrame._popupSettingsDialog(CommandHelperSettings)

	def terminate(self):
		try:
			if hasattr(settingsDialogs, 'SettingsPanel'):
				NVDASettingsDialog.categoryClasses.remove(CommandHelperPanel)
			else:
				self.prefsMenu.RemoveItem(self.CommandHelperSettingsItem)
		except:
			pass
		#1 store recents Upon leaving

	def mouseCapture(self, msg, x, y, injected):
		if msg in (513, 516, 519):
			# Error tone if a mouse button is pressed.
			tones.beep(200,30)
		return

	def lockMouse(self):
		global mouseCallbackFunc
		mouseCallbackFunc = winInputHook.mouseCallback
		winInputHook.setCallbacks(mouse=self.mouseCapture)

	def unlockMouse(self):
		global mouseCallbackFunc
		winInputHook.setCallbacks(mouse=mouseCallbackFunc)
		mouseCallbackFunc = None

	def getScript(self, gesture):
		if self.toggling and gesture.identifiers in self.__trigger__.gestures and self.cancelSpeech:
			# Prevents the voice from being muted when launching the helper. Otherwise nothing is spoken if the activation key is being pressed and the user does not know if the helper has been launched.
			gesture.speechEffectWhenExecuted = None
		if config.conf["commandHelper"]["controlKey"] and not self.toggling and self.__trigger__(gesture):
			# Launch of the helper by repeating a modifier key (in this case control).
			gesture.speechEffectWhenExecuted = None
			script = self.script_commandHelper(gesture)
		if not self.toggling or isinstance(gesture, brailleInput.BrailleInputGesture) or True in [gID.lower() in self.allowedBrailleGestures for gID in gesture.identifiers]:
			return globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		inputCore.manager._captureFunc = lambda self: not (gesture.isModifier and gesture.mainKeyName in (
		"leftWindows", "rightWindows", "leftAlt"))
		if not script:
			if "kb:"+config.conf["commandHelper"]["exitKey"] in gesture.identifiers or (
			config.conf["commandHelper"]["numpad"] and "kb:numpadDelete" in gesture.identifiers):
				script = finally_(self.script_exit, self.finish)
			else:
				script = finally_(self.script_speechHelp, lambda: None) 
		return script

	def finish(self):
		if self.flagFilter:
			if "speechFilter" in self.categories: self.categories.pop(self.categories.index("speechFilter"))
			if "speechFilter" in self.gestures: self.gestures.pop("speechFilter")
			self.flagFilter = False
			self.catIndex = -1
			self.script_nextCategory(None)
			return
		self.toggling = False
		self.unlockMouse()
		self.cancelSpeech = False
		self.clearGestureBindings()
		# Restore old bindings
		self.bindGestures(self.__gestures)
		for key in self.oldGestureBindings:
			script = self.oldGestureBindings[key]
			if hasattr(script.__self__, script.__name__):
				script.__self__.bindGesture(key, script.__name__[7:])
				if "showMessages" in config.conf["braille"]:
					#14233
					config.conf["braille"]["showMessages"] = self.brailleMessageTimeout
				else:
					config.conf["braille"]["noMessageTimeout"] = self.brailleMessageTimeout
		braille.handler.handleGainFocus(api.getFocusObject())

	def script_commandHelper(self, gesture):
		if inputCore.manager.isInputHelpActive:
			# Prevents the helper was launched when the keyboard help mode is active, instead it speaks the script help message.
			if config.conf["commandHelper"]["controlKey"]:
				menuMessage(self.script_commandHelper.__doc__)
			return
		elif inputCore.manager._captureFunc and not inputCore.manager._captureFunc(gesture):
			# Prevents the helper was launched when the keyboard is locked by the InputLock addon
			return
		if self.toggling:
			self.script_exit(gesture)
			self.finish()
			return
		for k in ("upArrow", "downArrow", "leftArrow", "rightArrow", "enter", "shift+enter", "control+enter", "numpadEnter", "shift+numpadEnter", "control+numpadEnter", "escape", "backspace", "F1", "F12", "numpad2", "numpad4", "numpad5", "numpad6", "numpad8", "numpadPlus", "numpadMinus", "numpadDelete"):
			# Save binds (to restore them later) and remove then before binding the new ones to avoid keyboard conflicts.
			try:
				script = KeyboardInputGesture.fromName(k).script
			except KeyError:
				script = None
			if script and self != script.__self__:
				try:
					script.__self__.removeGestureBinding("kb:"+k)
				except KeyError:
					pass
				else:
					self.oldGestureBindings["kb:"+k] = script
		self.bindGestures(self.__CHGestures)
		if config.conf["commandHelper"]["numpad"]:
			self.bindGestures(self.__numpadGestures)
		scanCodes = [
		# keyboard top row (1,2,3,4...)
		sc for sc in range(2,14)]+[41]+[
		# Second row (QWERT...)
		sc for sc in range(16,28)]+[
		# Third row (ASDF...)
		sc for sc in range(30,41)]+[43]+[
		# Bottom row (ZXCV...)
		sc for sc in range(44,54)]+[86]
		for sc in scanCodes:
			self.bindGesture(
			KeyboardInputGesture(modifiers={}, vkCode=0, scanCode=sc, isExtended=False).identifiers[-1],
			"skipToCategory")
		self.bindGesture("kb:"+config.conf["commandHelper"]["reportGestureKey"], "AnnounceGestures")
		self.bindGesture("kb:space", "speechRecognition")
		self.toggling = True
		self.flagFilter = False
		self.lockMouse()
		if "showMessages" in config.conf["braille"]:
			#14233
			self.brailleMessageTimeout = config.conf["braille"]["showMessages"]
			config.conf["braille"]["showMessages"] = 2
		else:
			self.brailleMessageTimeout = config.conf["braille"]["noMessageTimeout"]
			config.conf["braille"]["noMessageTimeout"] = True
		menuMessage(_("Available commands"))
		if speech.getState().speechMode == 3: beep(1500, 100)
		voiceOnly = True
		if self.firstTime:
			self.script_speechHelp(None)
			self.firstTime = False
			if braille.handler._messageCallLater: voiceOnly = False
		try:
			self.gestures = inputCore.manager.getAllGestureMappings(obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors)
		except:
			menuMessage(_("Failed to retrieve scripts."))
		self.categories = sorted(self.gestures, key=locale.strxfrm)
		self.categories.remove(self.scriptCategory)
		if self.recentCommands:
			self.categories.insert(0, _("Recents"))
			self.gestures[_("Recents")] = self.recentCommands
		#3 Implement another category with a list of the most used commands in order of frequency.
		# Braille gestures that will be allowed:
		try:
			for brGesture in\
			self.gestures[globalCommands.SCRCAT_BRAILLE][globalCommands.GlobalCommands.script_braille_scrollForward.__doc__].gestures\
			+self.gestures[globalCommands.SCRCAT_BRAILLE][globalCommands.GlobalCommands.script_braille_scrollBack.__doc__].gestures:
				self.allowedBrailleGestures.add(brGesture)
		except KeyError:
			pass
		# Braille gestures remapped:
		try:
			for brGesture in self.gestures[globalCommands.SCRCAT_BRAILLE][globalCommands.GlobalCommands.script_braille_nextLine.__doc__].gestures:
				self.bindGesture(brGesture, "nextCommand")
		except KeyError:
			pass
		try:
			for brGesture in self.gestures[globalCommands.SCRCAT_BRAILLE][globalCommands.GlobalCommands.script_braille_previousLine.__doc__].gestures:
				self.bindGesture(brGesture, "previousCommand")
		except KeyError:
			pass
		try:
			for brGesture in self.gestures[globalCommands.SCRCAT_OBJECTNAVIGATION][globalCommands.GlobalCommands.script_review_activate.__doc__].gestures:
				self.bindGesture(brGesture, "executeCommand")
		except KeyError:
			pass
		self.catIndex = -1
		self.script_nextCategory(None, voiceOnly)
		self.cancelSpeech = True
	#TRANSLATORS: message shown in Input gestures dialog for this script
	script_commandHelper.__doc__ = _("Provides a virtual menu where you can select any command to be executed without having to press its gesture.")

	@scriptHandler.script(**speechOnDemand)
	def script_nextCategory(self, gesture, verbose=True):
		if self.flagFilter:
			self.script_speechHelp(None)
			return
		self.cancelSpeech = False
		self.catIndex = self.catIndex+1 if self.catIndex < len(self.categories)-1 else 0
		if verbose: menuMessage(self.categories[self.catIndex])
		self.commandIndex = -1
		self.commands = sorted(self.gestures[self.categories[self.catIndex]], key=locale.strxfrm)

	@scriptHandler.script(**speechOnDemand)
	def script_previousCategory(self, gesture):
		if self.flagFilter:
			self.script_speechHelp(None)
			return
		self.cancelSpeech = False
		self.catIndex = self.catIndex -1 if self.catIndex > 0 else len(self.categories)-1
		menuMessage(self.categories[self.catIndex])
		self.commandIndex = -1
		self.commands = sorted(self.gestures[self.categories[self.catIndex]], key=locale.strxfrm)

	@scriptHandler.script(**speechOnDemand)
	def script_skipToCategory(self, gesture):
		if self.flagFilter:
			self.script_speechHelp(None)
			return
		self.cancelSpeech = False
		categories = (self.categories[self.catIndex+1:] if self.catIndex+1 < len(self.categories) else []) + (self.categories[:self.catIndex])
		try:
			self.catIndex = self.categories.index(filter(lambda i: i[0].lower() == gesture.mainKeyName, categories).__next__())-1
		# Compatibility with Python 2
		except AttributeError:
			try:
				self.catIndex = self.categories.index(filter(lambda i: i[0].lower() == gesture.mainKeyName, categories)[0])-1
				self.script_nextCategory(None)
			except IndexError:
				if self.categories[self.catIndex][0].lower() == gesture.mainKeyName:
					menuMessage(self.categories[self.catIndex])
				else:
					tones.beep(200, 30)
		# End of compatibility with Python 2
		except StopIteration:
			if self.categories[self.catIndex][0].lower() == gesture.mainKeyName:
				menuMessage(self.categories[self.catIndex])
			else:
				tones.beep(200, 30)
		else:
			self.script_nextCategory(None)

	@scriptHandler.script(**speechOnDemand)
	def script_nextCommand(self, gesture):
		if self.flagFilter and not self.commands:
			menuMessage(_("No matches found. Press the space bar to perform another search or escape to return to the full menu."))
			return
		self.cancelSpeech = False
		self.commandIndex = self.commandIndex + 1 if self.commandIndex < len(self.commands)-1 else 0
		menuMessage(self.commands[self.commandIndex])

	@scriptHandler.script(**speechOnDemand)
	def script_previousCommand(self, gesture):
		if self.flagFilter and not self.commands:
			menuMessage(_("No results. Press the space bar to perform another search or escape to return to the full menu."))
			return
		self.cancelSpeech = False
		self.commandIndex = self.commandIndex-1 if self.commandIndex > 0 else len(self.commands)-1
		menuMessage(self.commands[self.commandIndex])

	@scriptHandler.script(**speechOnDemand)
	def script_executeCommand(self, gesture):
		if self.commandIndex < 0:
			menuMessage(_("Select a command using up or down arrows"))
			return
		commandInfo = self.gestures[self.categories[self.catIndex]][self.commands[self.commandIndex]]
		script = None
		try:
			# Handling all scriptable object in the same order as in scriptHandler._yieldObjectsForFindScript

			# Gesture specific scriptable object
			if commandInfo.scriptName.startswith("kb:"):
				# Keypress emulation script
				script = scriptHandler._makeKbEmulateScript(commandInfo.scriptName)

			# Global plugins
			if not script and issubclass(commandInfo.cls, globalPluginHandler.GlobalPlugin):
				pluginPath = '.'.join(commandInfo.moduleName.split(".")[:2])
				for m in globalPluginHandler.runningPlugins:
					if m.__module__ == pluginPath:
						plugin = m
						break
				script = getattr(plugin, "script_"+commandInfo.scriptName)

			# App module
			if not script and issubclass(commandInfo.cls, appModuleHandler.AppModule):
				try:
					script = getattr(api.getForegroundObject().appModule , "script_"+commandInfo.scriptName)
				except:
					menuMessage(_("Can't run this script here"))
					return
	
			# Braille display
			if not script and issubclass(commandInfo.cls, braille.BrailleDisplayDriver):
				try:
					script = getattr(braille.handler.display, "script_" + commandInfo.scriptName)
				except AttributeError:
					pass
	
			# Vision enhancement provider
			if not script and issubclass(commandInfo.cls, vision.providerBase.VisionEnhancementProvider):
				for provider in vision.handler.getActiveProviderInstances():
					if isinstance(provider, baseObject.ScriptableObject):
						script = getattr(provider, "script_"+commandInfo.scriptName, None)
						if script:
							break
				else:
					menuMessage(_("Can't run this script while the corresponding provider is not enabled"))
					return

			# Tree interceptor
			if not script and issubclass(commandInfo.cls, treeInterceptorHandler.TreeInterceptor):
				treeInterceptor = api.getFocusObject().treeInterceptor
				if treeInterceptor and treeInterceptor.isReady:
					script = getattr(treeInterceptor, "script_"+commandInfo.scriptName, None)
					if script:
						if treeInterceptor.passThrough and not getattr(script, "ignoreTreeInterceptorPassThrough", False):
							menuMessage(_("Can't run this script while in focus mode"))
							return
					else:  # The current tree interceptor has not the requested script.
						menuMessage(_("Can't run this script here"))
						return
				else:  # The focused object has no tree intereceptor or the tree interceptor is not ready.
					menuMessage(_("Can't run this script here"))
					return

			# NVDAObject
			if not script:
				script = getattr(api.getFocusObject(), "script_" + commandInfo.scriptName, None)

			# Focus ancestors
			if not script:
				for ancObj in reversed(api.getFocusAncestors()):
					script = scriptHandler._getFocusAncestorScript(
						getattr(ancObj, "script_" + commandInfo.scriptName, None),
						ancObj,
						None,
					)
					if script:
						break

			# Configuration profile activation scripts
			if not script and issubclass(commandInfo.cls, globalCommands.ConfigProfileActivationCommands):
				script = getattr(globalCommands.configProfileActivationCommands, "script_"+commandInfo.scriptName)

			# Global commands
			if not script and issubclass(commandInfo.cls, globalCommands.GlobalCommands):
				script = getattr(globalCommands.commands, "script_"+commandInfo.scriptName)
			
			if not script:
				self.finish()
				raise RuntimeError(f"Failed to retrieve scripts for '{commandInfo.className}'. Not found in known modules.")
		except:
			self.finish()
			menuMessage(_("Failed to retrieve scripts."))
			raise
		try:
			g = inputCore._getGestureClsForIdentifier(commandInfo.gestures[0])
		except:
			g = KeyboardInputGesture
		self.flagFilter = False
		self.finish()
		try:
			scriptHandler.executeScript(script, g)
		except:
			raise
		else:
			if not isinstance(gesture, braille.BrailleDisplayGesture) and (gesture.modifierNames == ["shift"] or gesture.mainKeyName == "numpadPlus"):
				speech.cancelSpeech()
				scriptHandler.executeScript(script, g)
			elif not isinstance(gesture, braille.BrailleDisplayGesture) and (gesture.modifierNames == ["control"]  or gesture.mainKeyName == "numpadMinus"):
				speech.cancelSpeech()
				scriptHandler.executeScript(script, g)
				speech.cancelSpeech()
				scriptHandler.executeScript(script, g)
			if self.commands[self.commandIndex] not in self.recentCommands:
				key = self.commands[self.commandIndex]
				if commandInfo.className == "AppModule":
					key = "%s: %s" % (self.categories[self.catIndex], key)
				self.recentCommands[key] = commandInfo

	@scriptHandler.script(**speechOnDemand)
	def script_AnnounceGestures(self, gesture):
		self.cancelSpeech = False
		if self.commandIndex < 0:
			menuMessage(_("Select a command using up or down arrows"))
			return
		commandInfo = self.gestures[self.categories[self.catIndex]][self.commands[self.commandIndex]]
		gestureDisplayText = ""
		if commandInfo.gestures:
			try:
				gestureDisplayText = ".\n".join([": ".join(KeyboardInputGesture.getDisplayTextForIdentifier(g)) for g in commandInfo.gestures])
				menuMessage(gestureDisplayText)
			except:
				gestureDisplayText = "\n".join(commandInfo.gestures)
				menuMessage(gestureDisplayText)
		else:
			gestureDisplayText = _("There is no gesture")
			menuMessage(gestureDisplayText)
		log.info("%s on %s.%s\n%s\n%s" % (
		commandInfo.scriptName,
		commandInfo.moduleName,
		commandInfo.className,
		self.commands[self.commandIndex],
		gestureDisplayText))
		#9 Search for keyboard conflicts and announce them

	@scriptHandler.script(**speechOnDemand)
	def script_speechHelp(self, gesture):
		if self.flagFilter:
			menuMessage(_("Use up and down arrows to select a script and enter to run the selected. %s to clear filter and return to full menu. Press space to perform another voice search.") % _(config.conf["commandHelper"]["exitKey"]))
		else:
			menuMessage(_("Use right and left arrows to navigate categories, up and down arrows to select a script and enter to run the selected. %s to exit.") % _(config.conf["commandHelper"]["exitKey"]))

	def script_exit(self, gesture):
		if speech.getState().speechMode == 3: beep(800, 100)
		if self.flagFilter:
			menuMessage(_("Returning to the full menu"))
		else:
			if "showMessages" in config.conf["braille"]:
				#14233
				config.conf["braille"]["showMessages"] = self.brailleMessageTimeout
			else:
				config.conf["braille"]["noMessageTimeout"] = self.brailleMessageTimeout
			menuMessage(_("Leaving the command hhelper"))
			if speech.getState().speechMode == 3:
				time.sleep(0.1)
				beep(500, 60)

	@scriptHandler.script(**speechOnDemand)
	def script_speechRecognition(self, gesture):
		if not speech_recognition:
			menuMessage(_("Unavailable feature"))
			raise RuntimeError("The speech recognition feature is not available because the speech_recognition module could not be loaded.")
		mic = speech_recognition.Microphone()
		recognizer = speech_recognition.Recognizer()
		with mic:
			speech.speakMessage(_("Speak now"))
			try:
				audio = recognizer.listen(mic, timeout=3)
			except speech_recognition.WaitTimeoutError:
				speech.speakMessage(_("Nothing was heard. Make sure the microphone is connected and try again."))
				return
			try:
				recognizedText = recognizer.recognize_google(audio, language=locale.normalize(locale.getlocale()[0].split("_")[0]).split("_")[0])
			except speech_recognition.UnknownValueError:
				speech.speakMessage(_("Unable to recognize"))
				return
			except speech_recognition.RequestError:
				speech.speakMessage(_("Could not connect. Check your internet connection."))
				return
		string = ""
		for cat in self.categories:
			for com in self.gestures[cat]:
				string = "%s %s" % (string, com)
		textParser = parser.Parser(dictionary=string)
		candidates = []
		candidatesInfo = {}
		if "speechFilter" not in self.categories: self.categories.append("speechFilter")
		self.gestures["speechFilter"] = {}
		for cat in self.categories:
			for com in self.gestures[cat]:
				if cat == _("Recents") or cat == "speechFilter": continue
				s = textParser.match(recognizedText, com)
				if s>0:
					candidates.append((s, com))
					candidatesInfo[com] = self.gestures[cat][com]
		if candidates:
			if len(candidates)>1:
				speech.speakMessage(_("%d matches found for %s") % (len(candidates), recognizedText))
			self.gestures["speechFilter"] = candidatesInfo
			candidates.sort(reverse=True)
			self.catIndex = self.categories.index("speechFilter")
			self.commands = [i[1] for i in candidates]
			self.commandIndex = -1
			self.script_nextCommand(None)
		else:
			menuMessage(_("No matches found for %s") % recognizedText)
			self.commands = []
		self.flagFilter = True

	__CHGestures = {
	"kb:rightArrow": "nextCategory",
	"kb:leftArrow": "previousCategory",
	"kb:downArrow": "nextCommand",
	"kb:upArrow": "previousCommand",
	"kb:enter": "executeCommand",
	"kb:control+enter": "executeCommand",
	"kb:shift+enter": "executeCommand",
	"kb:numpadEnter": "executeCommand",
	"kb:control+numpadEnter": "executeCommand",
	"kb:shift+numpadEnter": "executeCommand",
	}

	__numpadGestures = {
	"kb:numpad6": "nextCategory",
	"kb:numpad4": "previousCategory",
	"kb:numpad2": "nextCommand",
	"kb:numpad8": "previousCommand",
	"kb:numpad5": "AnnounceGestures",
	"kb:numpadPlus": "executeCommand",
	"kb:numpadMinus": "executeCommand"
	}

	__gestures = {
	"kb:NVDA+H": "commandHelper"
	}

class Settings():
	warningMessageFlag = True

	def makeSettings(self, sizer):
		controlKeySizer = gui.guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		#TRANSLATORS: Checkbox to enable or disable helper launching by control key
		self.controlKeyEnabledCheckBox=wx.CheckBox(self, wx.NewId(), label=_("Control key launches the helper"))
		self.controlKeyEnabledCheckBox.Bind(wx.EVT_CHECKBOX, self.onControlKeyEnabledCheckBoxChanged)
		self.controlKeyEnabledCheckBox.SetValue(config.conf["commandHelper"]["controlKey"])
		self.warningMessage= _("With the control key activated, it is recommended to reduce the keyboard repetition speed. See more information in the addon documentation.")
		self.controlKeyEnabledCheckBox.SetToolTipString(self.warningMessage)
		controlKeySizer.addItem(self.controlKeyEnabledCheckBox,border=10,flag=wx.BOTTOM)
		self.windowSettingsButton = wx.Button(self, label=_("Windows keyboard settings"))
		self.windowSettingsButton.Bind(wx.EVT_BUTTON, self.onWindowsSettingsButton)
		self.windowSettingsButton.SetToolTipString(_("Open the Windows control panel to adjust keyboard parameters"))
		controlKeySizer.addItem(self.windowSettingsButton)
		sizer.Add(controlKeySizer.	sizer)
		otherKeysSizer = gui.guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		self.exitKeyRadioBox = wx.RadioBox(self,label=_("Key to leave the keyboard command layer"), choices=(_("escape"),_("backspace")))
		self.exitKeyRadioBox .SetSelection(("escape", "backspace").index(config.conf["commandHelper"]["exitKey"]))
		self.exitKeyRadioBox.SetToolTipString(_("Choose which key to use to exit the helper."))
		otherKeysSizer.addItem(self.exitKeyRadioBox)
		self.reportGestureKeyRadioBox = wx.RadioBox(self,label=_("Key to report the gesture assigned to a command"), choices=(_("F1"),_("F12")))
		self.reportGestureKeyRadioBox .SetStringSelection(config.conf["commandHelper"]["reportGestureKey"])
		self.reportGestureKeyRadioBox.SetToolTipString(_("Choose which key to use to announce the gesture assigned to the command."))
		otherKeysSizer.addItem(self.reportGestureKeyRadioBox)
		self.numpadKeysEnabledCheckBox=wx.CheckBox(self, wx.NewId(), label=_("Use numpad in the keyboard command layer"))
		self.numpadKeysEnabledCheckBox.SetValue(config.conf["commandHelper"]["numpad"])
		self.numpadKeysEnabledCheckBox.SetToolTipString(_("Use the numeric keyboard in the command layer."))
		otherKeysSizer.addItem(self.numpadKeysEnabledCheckBox)
		sizer.Add(otherKeysSizer.sizer)

	def onWindowsSettingsButton(self, evt):
		try:
			if hasattr(subprocess, "run"):
				subprocess.run(("control.exe", "keyboard"))
			else: # Old versions of NVDA
				subprocess.call(("control.exe", "keyboard"))
		except:
			raise
		else:
			pass
			#10 Bring the control panel window to the front
			# windowClassName = "#32770"

	def onControlKeyEnabledCheckBoxChanged(self, evt):
		if self.controlKeyEnabledCheckBox.GetValue() and self.warningMessageFlag:
			menuMessage(self.warningMessage)
			self.warningMessageFlag = False

class CommandHelperPanel(SettingsPanel, Settings):
	#TRANSLATORS: Settings panel title
	title=_("Command Helper")

	def makeSettings(self, sizer):
		Settings.makeSettings(self, sizer)

	def onSave(self):
		config.conf["commandHelper"]["controlKey"] = self.controlKeyEnabledCheckBox.GetValue()
		config.conf["commandHelper"]["exitKey"] = ("escape", "backspace")[self.exitKeyRadioBox.GetSelection()]
		config.conf["commandHelper"]["reportGestureKey"] = self.reportGestureKeyRadioBox.GetStringSelection()
		config.conf["commandHelper"]["numpad"] = self.numpadKeysEnabledCheckBox.GetValue()

class CommandHelperSettings(settingsDialogs.SettingsDialog, Settings):
	#TRANSLATORS: Settings dialog title
	title=_("Command Helper settings")

	def makeSettings(self, sizer):
		Settings.makeSettings(self, sizer)

	def postInit(self):
		self.controlKeyEnabledCheckBox.SetFocus()

	def onOk(self, evt):
		config.conf["commandHelper"]["controlKey"] = self.controlKeyEnabledCheckBox.GetValue()
		config.conf["commandHelper"]["exitKey"] = ("escape", "backspace")[self.exitKeyRadioBox.GetSelection()]
		config.conf["commandHelper"]["reportGestureKey"] = self.reportGestureKeyRadioBox.GetStringSelection()
		config.conf["commandHelper"]["numpad"] = self.numpadKeysEnabledCheckBox.GetValue()
		super(CommandHelperSettings, self).onOk(evt)
