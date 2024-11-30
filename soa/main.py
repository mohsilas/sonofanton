from time import sleep as wait
from soa_functions import SOAService
from json import tool

fn = SOAService("server-gmail-addr", "app password", 'SUBJECT "email-subjct-password"', "anthropic_api", "pushover-app-api", "puhsover-user-key")
instructions = []

def main_loop():
    sender, body = fn.mail_check()
    if not(body):
        return 0

    directive = fn.claude(f"You're an ai agent named Soa, given this email. follow the instructions that you can and then summarize the user's commands for another agent that can use functions and scripts. EmailData: from: {sender} email: {body}")

    # use tool
    tool = fn.tool_use(directive)
    result = fn.run_tool(tool)

    # notification
    tool = fn.tool_use(f"send me a concise pushover notification about this: {result}")
    result = fn.run_tool(tool)




main_loop()

#while True:
#    try:
#        main_loop()
#        wait(30)
#    except Exception as e:
#        print(e)
#        quit()
