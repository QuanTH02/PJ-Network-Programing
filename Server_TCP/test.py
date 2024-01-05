requests = "xinchao\r\ncacban\r\nhehe"
commands = [request for request in requests.split('\r\n')[::2] if request] 

print(commands)
