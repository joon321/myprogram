from tkinter import *
from tkinter import messagebox
import re


class SubCal:
	octets = [128, 64, 32, 16, 8, 4, 2, 1]
	ipClass = "255", "255.255", "255.255.255"
	ClassA, ClassB, ClassC = ipClass

	def __init__(self, master):
		frame = Frame(master)
		frame.grid()

		self.label = Label(master, text="IP Subnet Calculator")
		self.label.grid(row=0, column=0)

		self.listLabel = Label(master, text="List Hosts")
		self.listLabel.grid(row=0, column=1, sticky='se')
		self.listbox = Listbox(master, width=40)
		self.listbox.grid(row=1, column=1, sticky='nsew', rowspan=2)
		self.listbox.config(border=2, relief='sunken')

		self.listScroll = Scrollbar(master, orient=VERTICAL, command=self.listbox.yview)
		self.listScroll.grid(row=1, column=2, sticky='nsw', rowspan=2)
		self.listbox['yscrollcommand'] = self.listScroll.set

		# Frame for the radio buttons
		self.optionFrame = LabelFrame(master, text="IP Class")
		self.optionFrame.grid(row=1, column=0, sticky='nw')

		self.rbValue = IntVar()
		self.rbValue.set(1)

		self.radio1 = Radiobutton(self.optionFrame, text="Class A", value=1, variable=self.rbValue,
								  command=self.setspinnervalue)
		self.radio2 = Radiobutton(self.optionFrame, text="Class B", value=2, variable=self.rbValue,
								  command=self.setspinnervalue)
		self.radio3 = Radiobutton(self.optionFrame, text="Class C", value=3, variable=self.rbValue,
								  command=self.setspinnervalue)
		self.radio1.grid(row=0, column=0, sticky='w')
		self.radio2.grid(row=1, column=0, sticky='w')
		self.radio3.grid(row=2, column=0, sticky='w')

		# Frame for the mask spinners
		self.maskFrame = LabelFrame(master, text="CIDR Mask")
		self.maskFrame.grid(row=2, column=0, sticky='nw')

		self.spValue = StringVar()
		# Masking
		self.maskSpinner = Spinbox(self.maskFrame, width=2, textvariable=self.spValue, values=tuple(range(8, 32)),
								   command=self.setipclassvalue)
		self.maskSpinner.grid(row=2, column=0)

		# Frame for IP entry
		self.ipFrame = LabelFrame(master, text="IP Address")
		self.ipFrame.grid(row=3, column=0, sticky='nw')
		self.ipEntry = Entry(self.ipFrame)
		self.ipEntry.grid(row=0, column=0, sticky='sw', padx=2)

		# Buttons
		self.okButton = Button(master, text="OK", command=self.ok_button)
		self.quitButton = Button(master, text="QUIT", command=master.destroy)
		self.clearButton = Button(master, text="CLEAR TEXT", command=self.clear_button)
		self.okButton.grid(row=4, column=0, sticky='e')
		self.quitButton.grid(row=4, column=1, sticky='w')
		self.clearButton.grid(row=3, column=1, sticky='e')

	def setipclassvalue(self):
		val = int(self.spValue.get())
		if val in range(8, 16):
			self.rbValue.set(1)
		elif val in range(16, 24):
			self.rbValue.set(2)
		else:
			self.rbValue.set(3)

	def setspinnervalue(self):
		radiobutton = self.rbValue.get()
		if radiobutton == 1:
			self.spValue.set(8)
		elif radiobutton == 2:
			self.spValue.set(16)
		else:
			self.spValue.set(24)

	@staticmethod
	def validateip(ipaddr):
		pattern = '^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'
		if re.search(pattern, ipaddr):
			return 0
		else:
			return 1

	@staticmethod
	def getClassAhosts(cidr):
		# the input defaults to string so must convert the cidr to int
		mod = int(cidr) % 8
		if mod == 0:
			return 2 ** 24 - 2
		else:
			return 2 ** (24 - mod) - 2

	@staticmethod
	def getClassBhosts(cidr):
		# the input defaults to string so must convert the cidr to int
		mod = int(cidr) % 8
		if mod == 0:
			return 2 ** 16 - 2
		else:
			return 2 ** (16 - mod) - 2

	@staticmethod
	def getClassChosts(cidr):
		# the input defaults to string so must convert the cidr to int
		mod = int(cidr) % 8
		if mod == 0:
			return 2 ** 8 - 2
		else:
			return 2 ** (8 - mod) - 2

	def getTotalHosts(self, cidr):
		args = self.identify(cidr)
		if args == 1:
			return self.getClassAhosts(cidr)
		elif args == 2:
			return self.getClassBhosts(cidr)
		else:
			return self.getClassChosts(cidr)

	@staticmethod
	def getTotalSubnet(cidr):
		mod = int(cidr) % 8
		if mod == 0:
			power = 0
		else:
			power = mod
		total_subnet = 2 ** power
		return total_subnet

	def getNetworkAddr(self, ipaddr, cidr):
		totalMaskRange = 256
		ID = self.identify(cidr)
		totalSubnet = self.getTotalSubnet(cidr)
		splitaddr = ipaddr.split(".")
		reassembledIP = ".".join(splitaddr[0:ID])
		myrange = totalMaskRange / totalSubnet
		networkaddr = []
		for item in range(0, totalMaskRange, int(myrange)):
			# network addresses
			if ID == 1 or ID == 2:
				result = reassembledIP + "." + str(item) + "." + str(self.subNetTrail(ID))
			else:
				result = reassembledIP + "." + str(item)
			networkaddr.append(result)
		return networkaddr

	@staticmethod
	def subNetTrail(args):
		if args == 1:
			return 0.0
		elif args == 2:
			return 0
		else:
			return None

	def subNetBits(self, cidr):
		bit = 0
		ID = self.identify(cidr)
		mod = int(cidr) % 8
		if mod == 0 and ID in range(1, 4):
			return 0
		else:
			for each in range(mod):
				bit += self.octets[each]
			bits = bit
			return bits

	def subNetMask(self, args):
		if args == 1:
			return self.ClassA
		elif args == 2:
			return self.ClassB
		else:
			return self.ClassC

	@staticmethod
	def identify(cidr):
		if cidr in range(8, 16):
			return 1  # class A
		elif cidr in range(16, 24):
			return 2  # class B
		else:
			return 3  # class C

	@staticmethod
	def maskTrail(args):
		if args == 1:
			return "255.255"
		elif args == 2:
			return "255"
		else:
			return None

	def getbroadcastaddr(self, ipaddr, cidr):
		totalMaskRange = 256
		ID = self.identify(cidr)
		totalSubnet = self.getTotalSubnet(cidr)
		splitaddr = ipaddr.split(".")
		reassembledIP = ".".join(splitaddr[0:ID])
		myrange = int(totalMaskRange / totalSubnet)
		modify = lambda mod: 255 if totalSubnet == 1 else myrange
		broadcastaddr = []
		for item in range(modify(totalSubnet), totalMaskRange, modify(totalSubnet)):
			# network addresses
			if (ID == 1 or ID == 2) and totalSubnet == 1:
				result = reassembledIP + "." + str(item) + "." + self.maskTrail(ID)
			elif ID == 1 or ID == 2:
				result = reassembledIP + "." + str(item - 1) + "." + self.maskTrail(ID)
			elif ID == 3 and totalSubnet == 1:
				result = reassembledIP + "." + str(item)
			else:
				result = reassembledIP + "." + str(item - 1)
			broadcastaddr.append(result)
		# if total subnet is more than 1, must append the final broadcast address
		if (ID == 1 or ID == 2) and totalSubnet is not 1:
			broadcastaddr.append(reassembledIP + ".255." + self.maskTrail(ID))
		if ID == 3 and totalSubnet is not 1:
			broadcastaddr.append(reassembledIP + ".255")
		return broadcastaddr

	def ok_button(self):
		ipaddr = self.ipEntry.get()
		valid = self.validateip(ipaddr)
		if valid == 0:
			pass
		else:
			return messagebox.showinfo("ERROR", "Enter a valid IP")
		if len(self.listbox.get(first=0, last=0)) is 0:
			cidr = int(self.maskSpinner.get())
			radiobutton = self.rbValue.get()
			total_hosts = self.getTotalHosts(cidr)
			total_subnet = self.getTotalSubnet(cidr)
			network_address = self.getNetworkAddr(ipaddr, cidr)
			broadcast_address = self.getbroadcastaddr(ipaddr, cidr)
			subnet_bits = self.subNetBits(cidr)
			class_mask = self.subNetMask(radiobutton)
			subnet_trail = self.subNetTrail(radiobutton)
			self.listbox.insert(END, "Total hosts per subnet: {} ".format(total_hosts))
			self.listbox.insert(END, "Total subnet: {} ".format(total_subnet))
			if subnet_trail is None:
				self.listbox.insert(END, "Subnet mask: {}.{} ".format(class_mask, subnet_bits))
			else:
				self.listbox.insert(END, "Subnet mask: {}.{}.{} ".format(class_mask, subnet_bits, subnet_trail))
				self.listbox.insert(END, "Network address - Broadcast address")
				for net, broad in zip(network_address, broadcast_address):
					self.listbox.insert(END, " {} - {} ".format(net, broad))
				self.listbox.insert(END, "--" * 40)
		else:
			self.listbox.delete(0, END)
			self.ok_button()

	def clear_button(self):
		self.listbox.delete(0, END)

if __name__ == '__main__':
	mainWindow = Tk()
	SubCal(mainWindow)
	mainWindow.title("Calculator")
	mainWindow.geometry('420x400')
	mainWindow['padx'] = 8

	# main window geometry config
	mainWindow.columnconfigure(0, weight=1)
	mainWindow.columnconfigure(1, weight=1)
	mainWindow.columnconfigure(2, weight=1)
	mainWindow.columnconfigure(3, weight=1)
	mainWindow.columnconfigure(4, weight=1)
	mainWindow.rowconfigure(0, weight=1)
	mainWindow.rowconfigure(1, weight=1)
	mainWindow.rowconfigure(2, weight=1)
	mainWindow.rowconfigure(3, weight=1)
	mainWindow.rowconfigure(4, weight=1)
	mainWindow.mainloop()
