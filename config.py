#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2020 Michael Schmidt-Korth
#
# GNU GPL v2.0 Licence. See https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#
from __future__ import unicode_literals
import sys
from workflow import Workflow, Workflow3, ICON_WARNING, web, PasswordNotFound

confNames = {'confApi': 'apiKey', 'confDue': 'dueDate', 'confList': 'list', 'confSpace': 'space', 'confTeam': 'workspace', 'confProject': 'folder', 'confNotification': 'notification', 'confDefaultTag': 'defaultTag', 'confHierarchyLimit': 'hierarchyLimit', 'confUser': 'userId'}


def main(wf):
	configuration()


def configuration():
	'''Provides list items to configure the workflow.

----------
	'''
	if len(wf.args):
		query = wf.args[0]
	else:
		query = None

	if not query:
		apiKeyValue = getConfigValue(confNames['confApi'])
		dueValue = getConfigValue(confNames['confDue'])
		listValue = getConfigValue(confNames['confList'])
		spaceValue = getConfigValue(confNames['confSpace'])
		teamValue = getConfigValue(confNames['confTeam'])
		projectValue = getConfigValue(confNames['confProject'])
		notificationValue = getConfigValue(confNames['confNotification'])
		if notificationValue == 'true':
			notificationValue = '✓'
		elif notificationValue == 'false':
			notificationValue = '✗'
		defaultTagValue = getConfigValue(confNames['confDefaultTag'])
		hierarchyLimitValue = getConfigValue(confNames['confHierarchyLimit'])

		wf3.add_item(title = 'Set API key' + (' (' + apiKeyValue + ')' if apiKeyValue else ''), subtitle = 'Your personal ClickUp API key/token.', valid = False, autocomplete = confNames['confApi'] + ' ')
		wf3.add_item(title = 'Set default due date' + (' (' + dueValue + ')' if dueValue else ''), subtitle = 'e.g. m30 (in 30 minutes), h2 (in two hours), d1 (in one day), w1 (in one week)', valid = False, autocomplete = confNames['confDue'] + ' ')
		wf3.add_item(title = 'Set ClickUp workspace' + (' (' + teamValue + ')' if teamValue else ''), subtitle = 'Workspace that defines which tasks can be searched', valid = False, autocomplete = confNames['confTeam'] + ' ')
		wf3.add_item(title = 'Set ClickUp space' + (' (' + spaceValue + ')' if spaceValue else ''), subtitle = 'Space that defines your available labels and priorities', valid = False, autocomplete = confNames['confSpace'] + ' ')
		wf3.add_item(title = 'Set ClickUp folder' + (' (' + projectValue + ')' if projectValue else ''), subtitle = 'Folder that which tasks can be searched. The Folder must be part of the workspace.', valid = False, autocomplete = confNames['confProject'] + ' ')
		wf3.add_item(title = 'Set default ClickUp list' + (' (' + listValue + ')' if listValue else ''), subtitle = 'List you want to add tasks to by default', valid = False, autocomplete = confNames['confList'] + ' ')
		wf3.add_item(title = 'Set Show Notification' + (' (' + notificationValue + ')' if notificationValue else ''), subtitle = 'Show notification after creating task?', valid = False, autocomplete = confNames['confNotification'] + ' ')
		wf3.add_item(title = 'Set default Tag' + (' (' + defaultTagValue + ')' if defaultTagValue else ''), subtitle = 'Tag that is added to all new tasks.', valid = False, autocomplete = confNames['confDefaultTag'] + ' ')
		wf3.add_item(title = 'Set hierarchy levels to limit search results' + (' (' + hierarchyLimitValue + ')' if hierarchyLimitValue else ''), subtitle = 'Levels to lmit search results by (list, folder, space).', valid = False, autocomplete = confNames['confHierarchyLimit'] + ' ')
		wf3.add_item(title = 'Validate Configuration', subtitle = 'Check if provided configuration parameters are valid.', valid = False, autocomplete = 'validate', icon = './settings.png')
		clearCache = wf3.add_item(title = 'Clear Cache', subtitle = 'Clear list of available labels and lists to be retrieved again.', valid = True, arg = 'cu:config cache', icon = './settings.png')
		clearCache.setvar('isSubmitted', 'true') # No secondary screen necessary
	elif query.startswith(confNames['confApi'] + ' '): # Check for suffix ' ' which we add automatically so user can type immediately
		userInput = query.replace(confNames['confApi'] + ' ', '')
		apiItem = wf3.add_item(title = 'Enter API key: ' + userInput, subtitle = 'Confirm to save to keychain?', valid = True, arg = 'cu:config ' + query)
		apiItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confDue'] + ' '):
		userInput = query.replace(confNames['confDue'] + ' ', '')
		dueType = userInput[:1]
		if dueType == 'm':
			dueType = 'minutes'
		elif dueType == 'h':
			dueType = 'hours'
		elif dueType == 'd':
			dueType = 'days'
		elif dueType == 'w':
			dueType = 'weeks'
		dueTime = userInput[1:]
		output = dueTime + ' ' + dueType
		if not dueType.isalpha() or not dueTime.isnumeric():
			output = '(Invalid input).'
		dueItem = wf3.add_item(title = 'Enter default due date (e.g. d2): ' + output, subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		dueItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confList'] + ' '):
		userInput = query.replace(confNames['confList'] + ' ', '')
		if not userInput.isnumeric() or len(userInput) != 7:
			userInput = '(Invalid input).'
		listItem = wf3.add_item(title = 'Enter default list (Id): ' + userInput, subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		listItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confSpace'] + ' '):
		userInput = query.replace(confNames['confSpace'] + ' ', '')
		if not userInput.isnumeric() or len(userInput) != 7:
			userInput = '(Invalid input).'
		spaceItem = wf3.add_item(title = 'Enter space (Id): ' + userInput, subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		spaceItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confTeam'] + ' '):
		userInput = query.replace(confNames['confTeam'] + ' ', '')
		if not userInput.isnumeric() or len(userInput) != 7:
			userInput = '(Invalid input).'
		teamItem = wf3.add_item(title = 'Enter workspace (Id): ' + userInput, subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		teamItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confProject'] + ' '):
		userInput = query.replace(confNames['confProject'] + ' ', '')
		if not userInput.isnumeric() or len(userInput) != 7:
			userInput = '(Invalid input).'
		projectItem = wf3.add_item(title = 'Enter folder (Id): ' + userInput, subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		projectItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confDefaultTag'] + ' '):
		userInput = query.replace(confNames['confDefaultTag'] + ' ', '')
		if ',' in userInput:
			userInput = '(Invalid input).'
		tagItem = wf3.add_item(title = 'Enter default tag: ' + userInput.lower(), subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		tagItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confHierarchyLimit'] + ' '):
		userInput = query.replace(confNames['confHierarchyLimit'] + ' ', '')
		for level in userInput.split(','):
			if level.strip() not in ('list', 'folder', 'space'):
				userInput = '(Invalid input).'
		tagItem = wf3.add_item(title = 'Enter hierarchy level(s): ' + userInput, subtitle = 'e.g. "list" or "list, folder". Save?', valid = True, arg = 'cu:config ' + query)
		tagItem.setvar('isSubmitted', 'true')
	elif query.startswith(confNames['confNotification'] + ' '):
		userInput = query.replace(confNames['confNotification'] + ' ', '')
		if not (userInput == 'true' or userInput == 'false'):
			userInput = '(Invalid input).'
		elif userInput == 'true':
			userInput = '✓'
		elif userInput == 'false':
			userInput = '✗'
		notificationItem = wf3.add_item(title = 'Enable notification (true, false): ' + userInput, subtitle = 'Save?', valid = True, arg = 'cu:config ' + query)
		notificationItem.setvar('isSubmitted', 'true')
	elif query.startswith('validate'): # No suffix ' ' needed, as user is not expected to provide any input.
		wf3.add_item(title = 'Checking API Key: ' + ('✓' if checkClickUpId('list', 'confList') else '✗'), valid = True, arg = 'cu:config ')
		wf3.add_item(title = 'Checking List Id: ' + ('✓' if checkClickUpId('list', 'confList') else '✗'), valid = True, arg = 'cu:config ')
		wf3.add_item(title = 'Checking Space Id: ' + ('✓' if checkClickUpId('space', 'confSpace') else '✗'), valid = True, arg = 'cu:config ')
		wf3.add_item(title = 'Checking Team Id: ' + ('✓' if checkClickUpId('team', 'confTeam') else '✗'), valid = True, arg = 'cu:config ')
		wf3.add_item(title = 'Checking Project Id: ' + ('✓' if checkClickUpId('folder', 'confProject') else '✗'), valid = True, arg = 'cu:config ')
	wf3.send_feedback()


def getConfigName(query):
	'''Returns the name of a configuration item from a user's query, e.g. extracts 'defaultTag' from 'cu:config defaultTag'.

----------
	@param str query: The user's input.
	'''
	wf = Workflow()
	log = wf.logger
	hasValue = query.split(' ') > 1
	if hasValue:
		# First element is our config name, whether there is a value or not
		return query.split(' ')[1]
	else:
		return query


def getUserInput(query, configName):
	'''Returns the value for a configuration item from a user's query, e.g. extracts 'to_sort' from 'cu:config defaultTag to_sort'.

----------
	@param str query: The user's input.
	@param str configName: The name of a configuration item-, e.g. 'dueDate'.
	'''
	return query.replace('cu:config ', '').replace(configName, '').strip()


def getConfigValue(configName):
	'''Returns the stored value for a configuration item Workflow settings or MacOS Keychain.

----------
	@param str configName: The name of a configuration item-, e.g. 'dueDate'.
	'''
	wf = Workflow()
	log = wf.logger
	if configName == confNames['confApi']:
		try:
			value = wf.get_password('clickUpAPI')
		except PasswordNotFound:
			value = None
			pass
	else:
		if configName in wf.settings:
			value = wf.settings[configName]
		else:
			value = None

	return value


def checkClickUpId(idType, configKey):
	'''Calls ClickUp API and returns whether call was successful or not..

----------
	@param str idType: The value to be used in the API URL.
	@param str configKey: The name of the setting to be retrieved.
	'''
	url = 'https://api.clickup.com/api/v2/' + idType + '/' + getConfigValue(confNames[configKey])
	headers = {}
	headers['Authorization'] = getConfigValue(confNames['confApi'])
	headers['Content-Type'] = 'application/json'

	# Use requests instead of Workflow.web, as web does not return the response in case of failure (only 401 NOT_AUTHORIZED, which is the same for API key failure or listId etc. failure)
	import requests
	request = requests.get(url, headers = headers)
	result = request.json()
	if 'ECODE' in result and result['ECODE'] == 'OAUTH_019': # Wrong API key
		return False
	elif 'ECODE' in result and result['ECODE'] == 'OAUTH_023': # Wrong ListId or team not authorized
		return False
	elif 'ECODE' in result and result['ECODE'] == 'OAUTH_027': # Wrong SpaceId/ProjectId or team not authorized
		return False
	elif idType != 'team' and 'id' in result and result['id'] == getConfigValue(confNames[configKey]) and 'name' in result and result['name'] != '':
		return True
	elif idType == 'team' and 'team' in result and 'id' in result['team'] and result['team']['id'] == getConfigValue(confNames[configKey]) and 'name' in result['team'] and result['team']['name'] != '':
		return True


if __name__ == "__main__":
	wf = Workflow()
	wf3 = Workflow3()
	log = wf.logger
	sys.exit(wf.run(main))
