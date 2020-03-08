#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2020 Michael Schmidt-Korth
#
# GNU GPL v2.0 Licence. See https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import os
import emoji
import re
from workflow import Workflow, Workflow3, ICON_CLOCK, ICON_WARNING, ICON_GROUP, ICON_SYNC, web, util # Alfred-Workflow
from workflow.util import set_config, unset_config
from workflow.update import Version
from config import confNames, getConfigValue

DEBUG = 2 # 0 = Off (no output), 1 = Some, 2 = All

UPDATE_SETTINGS = {
	'github_slug': 'mschmidtkorth/alfred-clickup-msk',
	#'version': __version__,
	'frequency': 3
}
query = ''
availableTags = None
availableLists = None
availableListsIdName = {}
availableListsNameId = {} # Used to get Id from user's input, when we 'lost' the Id/context
hasFoundMatch = False
isDoNotDisplayCreate = False
isCustomTagEntered = False


def retrieveLabelsFromAPI():
	'''Retrieves list of available Labels from ClickUp.
	'''
	if DEBUG > 0:
		log.debug('[ Calling API to receive labels ]')
	url = 'https://api.clickup.com/api/v2/space/' + getConfigValue(confNames['confSpace']) + '/tag'
	params = None
	headers = {}
	headers['Authorization'] = getConfigValue(confNames['confApi'])
	headers['Content-Type'] = 'application/json'
	headers['format'] = 'json'
	try:
		request = web.get(url, params, headers)
		request.raise_for_status()
	except:
		log.debug('Error on HTTP request.')
		wf3.add_item(title = 'Error connecting to ClickUp.', subtitle = 'Open configuration to check your parameters?', valid = True, arg = 'cu:config ', icon = 'error.png')
		wf3.send_feedback()
		exit()
	result = request.json()
	if DEBUG > 1:
		log.debug('Response: ' + str(result))
	
	if 'tags' in result:
		return result['tags']
	else:
		return None


def getLabels(input):
	'''Returns list of available Labels from ClickUp and caches them. Initiates `retrieveLabelsFromAPI()` if cache has been cleared.

----------
	@param str input: The user's input for a label.
	'''
	if DEBUG > 0:
		log.debug('[ Displaying labels ] - input: ' + input)
	availableTags = wf.cached_data('availableLabels', retrieveLabelsFromAPI, max_age = 600) # Get data from cache or retrieve from API
	
	global query
	global hasFoundMatch
	# If user types 'test #123 ', we know that the tag has already been chosen - no need to display
	isUserEndedInput = query[-1] == ' '
	if not isUserEndedInput:
		allLabelTitles = []
		for tag in availableTags:
			allLabelTitles.append(tag['name'])
		filteredItems = wf.filter(input, allLabelTitles)
		for item in filteredItems:
			hasFoundMatch = True
			wf3.add_item(
				title = item,
				valid = False,
				# If the user already added input, we need to remove it and replace it with the value from the selected item (otherwise, e.g. #ci becomes #cicid when selecting "cid")
				#arg = 'cu ' + query.replace(input, '') + item + ' ',
				autocomplete = query.replace(input, '') + item + ' ',
				icon = './label.png'
			)
	if not hasFoundMatch:
		global isCustomTagEntered
		isCustomTagEntered = True
	
	if hasFoundMatch:
		wf3.send_feedback()


def getPriorities(input):
	'''Returns list of available Priorities.

----------
	@param str input: The user's input for a Label.
	'''
	if DEBUG > 0:
		log.debug('[ Collecting priorities - input: ' + input + ']')
	
	global query
	global hasFoundMatch
	dicPriorities = {1: 'Urgent', 2: 'High', 3: 'Normal', 4: 'Low'} # Priorities cannot be customized by user. -1 = None, but must not be selectable.
	
	isUserEndedInput = query[-1] == ' '
	if not isUserEndedInput:
		#for priority in dicPriorities:
		# Escape [ from search, otherwise RegEx error
		#if len(input) == 0 or re.match(r'^' + input.replace('[', '\['), str(dicPriorities[priority]), re.IGNORECASE) or re.match(r'^' + input.replace('[', '\['), str(priority)):
		allLabelTitles = []
		for priority in dicPriorities:
			allLabelTitles.append(str(priority) + ' ' + dicPriorities[priority])
		filteredItems = wf.filter(input, allLabelTitles)
		for item in filteredItems:
			hasFoundMatch = True
			wf3.add_item(
				title = item.split(' ')[1],
				valid = False,
				#arg = 'cu ' + query.replace(input, '') + str(priority) + ' ',
				autocomplete = query.replace(input, '') + item.split(' ')[0] + ' ',
				icon = './prio' + item.split(' ')[0] + '.png'
			)
	if hasFoundMatch:
		wf3.send_feedback()


