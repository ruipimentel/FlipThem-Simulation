import system


s = system.System(10)

for server in s.get_all_servers():
    print(server.get_name())

