import subprocess
import re

from langchain.agents import tool


@tool
def computer_applescript_action(apple_script):
    """
    Use this when you want to execute a command on the computer. The command should be in AppleScript.

    Always start with starting the app and activating it.

    If it's a calculation, use the calculator app.

    Use delay 0.5 between keystrokes.

    When possible click buttons instead of typing.

    Here are some examples of good AppleScript commands:

    Command: Create a new page in Notion
    AppleScript: tell application "Notion"
        activate
        delay 0.5
        tell application "System Events" to keystroke "n" using {{command down}}
    end tell

    Command: Search for a table nearby
    AppleScript: tell application "Google Chrome"
        activate
        delay 0.5
        open location "https://www.google.com/search?q=Table+nearby"
    end tell

    The AppleScript should be valid including quotations.

    Write the AppleScript for the Command:
    Command:
    """
    # print("Running\n", apple_script)

    return run_applescript(apple_script)


@tool
def chrome_get_the_links_on_the_page(input):
    """
    Use this when you want to get the links on the current page.

    You should use this before clicking on anything
    """
    return run_javascript(
        'Array.from(document.querySelectorAll("a")).map(x => x.innerText + ": " + x.href).join(" - ")'
    )[:4000]


@tool
def chrome_click_on_link(link):
    """
    Use this when you want to go to a link.

    The link should be a url from a previous observation
    """
    return run_javascript(f'window.location.href = "{link}"')[:4000]


@tool
def chrome_read_the_page(input):
    """
    Use this when you want to read the page.
    """

    return run_javascript("document.body.innerText")[:4000]


@tool
def read_messages_from_iMessage(input):
    """
    Use this when you want to read the messages from a contact in iMessage.
    """

    # Get the contact and time frame from the input
    contact = input[0]
    time_frame = input[1]

    script = f"""
    tell application "Messages"
        activate
        set targetService to id of 1st account whose service type = iMessage
        set theBuddy to buddy "{contact}" of service targetService
        set theMessages to messages of theBuddy
        set theMessages to last {time_frame} of theMessages
        set theTexts to ""
        repeat with aMessage in theMessages
            set theTexts to theTexts & sender of aMessage & ": " & content of aMessage & linefeed
        end repeat
        return theTexts
    end tell
    """

    return run_applescript(script)


@tool
def send_text_to_contact_on_iMessage(input):
    """
    Use this when you want to send a text to a contact in iMessage.
    """

    # Get the contact and message from the input split by the first comma
    split_input = input.split(",")
    contact = split_input[0]
    message = ",".join(split_input[1:])

    script = f"""
    tell application "Messages"
        activate
        set targetBuddy to "{contact}"
        set targetService to id of 1st account whose service type = iMessage
        set theBuddy to participant targetBuddy of account id targetService
        send "{message}" to theBuddy
    end tell
    """

    return run_applescript(script)


@tool
def retrieve_contact_from_device(input):
    """
    Use this when you want to retrieve a contact from your device. E.g phone number or email.
    """

    script = f"""
    tell application "Contacts"
        activate
        set thePerson to person "{input}"
        set thePhones to value of phones of thePerson
        set theEmails to value of emails of thePerson
        return thePhones & theEmails
    end tell
    """

    return run_applescript(script)


@tool
def retrieve_contact_online(input):
    """
    Use this to retrieve contact information from personal contacts list on google contacts.

    Use this first before sending a text to a contact on iMessage.
    """

    # search for the contact
    chrome_open_url("https://contacts.google.com/search/" + input)


    # click on the first contact
    chrome_click_on_link(
        run_javascript(
            'document.querySelectorAll("a")[0].href'
        )
    )


@tool
def browse_internet(input):
    """
    Use this when needing to access the internet. E.g. go to a website, search for something, etc.

    Use this first if information is needed from the internet. Input should contain the js command to execute.
    """

    return run_javascript(input)


# @tool
# def chrome_javascript_action(javascript):
#     """
#     Use this when you want to execute a javascript command on Chrome either to get data or trigger an action. The command should be in Javascript.

#     Here are some examples of good Javascript commands:

#     Command: Get the links on the page
#     document.querySelectorAll('a')

#     Command: Get the buttons on the page
#     document.querySelectorAll('button')

#     Command: Click the first button on the page
#     document.querySelectorAll('button')[0].click()

#     Write the Javascript for the command:
#     """

#     stdout = run_javascript(javascript)

#     return f"""
#     Current URL: {run_javascript('window.location.href')}

#     Result: {stdout}
#     """


@tool
def chrome_open_url(url):
    """
    Use this tool to open a URL in Chrome. It is recommended to use this tool before doing any other actions on Chrome.

    The URL should be a string. For example: https://gmail.com
    """
    script = f"""
    tell application "Google Chrome"
        open location "{url}"
    end tell
    """

    return run_applescript(script)


def run_javascript(javascript):
    javascript = javascript.replace('"', '\\"')

    if javascript.startswith("open "):
        return "Invalid command, not javascript"

    script = f"""
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "{javascript}"
        end tell
    end tell
    """

    return run_applescript(script)


def run_applescript(applescript):
    p = subprocess.Popen(
        ["osascript", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = p.communicate(applescript.encode("utf-8"))

    if p.returncode != 0:
        raise Exception(stderr)

    decoded_text = stdout.decode("utf-8")

    return decoded_text


def say_text(text):
    run_applescript(f'say "{text}"')