def retrieveListsFromAPI():
	''''Retrieves list of available Lists from ClickUp.
	'''
	if DEBUG > 0:
		log.debug('[ Calling API to receive lists ]')
	url = 'https://api.clickup.com/api/v2/team/' + getConfigValue(confNames['confTeam']) + '/list'
	params = {}
	params['archived'] = False
	headers = {}
	headers['Authorization'] = getConfigValue(confNames['confApi'])
	headers['Content-Type'] = 'application/json'
	try:
		request = web.get(url, params, headers)
		request.raise_for_status()
	except:
		log.debug('Error on HTTP request')
		wf3.add_item(title = 'Error connecting to ClickUp.', subtitle = 'Open configuration to check your parameters?', valid = True, arg = 'cu:config ', icon = 'error.png')
		wf3.send_feedback()
		exit()
	result = request.json()
	
	if DEBUG > 1:
		log.debug('Response: ' + str(result))
	
	return result['lists']


def getLists(input, doPrintResults):
	'''Returns list of available Lists from ClickUp and caches them. Initiates `retrieveListsFromAPI()` if cache has been cleared.

----------
	@param str input: The user's input for a List.
	@param bool doPrintResults: Whether to generate list items.
	'''
	if DEBUG > 0:
		log.debug('[ Displaying lists (' + str(doPrintResults) + ') ] - input: ' + input)
	global query
	global availableLists
	availableLists = wf.cached_data('availableLists', retrieveListsFromAPI, max_age = 7200)
	
	isUserEndedInput = query[-1] == ' '
	if not isUserEndedInput and doPrintResults:
		allListTitles = []
		for singleList in availableLists:
			# Limit results on SpaceId - as getting *all* lists for the Team is overkill and does not make much sense as the user already specified a Space in Alfred workflow variables.
			if singleList['space']['id'] == getConfigValue(confNames['confSpace']):
				# Store association of name to Id, as Id needs to be passed to API
				# Hidden lists are outside of a Folder, only connected to a Space
				folderName = '[' + singleList['folder']['name'] + '] ' if (singleList['folder']['name'] != 'hidden') else ''
				global availableListsIdName
				availableListsIdName[singleList['id']] = folderName + singleList['name']
				availableListsNameId[folderName + singleList['name']] = singleList['id']
				allListTitles.append(folderName + singleList['name'])
		filteredItems = wf.filter(input, allListTitles)
		global hasFoundMatch
		for item in filteredItems:
			hasFoundMatch = True
			wf3.add_item(
				title = item,
				valid = False,
				#arg = 'cu ' + query.replace(input, '') + item + ' ',
				autocomplete = query.replace(input, '') + item + ' ',
				icon = './note.png'
			)
		if doPrintResults and hasFoundMatch:
			wf3.send_feedback()
	else: # Even when nothing is entered, we need to fill our dictionaries.
		for singleList in availableLists:
			if singleList['space']['id'] == getConfigValue(confNames['confSpace']):
				folderName = '[' + singleList['folder']['name'] + '] ' if (singleList['folder']['name'] != 'hidden') else ''
				availableListsIdName[singleList['id']] = folderName + singleList['name']
				availableListsNameId[folderName + singleList['name']] = singleList['id']


