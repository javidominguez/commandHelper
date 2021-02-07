#-coding: UTF-8 -*-
"""
command helper- NVDA addon
This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright (C) 2021 Javi Dominguez <fjavids@gmail.com>
The keyboard command layer takes code from the Instant Translate addon by Alexy Sadovoy, Beqa Gozalishvili, Mesar Hameed, Alberto Buffolino and other NVDA contributors.

Provides a virtual menu where you can select any command to be executed without having to press its gesture.
"""

from functools import wraps
from keyboardHandler import KeyboardInputGesture
from string import ascii_uppercase
import addonHandler
import api
import appModuleHandler
import appModules
import config
import globalCommands
import globalPluginHandler
import globalPlugins
import gui
import inputCore
import re
import scriptHandler
import speech
import time
import tones
import ui
import wx

# Settings compatibility with older versions of NVDA
from gui import settingsDialogs
try:
	from gui import NVDASettingsDialog
	from gui.settingsDialogs import SettingsPanel
except:
	SettingsPanel = object

confspec = {
	"controlKey":"boolean(default=True)"
}
config.conf.spec["commandHelper"]=confspec

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

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if hasattr(settingsDialogs, 'SettingsPanel'):
			NVDASettingsDialog.categoryClasses.append(CommandHelperPanel)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
			#TRANSLATORS: The configuration option in NVDA Preferences menu
			self.CommandHelperSettingsItem = self.prefsMenu.Append(wx.ID_ANY, u"Command Helper...", _("Command Helper settings"))
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

	def script_switchTrigger(self, gesture):
		if config.conf["commandHelper"]["controlKey"]:
			config.conf["commandHelper"]["controlKey"] = False
			ui.message("control key disabled")
		else:
			config.conf["commandHelper"]["controlKey"] = True
			ui.message("control key enabled")

	def onCommandHelperMenu(self, evt):
		# Compatibility with older versions of NVDA
		gui.mainFrame._popupSettingsDialog(CommandHelperSettings)

	def terminate(self):
		#1 store recents Upon leaving
		try:
			if hasattr(settingsDialogs, 'SettingsPanel'):
				NVDASettingsDialog.categoryClasses.remove(CommandHelperPanel)
			else:
				self.prefsMenu.RemoveItem(self.CommandHelperSettingsItem)
		except:
			pass

	def getScript(self, gesture):
		if self.toggling and gesture.identifiers in self.__trigger__.gestures and self.cancelSpeech:
			# Prevents the voice from being muted when launching the helper. Otherwise nothing is spoken if the activation key is being pressed and the user does not know if the helper has been launched.
			gesture.speechEffectWhenExecuted = None
		if config.conf["commandHelper"]["controlKey"] and not self.toggling and self.__trigger__(gesture):
			# Launch of the helper by repeating a modifier key (in this case control).
			gesture.speechEffectWhenExecuted = None
			script = self.script_commandsHelper(gesture)
		if not self.toggling or re.match("br(\(.+\))?", gesture.normalizedIdentifiers[0]):
			return globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		if not script:
			script = finally_(self.script_exit, self.finish) if "kb:escape" in gesture.identifiers else finally_(self.script_speechHelp, lambda: None) 
		return script

	def finish(self):
		self.toggling = False
		self.cancelSpeech = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def script_commandsHelper(self, gesture):
		if self.toggling:
			self.script_exit(gesture)
			self.finish()
			return
		self.bindGestures(self.__CHGestures)
		for c in ascii_uppercase:
			self.bindGesture("kb:"+c, "skipToCategory")
		self.toggling = True
		ui.message(_("Available commands"))
		if self.firstTime:
			self.script_speechHelp(None)
			self.firstTime = False
		try:
			self.gestures = inputCore.manager.getAllGestureMappings(obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors)
		except:
			ui.message(_("Failed to retrieve scripts."))
		self.categories = sorted(self.gestures)
		self.categories.remove(self.scriptCategory)
		if self.recentCommands:
			self.categories.insert(0, _("Recents"))
			self.gestures[_("Recents")] = self.recentCommands
		#3 Implement another category with a list of the most used commands in order of frequency.
		self.catIndex = -1
		self.script_nextCategory(None)
		self.cancelSpeech = True
	#TRANSLATORS: message shown in Input gestures dialog for this script
	script_commandsHelper.__doc__ = _("Provides a virtual menu where you can select any command to be executed without having to press its gesture.")

	def script_nextCategory(self, gesture):
		self.cancelSpeech = False
		self.catIndex = self.catIndex+1 if self.catIndex < len(self.categories)-1 else 0
		ui.message(self.categories[self.catIndex])
		self.commandIndex = -1
		self.commands = sorted(self.gestures[self.categories[self.catIndex]])

	def script_previousCategory(self, gesture):
		self.cancelSpeech = False
		self.catIndex = self.catIndex -1 if self.catIndex > 0 else len(self.categories)-1
		ui.message(self.categories[self.catIndex])
		self.commandIndex = -1
		self.commands = sorted(self.gestures[self.categories[self.catIndex]])

	def script_skipToCategory(self, gesture):
		self.cancelSpeech = False
		categories = (self.categories[self.catIndex+1:] if self.catIndex+1 < len(self.categories) else []) + (self.categories[:self.catIndex])
		try:
			self.catIndex = self.categories.index(filter(lambda i: i[0].lower() == gesture.mainKeyName, categories).__next__())-1
		except StopIteration:
			if self.categories[self.catIndex][0].lower() == gesture.mainKeyName:
				ui.message(self.categories[self.catIndex])
			else:
				tones.beep(200, 30)
		else:
			self.script_nextCategory(None)

	def script_nextCommand(self, gesture):
		self.cancelSpeech = False
		self.commandIndex = self.commandIndex + 1 if self.commandIndex < len(self.commands)-1 else 0
		ui.message(self.commands[self.commandIndex])

	def script_previousCommand(self, gesture):
		self.cancelSpeech = False
		self.commandIndex = self.commandIndex-1 if self.commandIndex > 0 else len(self.commands)-1
		ui.message(self.commands[self.commandIndex])

	def script_executeCommand(self, gesture):
		if self.commandIndex < 0:
			ui.message(_("Select a command using up or down arrows"))
			return
		commandInfo = self.gestures[self.categories[self.catIndex]][self.commands[self.commandIndex]]
		try:
			if commandInfo.className == "GlobalCommands":
				script = getattr(globalCommands.commands, "script_"+commandInfo.scriptName)
			elif commandInfo.className == "GlobalPlugin":
				i = [m.__module__ for m in globalPluginHandler .runningPlugins].index(commandInfo.moduleName)
				script = getattr(list(globalPluginHandler .runningPlugins)[i], "script_"+commandInfo.scriptName)
			elif commandInfo.className == "AppModule":
				try:
					script = getattr(api.getForegroundObject().appModule , "script_"+commandInfo.scriptName)
				except:
					ui.message(_("Can't run this script here"))
					return
			else:
				self.finish()
				raise RuntimeError("Failed to retrieve scripts. Not found in known modules.")
		except:
			self.finish()
			ui.message(_("Failed to retrieve scripts."))
			raise
		try:
			g = inputCore._getGestureClsForIdentifier(commandInfo.gestures[0])
		except:
			g = KeyboardInputGesture
		try:
			scriptHandler.executeScript(script, g)
		except:
			raise
		else:
			if gesture.modifierNames == ["shift"]:
				speech.cancelSpeech()
				scriptHandler.executeScript(script, g)
			elif gesture.modifierNames == ["control"]:
				speech.cancelSpeech()
				scriptHandler.executeScript(script, g)
				speech.cancelSpeech()
				scriptHandler.executeScript(script, g)
			if self.commands[self.commandIndex] not in self.recentCommands:
				key = self.commands[self.commandIndex]
				if commandInfo.className == "AppModule":
					key = "%s: %s" % (self.categories[self.catIndex], key)
				self.recentCommands[key] = commandInfo
		self.finish()

	def script_AnnounceGestures(self, gesture):
		self.cancelSpeech = False
		if self.commandIndex < 0:
			ui.message(_("Select a command using up or down arrows"))
			return
		commandInfo = self.gestures[self.categories[self.catIndex]][self.commands[self.commandIndex]]
		if commandInfo.gestures:
			try:
				ui.message(".\n".join([": ".join(KeyboardInputGesture.getDisplayTextForIdentifier(g)) for g in commandInfo.gestures]))
			except:
				ui.message("\n".join(commandInfo.gestures))
		else:
			ui.message(_("There is no gesture"))
		#9 Search for keyboard conflicts and announce them

	def script_speechHelp(self, gesture):
		ui.message(_("Use right and left arrows to navigate categories, up and down arrows to select a script and enter to run the selected. Escape to exit."))

	def script_exit(self, gesture):
		ui.message(_("Leaving the command hhelper"))

	__CHGestures = {
	"kb:rightArrow": "nextCategory",
	"kb:leftArrow": "previousCategory",
	"kb:downArrow": "nextCommand",
	"kb:upArrow": "previousCommand",
	"kb:enter": "executeCommand",
	"kb:control+enter": "executeCommand",
	"kb:shift+enter": "executeCommand",
	"kb:F1": "AnnounceGestures",
	"kb:F2": "switchTrigger"
	}

	__gestures = {
	"kb:NVDA+H": "commandsHelper"
	}

