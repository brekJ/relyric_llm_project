from chat_driver import ChatDriver as ChatDriver

chat_driver = ChatDriver()
check_list = []
try:
    with open("./check_list.txt", 'r', encoding='utf-8') as f:
        check_list = f.read().split("\n")
except Exception as e:
    print(e)
print(len(check_list))