def firstRun(wf3):
	'''Checks whether this is the first time the user executed the workflow. If so, asks them to configure.

----------
	@param Workflow wf3: Workflow 3 object.
	'''
	if DEBUG > 0:
		log.debug('[ firstRun() ]')
	if wf3.first_run and not isinstance(wf3.last_version_run, Version):
		log.debug('First execution of workflow.')
		wf3.add_item(title = 'Welcome to your ClickUp workflow!', subtitle = 'Let\'s set it up?', valid = True, arg = 'cu:config ')
		wf3.send_feedback()
		exit()


def checkConfig(wf3):
	'''Checks whether the required configuration parameters have been set. If not, asks the user to configure.

----------
	@param Workflow wf3: Workflow 3 object.
	'''
	if DEBUG > 0:
		log.debug('[ checkConfig() ]')
	if getConfigValue(confNames['confApi']) == None or getConfigValue(confNames['confList']) == None or getConfigValue(confNames['confSpace']) == None or getConfigValue(confNames['confTeam']) == None or getConfigValue(confNames['confProject']) == None:
		log.debug('Missing essential variables')
		wf3.add_item(title = 'We are missing some settings for ClickUp.', subtitle = 'Let\'s set it up?', valid = True, arg = 'cu:config ', icon = ICON_WARNING)
		wf3.send_feedback()
		exit()


def checkUpdates(wf3):
	'''Checks whether an update is available for the workflow, downloads and installs it.

----------
	@param Workflow wf3: Workflow 3 object.
	'''
	if DEBUG > 0:
		log.debug('[ checkUpdates() ]')
	if wf.update_available:
		global query
		if DEBUG > 0:
			log.debug('Found workflow update.')
		updateItem = wf3.add_item(title = 'New version available for your ClickUp workflow!', subtitle = 'Press "Enter" to install the update.', autocomplete = 'workflow:update', icon = ICON_SYNC)
		
		if query == 'workflow:update':
			if DEBUG > 0:
				log.debug('Updating workflow.')
			wf.start_update()


def addCreateTaskItem(inputName, inputContent, inputDue, inputPriority, inputTags, inputList):
	'''Displays a 'Create Task?' list item.

----------
	@param str inputName: The user's input for the task title.
	@param str inputContent: The user's input for the task decsription.
	@param str inputDue: The user's input for the task due date.
	@param str inputPriority: The user's input for the task priority.
	@param str inputTags: The user's input for the task tags.
	@param str inputList: The user's input for the task list.
	'''
	if DEBUG > 0:
		log.debug('[ addCreateTaskItem() ]')
	
	import json
	inputParameters = {'inputName': inputName, 'inputContent': inputContent, 'inputDue': str(inputDue), 'inputPriority': inputPriority, 'inputTags': inputTags}
	inputParameters['inputList'] = None
	if inputList != getConfigValue(confNames['confList']): # Non-default list specified
		if inputList in availableListsIdName:
			# For display: Use Name. For passing to Create Task: Use Id.
			inputParameters['inputList'] = {availableListsIdName[inputList]: inputList} # ListId : ListName
	
	outputTaskValues = json.dumps(inputParameters)
	createTaskItem = wf3.add_item(
		title = 'Create task "' + str(inputName).strip() + '"?',
		subtitle = formatNotificationText(inputContent, inputDue, inputTags, inputPriority, inputParameters['inputList']),
		valid = True,
		arg = outputTaskValues # Passed to Run Script as JSON - which will use it to call the ClickUp API.
	)
	createTaskItem.setvar('isSubmitted', 'true')


