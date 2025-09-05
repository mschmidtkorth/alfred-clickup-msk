> [!IMPORTANT]
> **Project is no longer in active development.**
>
> [Find an updated fork for Python 3 here](https://github.com/four13co/alfred-clickup-four13).

# ClickUp 2.0 Alfred Workflow
This workflow allows you to use Alfred to quickly add tasks and search tasks within ClickUp 2.0.

## Contents

- [ClickUp 2.0 Alfred Workflow](#clickup-20-alfred-workflow)
  - [Contents](#contents)
  - [Installation & Requirements](#installation--requirements)
  - [Configuration](#configuration)
  - [Usage & Commands](#usage--commands)
    - [Creating Tasks (`cu`)](#creating-tasks-cu)
      - [Examples](#examples)
    - [Searching Tasks (`cus`)](#searching-tasks-cus)
    - [Listing Open Tasks (`cuo`)](#listing-open-tasks-cuo)
    - [Listing Created Tasks (`cul`)](#listing-created-tasks-cul)
  - [How to Contribute](#how-to-contribute)
  - [ClickUp Terminology](#clickup-terminology)
  - [Changelog](#changelog)
  - [Thanks](#thanks)

## Installation & Requirements
For this workflow you need

- [ClickUp 2.0](https://docs.clickup.com/en/articles/3005140-guide-to-switching-to-2-0) (will not work with 1.0)
- Alfred 4 with a [Powerpack](https://www.alfredapp.com/powerpack/) license

To install, download the [latest release](https://github.com/mschmidtkorth/alfred-clickup-msk/releases/latest) and open the `.alfredworkflow` file.

## Configuration
Before being able to connect to ClickUp, certain parameters need to be configured. Configuration can be initiated via the `cu:config` command in Alfred, or by simply typing `cu` when starting the workflow for the first time. See [ClickUp Terminology](#clickup-terminology) for an explanation of terms.

The following parameters are *required*:

| Configuration setting         | Description                                                                                                                                                                                                                                                                                                      | Example                |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| *ClickUp API key*             | API token generated in ClickUp (either a public token or a private SSO token). Allows us to connect to your ClickUp account.<br>Can be retrieved from *ClickUp app > Profile Icon (bottom left) > Apps > Generate API key*<br> *Note:* Treat this key as your password. It will be stored in the MacOS Keychain. | `pk_12345_sdhu2348...` |
| *Id for ClickUp Workspace*    | Id of the Workspace your tasks reside in.                                                                                                                                                                                                                                                                        | `2181159`              |
| *Id for ClickUp Space*        | Id of the Space that defines your available Labels and Priorities.                                                                                                                                                                                                                                               | `2288348`              |
| *Id for default ClickUp List* | Id of the List you want new tasks to be added to by default.                                                                                                                                                                                                                                                     | `4696187`              |
| *Default Tag*                 | Name of the tag you want to attach to all new tasks (this is only required for the `cul` command).                                                                                                                                                                                                               | `to_review`            |

*Note:* Your ClickUp user account must be authorized for the specified workspace, space, folder and list.

The following parameters are *optional*:

| Configuration setting                      | Description                                                                                                                                                                                                                                                                                                                             | Example       |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| *Id for ClickUp Folder*                    | Id of the Folder your List is part of.                                                                                                                                                                                                                                                                                                  | `2844542`     |
| *Default Due Date*                         | If no Due date is specified when creating a task (via `@`), this Due date is used. Otherwise, no due date is set.                                                                                                                                                                                                                       | `h2`          |
| *Hierarchy Levels to limit Search Results* | When searching (`cus`, `cul`) you can limit the tasks returned by Space, Folder, List or a combination of those. For example, limiting by `space,folder` would use the *Id for ClickUp Space* and *Id for ClickUp Folder* to limit the search results by. If you do not provide a value, all tasks for your Workspace will be returned. | `folder,list` |
| *Show Notification*                        | Whether to show a notification after creating a task.                                                                                                                                                                                                                                                                                   | `true`        |

You can validate all parameters via `cu:config validate`. This should be your first step if anything does not work.

## Usage & Commands
- `cu` Create a new task
- `cus` Search for a task
- `cuo` Show all open tasks
- `cul` Show all tasks created via Alfred

### Creating Tasks (`cu`)
![Creating a task](docs/ClickUp.gif)

Tasks can be created by providing a title and optional commands.

```text
   cu <Title> [:<Description>] [#<Tag>] [@<Due Date>] [!<Priority>] [+<List>]
```

- Press `Enter` to create the task.
- Press `⌥ + Enter` to open the created task in ClickUp (web)

Commands let you add additional information to your task:

- Commands are added via one-character shortcuts
  - `:` **Description** of a task (max. 1 possible)
  - `#` **Tag** of a task (N possible). A list of available tags will be provided and can be filtered by typing e.g. `#myLa`. Additional tags are specified via another command shortcut, e.g. `cu Task #Tag1 #Tag2`. If you have specified a default tag, it will always be added. Tags may contain spaces. To create a new tag, simply type its name and press *Space*. Tags are cached for 10 minutes.
  - `@` **Due date** of a task (max. 1 possible).
    - `m<number>` Task is due in `<number>` minutes
    - `h<number>` Task is due in `<number>` hours
    - `d<number>` Task is due in `<number>` days
    - `w<number>` Task is due in `<number>` weeks
    - `mon` or `monday` Task is due for next Monday (same for other days)
    - `tod` or `today` Task is due for today
    - `tom` or `tomorrow` Task is due for tomorrow
    - `2020-12-31` Task is due on 2020-12-31 at the current time
    - `2020-12-31 14.00` Task is due on 2020-12-31 at 2pm (*note:* Hours, minutes and seconds are separated via `.`, as `:` is used to define the task's description)
    - `14.00` Task is due today at 2pm (*note:* Hours, minutes and seconds are separated via `.`, as `:` is used to define the task's description)
  - `!` **Priority** of a task (max. 1 possible). A list of available priorities will be provided and can be filtered by typing e.g. `!1` or `!Urge`. If not specified, priority is Normal.
    - `!1` Task has a priority of Urgent
    - `!2` Task has a priority of High
    - `!3` Task has a priority of Normal
    - `!4` Task has a priority of Low
  - `+` **List** a task is assigned to (max. 1 possible). A list of available lists (ha) will be provided and can be filtered by typing e.g. `+myLi`. If you do not specify a List, your default will be used. Lists are cached for 2 hours.
- Commands are optional
- Commands are separated by space
- Commands can be in any sequence
- If no Due date or List is specified via a command, default values are used (see [Configuration](#configuration))
- *Caveat*: If you want to use `@`, `!` or `+` in either title or content, do not use a space before. Otherwise the character will be identified as a command signifier.

#### Examples

```text
cu Clean the kitchen :Before my wife gets angry #Housework @h4 !1
```

> Creates a task titled "Clean the kitchen", with description "Before my wife gets angry", tagged with "Housework", having a priority of "Urgent" and due in 4 hours , assigned to your default list.

```text
cu Clean the kitchen #Housework #Wife +Personal
```

> Creates a task titled "Clean the kitchen", tagged with "Housework" and "Wife" due in 2 hours (your default) and assigned to List "Personal".

### Searching Tasks (`cus`)
You can search through all of your tasks within your ClickUp workspace. All open tasks matching your search term will be returned. The search uses fuzzy matching, so `Test` will find `Test Task` and `Ted rest`. You can use `cus [<status>]` to filter tasks by status, e.g. `cus [Open]`.

```text
cus <search terms>
```

- Press `Enter` to open the task in ClickUp (web).
- Press `⌥ + Enter` to close the selected task (Status = Closed).

### Listing Open Tasks (`cuo`)
You can list all of your tasks that are due or overdue until end of today.

```text
cuo [<search terms>]
```

- Press `Enter` to open the task in ClickUp (web).
- Press `⌥ + Enter` to close the selected task (Status = Closed).

### Listing Created Tasks (`cul`)
You can list all of your tasks created via Alfred. This might be convenient if you created tasks in a hurry and want to go through them later in detail.

```text
cul [<search terms>]
```

- Press `Enter` to open the task in ClickUp (web).
- Press `⌥ + Enter` to close the selected task (Status = Closed).

*Note:* This only works if you defined a **default tag** via `cu:config defaultTag ` as the tasks are filtered by this tag.

## How to Contribute
Please see the [contribution guidelines](CONTRIBUTING.md).

## ClickUp Terminology
ClickUp allows you to organize your work in a hierarchy: *1 Workspace > n Spaces > [n Folders] > n Lists > n Tasks*

- A [**Workspace**](https://docs.clickup.com/en/articles/1156370-how-do-i-create-a-new-workspace) (also called *Workplace*, in ClickUp 1.0 called *Team*) is the highest level of the ClickUp hierarchy. You can be part of one, or many Workspaces. You switch between Workspaces by clicking on your avatar in the bottom left. Multiple people can be members of a workspace. Workspaces are entirely separate of each other, for example you cannot move tasks between them.
  - To find the Id of your Workspace, go to app.clickup.com and open the 'Task' sidebar. Click on a Space icon (not the name) and copy the URL. From the URL, retrieve the first Id after `https://app.clickup.com/`.
  - *Example:* `https://app.clickup.com/**2189725**/v/l/s/2288449`
- A [**Space**](https://docs.clickup.com/en/articles/2705244-what-are-spaces) is the second level of the ClickUp hierarchy. Spaces can be public or private. An example for a Space is 'Work' or 'Personal', or a department in a business context. In the 'Tasks' sidebar of the ClickUp app, Spaces can be found at the top.
  - To find the Id of your Space, go to app.clickup.com and open the 'Task' sidebar. Click on a Space icon (not the name) and copy the URL. From the URL, retrieve the second Id after the last slash.
  - *Example:* `https://app.clickup.com/2189725/v/l/s/**2288449**`
- A [**Folder**](https://docs.clickup.com/en/articles/887681-folders-lists-what-are-they) (in ClickUp 1.0 called *Project*) groups a set of Lists. Folders are optional. In the 'Tasks' sidebar of the ClickUp app, Folders can be found below Spaces.
  - To find the Id of a Folder, go to app.clickup.com and open the 'Task' sidebar. Click on a Space to open it, then click on a Folder and copy the URL. From the URL, retrieve the second Id after the last slash.
  - *Example:* `https://app.clickup.com/2189725/v/l/f/**2844754**?pr=2288429`
- A [**List**](https://docs.clickup.com/en/articles/887681-folders-lists-what-are-they) is where your tasks live. A list can be part of a folder, or exist on its own.  In the 'Tasks' sidebar of the ClickUp app, Lists can be found within Folders, or on its own below a Space.
  - To find the Id of a Space, go to app.clickup.com and open the 'Task' sidebar. Click on a Space to open it, then - if you use Folders - click on a Folder. Hover over a List and click on the three dots to the right, then click the URL icon on the top left of the popup to copy the link. and copy the URL. From the URL, retrieve the second Id after the last slash.
  - *Example:* `https://app.clickup.com/2189725/v/li/**4646883**`
- A [**Task**](https://docs.clickup.com/en/articles/911164-how-to-create-a-task) is where you document your activities. Tasks can be found within lists.

<!-- Sources:
https://docs.clickup.com/en/articles/3005140-guide-to-switching-to-2-0
https://docs.clickup.com/en/articles/2044847-onboarding-guide
https://docs.clickup.com/en/articles/1045623-how-does-the-hierarchy-structure-work-in-clickup
-->

## Changelog
See [Releases](https://github.com/mschmidtkorth/alfred-clickup-msk/releases)

- 1.0
  - Initial version, first public release

## Thanks

- The [ClickUp team](http://clickup.com) for providing their API and great responsiveness in case of any questions.
- [@deanishe](https://github.com/deanishe/) for his wonderful [Alfred-Workflow](https://github.com/deanishe/alfred-workflow) Python library.
