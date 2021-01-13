	#-coding: UTF-8 -*-
"""
command helper- NVDA addon
This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright (C) 2021 Javi Dominguez <fjavids@gmail.com>
The keyboard command layer takes code from the Instant Translate addon by Alexy Sadovoy, Beqa Gozalishvili, Mesar Hameed, Alberto Buffolino and other NVDA contributors.

Provides a virtual menu where you can select any command to be executed without having to press its gesture.
"""

from keyboardHandler import KeyboardInputGesture
import addonHandler
import api
import appModuleHandler
# import collections
import globalPluginHandler
# import globalVars
# import os
# import pickle
import scriptHandler
import tones
import ui
import re
# import wx
import gui
import inputCore
import globalPlugins
import appModules
import globalCommands
# import speech
from functools import wraps

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

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = _("Command helper")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.toggling = False
		self.categories = []
		self.catIndex = 0
		self.commands = []
		self.commandIndex = 0
		self.recentCommands = {}

	def terminate(self):
		pass #1 store recents Upon leaving

	def getScript(self, gesture):
		#6 Allow the use of the navigation keys for braille displays
		if not self.toggling or re.match("br(\(.+\))?", gesture.normalizedIdentifiers[0]):
			return globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		if not script:
			script = finally_(self.script_exit, self.finish)
		return script

	def finish(self):
		self.toggling = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def script_commandsHelper(self, gesture):
		if self.toggling:
			self.script_exit(gesture)
			self.finish()
			return
		self.bindGestures(self.__CHGestures)
		self.toggling = True
		ui.message(_("Available commands"))
		#2 Say this help message only the first time, implement in config.
		ui.message(_("Use right and left arrows to navigate categories, up and down arrows to select a script and enter to run the selected."))
		try:
			self.gestures = inputCore.manager.getAllGestureMappings(obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors)
		except:
			ui.message("fallo al recuperar los scripts")
		self.categories = sorted(self.gestures)
		self.categories.remove(self.scriptCategory)
		if self.recentCommands:
			self.categories.insert(0, _("Recents"))
			self.gestures[_("Recents")] = self.recentCommands
		#3 Implement another category with a list of the most used commands in order of frequency.
		self.catIndex = -1
		self.script_nextCategory(None)
	#TRANSLATORS: message shown in Input gestures dialog for this script
	script_commandsHelper.__doc__ = _("Provides a virtual menu where you can select any command to be executed without having to press its gesture.")

	def script_nextCategory(self, gesture):
		self.catIndex = self.catIndex+1 if self.catIndex < len(self.categories)-1 else 0
		ui.message(self.categories[self.catIndex])
		self.commandIndex = -1
		self.commands = sorted(self.gestures[self.categories[self.catIndex]])

	def script_previousCategory(self, gesture):
		self.catIndex = self.catIndex -1 if self.catIndex > 0 else len(self.categories)-1
		ui.message(self.categories[self.catIndex])
		self.commandIndex = -1
		self.commands = sorted(self.gestures[self.categories[self.catIndex]])

	def script_nextCommand(self, gesture):
		self.commandIndex = self.commandIndex + 1 if self.commandIndex < len(self.commands)-1 else 0
		ui.message(self.commands[self.commandIndex])

	def script_previousCommand(self, gesture):
		self.commandIndex = self.commandIndex-1 if self.commandIndex > 0 else len(self.commands)-1
		ui.message(self.commands[self.commandIndex])

	def script_executeCommand(self, gesture):
		if self.commandIndex < 0:
			ui.message(self.categories[self.catIndex])
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
				return
		except:
			self.finish()
			raise
			return
		try:
			g = inputCore._getGestureClsForIdentifier(commandInfo.gestures[0])
		except:
			g = KeyboardInputGesture
		try:
			scriptHandler.executeScript(script, g)
		except:
			raise
		else:
			if self.commands[self.commandIndex] not in self.recentCommands:
				key = self.commands[self.commandIndex]
				if commandInfo.className == "AppModule":
					key = "%s: %s" % (self.categories[self.catIndex], key)
				self.recentCommands[key] = commandInfo
		#4 Implement support for scripts with getLastScriptRepeatCount
		self.finish()

	def script_exit(self, gesture):
		ui.message(_("Leaving the command hhelper"))

	__CHGestures = {
	"kb:rightArrow": "nextCategory",
	"kb:leftArrow": "previousCategory",
	"kb:downArrow": "nextCommand",
	"kb:upArrow": "previousCommand",
	"kb:enter": "executeCommand"
	#5 Implement F1 to announce the gesture corresponding to the selected command
	}

	__gestures = {
	"kb:NVDA+H": "commandsHelper"
	}