def formatNotificationText(inputContent, inputDue, inputTags, inputPriority, availableListsIdName, lineBreaks = False):
	'''Generates text to display via notification or list item.

----------
	@param str inputContent: The user's input for the task decsription.
	@param str inputDue: The user's input for the task due date.
	@param str inputTags: The user's input for the task tags.
	@param str inputPriority: The user's input for the task priority.
	@param list availableListsIdName: Assignment of List Ids to List Names.
	@param bool lineBreaks: Whether to include a line break after the description.
	'''
	if not 'log' in locals():
		wf = Workflow(update_settings = UPDATE_SETTINGS)
		log = wf.logger
	
	if DEBUG > 0:
		log.debug('[ formatNotificationText() ] ')
	notificationPriority, notificationTag, notificationBracketOpen, notificationBracketClose, notificationSeparator = '', '', '', '', ''
	if inputPriority:
		notificationPriority = emoji.emojize(':exclamation_mark:') + str(inputPriority)
	hasTags = len(inputTags) > 1
	if hasTags: # If default tag is defined, it is always included
		notificationTag = emoji.emojize(':label:')
		for i in range(1, len(inputTags)): # Ignore default tag
			if i == len(inputTags) - 1:
				notificationTag += inputTags[i]
			else:
				notificationTag += inputTags[i] + ', '
	if inputPriority != None or hasTags:
		notificationBracketOpen = ' ('
		notificationBracketClose = ')'
	if inputPriority != None and hasTags:
		notificationSeparator = ', '
	if inputDue and inputDue != 'None':
		inputDue = emoji.emojize(':calendar:') + formatDate(inputDue)
	else:
		inputDue = ''
	
	br = ''
	if lineBreaks:
		br = '\n'
	
	return inputContent + ('  ' if inputContent != '' else '') + br + inputDue + notificationBracketOpen + notificationPriority + notificationSeparator + notificationTag + ' ' + (emoji.emojize(':spiral_notepad:') + str(next(iter(availableListsIdName))) if availableListsIdName != None else '') + notificationBracketClose


def formatDate(dateTime):
	'''Format date time value and return as String.

----------
	@param datetime dateTime: The date time value.
	'''
	if not 'log' in locals():
		wf = Workflow(update_settings = UPDATE_SETTINGS)
		log = wf.logger
	if DEBUG > 0:
		log.debug('[ formatDate() ] ')
	return dateTime.strftime('%Y-%m-%d %H:%M')


def getNameFromInput(query):
	'''Retrieves the task title from the user's input.

----------
	@param str query: The user's input.
	'''
	if DEBUG > 0:
		log.debug('[ getNameFromInput() ] ')
	inputName = query.split(":", 1)[0].split(" #", 1)[0].split(" @", 1)[0].split(" !", 1)[0].split(" +", 1)[0].strip() # If it cannot be split, first element will be complete string
	if DEBUG > 1:
		log.debug('inputName: ' + str(inputName))
	
	return inputName


def getContentFromInput(query):
	'''Retrieves the task description from the user's input.

----------
	@param str query: The user's input.
	'''
	if DEBUG > 0:
		log.debug('[ getContentFromInput() ] ')
	inputContent = ''
	hasContent = len(query.split(':')) > 1
	if hasContent:
		inputContent = query.split(':', 1)[1].split(' #', 1)[0].split(' @', 1)[0].split(' !', 1)[0].split(" +", 1)[0].strip().decode('utf-8') # Avoid adding #myTag, @due, !priority to the content text
	if DEBUG > 1:
		log.debug('inputContent: ' + str(inputContent))
	
	return inputContent


def getTagsFromInput(query):
	'''Retrieves the task tags from the user's input.

----------
	@param str query: The user's input.
	'''
	if DEBUG > 0:
		log.debug('[ getTagsFromInput() ] ')
	inputTags = []
	if getConfigValue(confNames['confDefaultTag']):
		inputTags.append(getConfigValue(confNames['confDefaultTag']))
	
	# Find first occurrence of '#' - from here, retrieve labels.
	if query.find(' #') > -1: # Char was found
		# From first occurrence until end of input # [u'', u'123 ', u'456']
		for tag in query[query.find(' #'):].split(' #'):
			# First element when splitting is always going to be empty ('') - as this is the left side of the first '#' which is not relevant for the tag
			if tag != '' and tag not in inputTags: # Do not add duplicate labels:
				tagValue = tag.split(':', 2)[0].split(' @', 2)[0].split(' !', 2)[0].split(" +", 1)[0].strip().replace(' ', ' ')
				inputTags.append(tagValue.strip())
	if DEBUG > 1:
		log.debug('inputTags: ' + str(inputTags))
	
	return inputTags


