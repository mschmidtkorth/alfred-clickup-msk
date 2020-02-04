#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2020 Michael Schmidt-Korth
#
# GNU GPL v2.0 Licence. See https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#
from __future__ import unicode_literals
import sys
import argparse
import os
from main import DEBUG, formatDate
from workflow import Workflow, Workflow3, ICON_WEB, ICON_CLOCK, ICON_WARNING, ICON_GROUP, web, PasswordNotFound
from config import getConfigName, getUserInput, confNames
from workflow.notify import notify


def main(wf):
	updateConfiguration()


def updateConfiguration():
	'''Updates Workflow Settings or MacOS Keychain with user provided value.

----------
	'''
	if len(wf.args):
		query = wf.args[0]
	else:
		query = None

	configName = getConfigName(query)
	userInput = getUserInput(query, configName)
	if DEBUG > 1:
		log.debug('Query: ' + str(query))
	if configName == confNames['confApi']:
		if DEBUG > 0:
			log.debug(' [ Updating ' + configName + ' ]')
		if DEBUG > 1:
			log.debug('Current value: ')
		try:
			wf.get_password('clickUpAPI')
		except PasswordNotFound:
			if DEBUG > 0:
				log.debug('No value stored.')
			pass
		if DEBUG > 1:
			log.debug('New value: ')
		if userInput.strip() == '':
			wf.delete_password('clickUpAPI')
		else:
			wf.save_password('clickUpAPI', userInput)
	elif query == 'cu:config cache':
		if DEBUG > 0:
			log.debug(' [ Clearing cache ]')
		if DEBUG > 0:
			log.debug('Current value: ')
			log.debug(wf.cached_data('availableLabels', None, max_age = 600))
			log.debug(wf.cached_data('availableLists', None, max_age = 600))
		wf.clear_cache(lambda f: 'availableLabels')
		wf.clear_cache(lambda f: 'availableLists')
		if DEBUG > 0:
			log.debug('New value: ')
			log.debug(wf.cached_data('availableLabels', None, max_age = 600))
			log.debug(wf.cached_data('availableLists', None, max_age = 600))
		notify('Cleared Cache', 'Lists and labels will be retrieved from ClickUp again.')
		#Notify cache cleared
	else:
		updateSetting(configName, userInput)


def updateSetting(configName, userInput):
	'''Updates specific Workflow Setting.

----------
	@param str configName: The name of a configuration item-, e.g. 'dueDate'.
	@param str userInput: The user's input (configuration value).
	'''
	if DEBUG > 0:
		log.debug(' [ Updating ' + configName + ' ]')
		log.debug('Current value: ')
		log.debug(wf.settings[configName] if configName in wf.settings else '')
	if userInput.strip() == '':
		if configName == 'notification':
			wf.settings[configName] = 'false'
		else:
			wf.settings.pop(configName)
	else:
		if configName == 'notification' and userInput != 'true':
			wf.settings[configName] = 'false'
		else:
			wf.settings[configName] = userInput.strip()
	wf.settings.save()
	if DEBUG > 0:
		log.debug('New value: ')
		log.debug(wf.settings[configName])


if __name__ == "__main__":
	wf = Workflow()
	wf3 = Workflow()
	log = wf.logger
	sys.exit(wf.run(main))