class CommandHelperSettings(settingsDialogs.SettingsDialog):
	#TRANSLATORS: Settings dialog title
	title=_("Command Helper settings")
	def makeSettings(self, sizer):
		#TRANSLATORS: Checkbox to enable or disable helper launching by control key
		self.controlKeyEnabled=wx.CheckBox(self, wx.NewId(), label=_("Control key launches the helper"))
		self.controlKeyEnabled.SetValue(config.conf["commandHelper"]["controlKey"])
		sizer.Add(self.controlKeyEnabled,border=10,flag=wx.BOTTOM)

	def postInit(self):
		self.controlKeyEnabled.SetFocus()

	def onOk(self, evt):
		config.conf["commandHelper"]["controlKey"] = self.controlKeyEnabled.GetValue()
		super(CommandHelperSettings, self).onOk(evt)

class CommandHelperPanel(SettingsPanel):
	#TRANSLATORS: Settings panel title
	title=_("Command Helper")
	def makeSettings(self, sizer):
		#TRANSLATORS: Checkbox to enable or disable helper launching by control key
		self.controlKeyEnabled=wx.CheckBox(self, wx.NewId(), label=_("Control key launches the helper"))
		self.controlKeyEnabled.SetValue(config.conf["commandHelper"]["controlKey"])
		sizer.Add(self.controlKeyEnabled,border=10,flag=wx.BOTTOM)

	def onSave(self):
		config.conf["commandHelper"]["controlKey"] = self.controlKeyEnabled.GetValue()

