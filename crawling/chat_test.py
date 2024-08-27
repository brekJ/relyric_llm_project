from chat_driver import ChatDriver as ChatDriver

chat_driver = ChatDriver()
check_list = []
try:
    with open("check_list.txt", 'r') as f:
        check_list = f.read().split("\n")
except:
    pass
print(len(check_list))