def nextWeekday(d, weekday):
	'''Returns date of next weekday - either in current week, or in next week if already passed.

----------
	@param datetime d: A datetime object to which the result is added.
	@param int weekday: Number of the day in a week (0 = Monday, 1 = Tuesday etc.)
	'''
	days_ahead = weekday - d.weekday()
	if days_ahead <= 0: # Target day already happened this week
		days_ahead += 7
	
	return d + datetime.timedelta(days_ahead)


def getDueFromInput(query):
	'''Retrieves the task due date from the user's input.

----------
	@param str query: The user's input.
	'''
	
	if DEBUG > 0:
		log.debug('[ getDueFromInput() ] ')
	
	naturalLanguageWeekdays = {'mon': 0, 'monday': 0, 'tue': 1, 'tuesday': 1, 'wed': 2, 'wednesday': 2, 'thu': 3, 'thursday': 3, 'fri': 4, 'friday': 4, 'sat': 5, 'saturday': 5, 'sun': 6, 'sunday': 6}
	naturalLanguageRelativeDays = {'tod': 0, 'today': 0, 'tom': 1, 'tomorrow': 1}
	# 'in X days/weeks': Handled via dX/wx
	# 'next mon': Same as 'mon'
	
	inputMinHourDayWeek = ''
	# passedDue = ''
	isUseDefault = True
	isNoDueDate = False
	hasTime = len(query.split(' @', 2)) > 1
	hasDefault = (getConfigValue(confNames['confDue']) is not None and getConfigValue(confNames['confDue']) != '')
	naturalValue = ''
	if hasTime or hasDefault:
		inputDue = 0
		hasTime = len(query.split(' @')) > 1
		if hasTime:
			hasValue = len(query.split(' @')[1]) > 0 and query.split(' @')[1][0] != ' ' # [1] = First element in array (h3 (+ any text after)). [0] = First character of array (h). Ensure that first character is not a space, otherwise "cu Test @ someText" will be true
			timeValue = query.split(' @')[1][1:].split(' ')[0] # cu Task @h2 some other text -> h2
		
		if hasTime and hasValue:
			isUseDefault = False
			# if DEBUG > 1:
			# 	passedDue = getConfigValue(confNames['confDue']) if isUseDefault else query.split(' @')[1][1:].split(' ')[0]
			# 	log.debug('passedDue: ' + str(passedDue))
		
		inputMinHourDayWeek = ''
		if (isUseDefault and getConfigValue(confNames['confDue'])):
			inputMinHourDayWeek = getConfigValue(confNames['confDue'])[0]
		elif len(query.split(' @', 2)[1]) > 0:
			value = query.split(' @', 2)[1]
			if value.split(' ')[0] in naturalLanguageWeekdays.keys(): # Get date of next x-day
				naturalValue = nextWeekday(datetime.datetime.today(), naturalLanguageWeekdays[value.split(' ')[0].lower()])
				if DEBUG > 1:
					log.debug('Received weekday: ' + str(naturalValue))
				log.debug(nextWeekday(datetime.datetime.today(), naturalLanguageWeekdays[value.split(' ')[0].lower()]))
			elif value.split(' ')[0] in naturalLanguageRelativeDays.keys(): # Get date of today/tomorrow
				naturalValue = datetime.datetime.today() + datetime.timedelta(naturalLanguageRelativeDays[value.split(' ')[0].lower()])
				if DEBUG > 1:
					log.debug('Received relative date: ' + str(naturalValue))
				log.debug(datetime.datetime.today() + datetime.timedelta(naturalLanguageRelativeDays[value.split(' ')[0].lower()]))
			elif re.search(r'\d{4}-\d?\d-\d?\d', value) or re.search(r'(:2[0-3]|[01]?[0-9])\.[0-5]?[0-9](\.[0-5]?[0-9])?', value): # Get date or date-time as specified
				date = ''
				dateTime = ''
				if len(sys.argv) == 2 or len(sys.argv) == 3:
					date = re.search(r'\d{4}-\d?\d-\d?\d', value) # Matches 2000-01-01
				if len(sys.argv) == 3:
					dateTime = re.search(r'(:2[0-3]|[01]?[0-9])\.[0-5]?[0-9](\.[0-5]?[0-9])?', value) # Matches 12:00:00 or 12:00 # TODO: Split on Space?
				if date:
					if DEBUG > 1:
						log.debug('Found date: ' + str(date.group()))
					try:
						naturalValue = datetime.datetime.strptime(date.group() + 'T' + datetime.datetime.now().strftime("%H.%M.%S"), '%Y-%m-%dT%H.%M.%S') # Convert string 'date + current time' to dateTime.
					except ValueError: # Incorrect format, e.g. 2020-01-1
						naturalValue = ''
						pass
				if dateTime:
					if DEBUG > 1:
						log.debug('Found date time: ' + str(dateTime.group()))
					theDate = str(datetime.datetime.today().strftime('%Y-%m-%d')) if not date else date.group()
					if len(dateTime.group()) == 5 or len(dateTime.group()) == 8: # 12:00, 12:00:00
						try:
							time = dateTime.group() if len(dateTime.group()) != 8 else dateTime.group()[:5]
							naturalValue = datetime.datetime.strptime(theDate + 'T' + time, '%Y-%m-%dT%H.%M')
						except ValueError: # Incorrect format, e.g. used : instead of . for hour.min.sec
							naturalValue = ''
							pass
				
				# Note: If only time given, e.g. @20:00:00 - then I need to add the current date.
			else:
				inputMinHourDayWeek = value[0] # First character: m, h, d, w
				if DEBUG > 1:
					log.debug('inputMinHourDayWeek: ' + str(inputMinHourDayWeek))
		if not naturalValue:
			isDefaultInteger = getConfigValue(confNames['confDue']) and int(getConfigValue(confNames['confDue'])[1:])
			if hasTime:
				isInputInteger = timeValue.isnumeric() #query.split(' @', 2)[1].strip()[1:].isnumeric()
			if isUseDefault and isDefaultInteger:
				inputDue = int(getConfigValue(confNames['confDue'])[1:])
			elif isInputInteger:
				inputDue = int(timeValue) #int(query.split(' @', 2)[1].strip()[1:])
			else: # Invalid input
				inputDue = 0 # No longer default of 2h - can now be set via configuration if desired, if not no due date will be added
				isNoDueDate = True
				inputMinHourDayWeek = 'h'
			
			if inputMinHourDayWeek == 'm':
				inputDue *= 1000 * 60
			elif inputMinHourDayWeek == 'h':
				inputDue *= 1000 * 60 * 60
			elif inputMinHourDayWeek == 'd':
				inputDue *= 1000 * 60 * 60 * 24
			elif inputMinHourDayWeek == 'w':
				inputDue *= 1000 * 60 * 60 * 24 * 7
	else:
		inputDue = 0 # No longer default of 2h if no other value specified and no default context variable specified - can now be set via configuration if desired, if not no due date will be added
		isNoDueDate = True
	if not naturalValue:
		inputDue = datetime.datetime.now() + datetime.timedelta(milliseconds = inputDue) # Add to whatever buffer has been selected
	else:
		inputDue = naturalValue
	if DEBUG > 1:
		log.debug('inputDue: ' + str(inputDue))
	
	if isNoDueDate:
		return None
	else:
		return inputDue


