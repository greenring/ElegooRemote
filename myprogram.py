import lirc

sockid = lirc.init("myprogram")
r = lirc.nextcode()
print(r)