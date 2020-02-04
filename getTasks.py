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
import json
import emoji
import datetime
from main import DEBUG, formatDate
from workflow import Workflow, Workflow3, ICON_WEB, ICON_CLOCK, ICON_WARNING, ICON_GROUP, web
from config import confNames, getConfigValue


def main(wf):
	getTasks()


def getTasks():
	'''Retrieves a list of Tasks from the ClickUp API.

----------
	'''
	# For mode = search: ClickUp does not offer a parameter 'filter_by' - therefore we receive all tasks, and use Alfred/fuzzy to filter.
	if DEBUG > 0:
		log.debug('[ Calling API to list tasks ]')
	url = 'https://api.clickup.com/api/v2/team/' + getConfigValue(confNames['confTeam']) + '/task'
	params = {}

	if 'space' in getConfigValue(confNames['confHierarchyLimit']):
		params['space_ids[]'] = getConfigValue(confNames['confSpace']) # Use [] instead of %5B%5D
	if 'folder' in getConfigValue(confNames['confHierarchyLimit']):
		params['project_ids[]'] = getConfigValue(confNames['confProject'])
	if 'list' in getConfigValue(confNames['confHierarchyLimit']):
		params['list_ids[]'] = getConfigValue(confNames['confList'])
	params['order_by'] = 'due_date'
	# Differentiates between listing all Alfred-created tasks and searching for all tasks (any)
	if DEBUG > 0 and len(wf.args) > 1 and wf.args[1] == 'search':
		log.debug('[ Mode: Search ]')
	else:
		params['tags[]'] = getConfigValue(confNames['confDefaultTag'])
	headers = {}
	headers['Authorization'] = getConfigValue(confNames['confApi'])
	headers['Content-Type'] = 'application/json'
	if DEBUG > 1:
		log.debug(url)
		log.debug(headers)
		log.debug(params)
	try:
		request = web.get(url, params = params, headers = headers)
		request.raise_for_status()
	except:
		log.debug('Error on HTTP request')
		wf3.add_item(title = 'Error connecting to ClickUp.', subtitle = 'Open configuration to check your parameters?', valid = True, arg = 'cu:config ', icon = 'error.png')
		wf3.send_feedback()
		exit()
	result = request.json()
	if DEBUG > 1:
		log.debug('Response: ' + str(result))

	wf3 = Workflow3()
	for task in result['tasks']:
		tags = ''
		if task['tags']:
			for allTaskTags in task['tags']:
				tags += allTaskTags['name'] + ' '

		wf3.add_item(
			title = '[' + task['status']['status'] + '] ' + task['name'],
			subtitle = (emoji.emojize(':calendar:') + \
                str(datetime.datetime.fromtimestamp(int(task['due_date'])/1000)) if task['due_date'] else '') + (emoji.emojize(
			':exclamation_mark:') + task['priority']['priority'].title() if task['priority'] else '') + (' ' + emoji.emojize(':label:') + tags if task['tags'] else ''),
			valid = True,
			arg = task['url']
		)
	wf3.send_feedback()


if __name__ == "__main__":
	wf = Workflow()
	log = wf.logger
	sys.exit(wf.run(main))