def getListFromInput(query):
	'''Retrieves the task list from the user's input.

----------
	@param str query: The user's input.
	'''
	if DEBUG > 0:
		log.debug('[ getListFromInput() ] ')
	inputList = getConfigValue(confNames['confList'])
	global availableListsIdName
	hasList = len(query.split('+')) > 1
	if hasList:
		# If user is typing, the current list name - e.g. 'tes' for 'cu X +tes' - will not match anything in the dict. Until we found a complete match, do not attempt to update inputList
		listName = query.split('+', 1)[1].split(' #', 1)[0].split(' @', 1)[0].split(' !', 1)[0].strip()
		if listName in availableListsNameId:
			inputList = availableListsNameId[query.split('+', 1)[1].split(' #', 1)[0].split(' @', 1)[0].split(' !', 1)[0].strip()]
	if DEBUG > 1:
		log.debug('inputList: ' + str(inputList))
		log.debug(availableListsIdName)
	
	return inputList


def getPriorityFromInput(query):
	'''Retrieves the task priority from the user's input.

----------
	@param str query: The user's input.
	'''
	if DEBUG > 0:
		log.debug('[ getPriorityFromInput() ] ')
	inputPriority = None
	hasPriority = len(query.split(' !', 2)) > 1
	if hasPriority:
		isInputInteger = query.split(' !', 2)[1][:1].isnumeric()
	if hasPriority and isInputInteger: # Priority is of only 1 character, so we can receive the 1st character of the second element. As such, any text after is ignored.
		inputPriority = int(query.split(' !', 2)[1].strip()[:1])
	if DEBUG > 1:
		log.debug('inputPriority: ' + str(inputPriority))
	
	return inputPriority


def main(wf):
	global query
	# Check if there is a user input
	if len(wf.args):
		query = wf.args[0]
	else:
		query = None
	if DEBUG > 0:
		log.debug('[ main() ] - ' + query)
	
	firstRun(wf3)
	checkConfig(wf3)
	
	# Evaluate input for description/content
	global isDoNotDisplayCreate
	if len(query.split(' :')) > 3: # Check if user is trying to add a second description - not possible
		if DEBUG > 0:
			log.debug('Attempted to define additional description.')
		isDoNotDisplayCreate = True
		wf3.add_item(
			title = 'Description already defined.',
			subtitle = 'Please remove the second \':\' defining a content.',
			valid = False,
			# arg = 'cu ' + query + ' ',
			autocomplete = query + ' ',
			icon = ICON_WARNING
		)
		wf3.send_feedback()
	
	# Evaluate input for labels
	for idx, labelIdentifier in enumerate(query.split(' #')):
		hasAtLeastOneLabel = len(query.split(' #')) > 1
		isLabelLastOne = idx == len(query.split(' #')) - 1
		if hasAtLeastOneLabel and isLabelLastOne:
			posFollowUpIdentifier = 0
			posFollowUpList = labelIdentifier.find(' +')
			posFollowUpTPriority = labelIdentifier.find(' !')
			# Either + or ! may come directly after a #, so we only need to consider one
			if posFollowUpList > -1: # Found match
				posFollowUpIdentifier = posFollowUpList
			elif posFollowUpTPriority > -1: # Found match
				posFollowUpIdentifier = posFollowUpTPriority
			if posFollowUpIdentifier:
				labelIdentifier = labelIdentifier[0:posFollowUpIdentifier] # Extract text from # until +/!
				log.debug(labelIdentifier[0:posFollowUpIdentifier])
			else: # End of string
				labelIdentifier = labelIdentifier[0:len(labelIdentifier)]
				log.debug(labelIdentifier[0:len(labelIdentifier)])
			if DEBUG > 1:
				log.debug('labelIdentifier: ' + str(labelIdentifier))
				log.debug(labelIdentifier)
			if not posFollowUpIdentifier: # Only if tag is at the end of input, not if followed by other command-characters such as +/!
				getLabels(labelIdentifier)
	
	# Evaluate input for priorities
	if len(query.split(' !')) < 3: # Check if user is trying to add a second priority - not possible
		for idx, priorityIdentifier in enumerate(query.split(' !')): # No priority yet entered, suggest.
			posFollowUpIdentifier = 0
			hasAtLeastOnePriority = len(query.split(' !')) > 1
			if hasAtLeastOnePriority:
				posFollowUpTag = priorityIdentifier.find(' #') # If a tag follows after a list definition, treat it as end of string.
				if posFollowUpTag > -1:
					posFollowUpIdentifier = posFollowUpTag
				if posFollowUpIdentifier:
					priorityIdentifier = priorityIdentifier[0:posFollowUpIdentifier]
					log.debug(priorityIdentifier[0:posFollowUpIdentifier])
				if not posFollowUpIdentifier:
					getPriorities(priorityIdentifier)
	else:
		if DEBUG > 0:
			log.debug('Attempted to define additional priority.')
		isDoNotDisplayCreate = True
		wf3.add_item(
			title = 'Priority already defined.',
			subtitle = 'Please remove the second \'!\' defining a priority.',
			valid = False,
			#arg = 'cu ' + query + ' ',
			autocomplete = query + ' ',
			icon = ICON_WARNING
		)
		wf3.send_feedback()
	
	# Evaluate input for lists
	if len(query.split(' +')) < 3:
		for idx, listIdentifier in enumerate(query.split(' +')): # No list yet entered, suggest.
			if idx > 0: # Start from 1, as 0 is everything to the left of +
				posFollowUpIdentifier = 0
				# Lists are different from Labels/Priorities, as they might have spaces. To prevent calling getLists() if the user entered e.g. 'cu Title +My List With Spaces #x' to select label x - as calling getLists() would add secondary JSON output -, we stop when we find #/!.
				# If +List is followed by either #Tag or !Priority, only extract list name from + until #/!.
				hasAtLeastOneList = len(query.split(' +')) > 1
				if hasAtLeastOneList:
					posFollowUpTag = listIdentifier.find(' #')
					posFollowUpTPriority = listIdentifier.find(' !')
					# Either # or ! may come directly after a !, so we only need to consider one
					if DEBUG > 1:
						log.debug('listIdentifier:')
					if posFollowUpTag > -1: # Found match
						posFollowUpIdentifier = posFollowUpTag
					elif posFollowUpTPriority > -1:
						posFollowUpIdentifier = posFollowUpTPriority
					if posFollowUpIdentifier:
						listIdentifier = listIdentifier[0:posFollowUpIdentifier] # Extract text from + until #/!
						log.debug(listIdentifier[0:posFollowUpIdentifier])
					else:
						listIdentifier = listIdentifier[0:len(listIdentifier)]
						log.debug(listIdentifier[0:len(listIdentifier)])
				if not posFollowUpIdentifier and hasAtLeastOneList:
					getLists(listIdentifier, True)
				elif hasAtLeastOneList: # Get lists from API or from cache, to update availableistsIdName/availableListsNameId for passing the Id to createTask.py. Do not generate list items. As the user can only select a single list, this is not an issue of unnecessary API calls - if the user attempts to add another one, we will not callout and instead fall back to the default list. Lists will not be displayed.
					getLists(listIdentifier, False)
	else:
		if DEBUG > 0:
			log.debug('Attempted to define additional list.')
		isDoNotDisplayCreate = True
		wf3.add_item(
			title = 'List already defined.',
			subtitle = 'Please remove the second \'+\' defining a list.',
			valid = False,
			# arg = 'cu ' + query + ' ',
			autocomplete = query + ' ',
			icon = ICON_WARNING
		)
		wf3.send_feedback()
	
	# Extract different parts from input
	inputName = getNameFromInput(query)
	inputContent = getContentFromInput(query)
	inputTags = getTagsFromInput(query)
	inputDue = getDueFromInput(query)
	inputList = getListFromInput(query)
	inputPriority = getPriorityFromInput(query)
	
	# Show 'Create Task' if user has completed their input - and no previous list item has been generated (JSON garbage).
	inputEndsWithCommand = query[-2:] == ' #' or query[-2:] == ' !' or query[-2:] == ' +'
	# log.debug('createListItemNotification - conditions: ')
	# log.debug('inputEndsWithCommand: ' + str(inputEndsWithCommand))
	# log.debug('doNotDisplayCreate: ' + str(isDoNotDisplayCreate))
	# log.debug('hasFoundMatch: ' + str(hasFoundMatch))
	# log.debug('isCustomTagEntered: ' + str(isCustomTagEntered))
	if not inputEndsWithCommand and not isDoNotDisplayCreate and (not hasFoundMatch or isCustomTagEntered):
		addCreateTaskItem(inputName, inputContent, inputDue, inputPriority, inputTags, inputList)
		checkUpdates(wf3) # Output *after* 'Create Task', so user is not pestered by the notiifcation when trying to create a task
		wf3.send_feedback()


if __name__ == "__main__":
	wf = Workflow(update_settings = UPDATE_SETTINGS)
	wf3 = Workflow3(update_settings = UPDATE_SETTINGS)
	log = wf.logger
	sys.exit(wf.run(main))
