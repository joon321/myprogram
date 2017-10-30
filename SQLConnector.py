from tkinter import *
from tkinter import messagebox, filedialog
import csv
import re
import psycopg2
import pymssql
import pymysql
import _mssql


class SQLConnector:

	def __init__(self, master):
		frame = Frame(master)
		frame.grid()

		self.label = Label(master, text="SQL Connector")
		self.label.grid(row=0, column=0, sticky='w')

		self.listLabel = Label(master, text="Query Result")
		self.listLabel.grid(row=0, column=4, sticky='se')
		self.listbox = Listbox(master, width=80)
		self.listbox.grid(row=1, column=3, sticky='nsew', columnspan=2, rowspan=2)
		self.listbox.config(border=2, relief='sunken')

		self.listScrolly = Scrollbar(master, orient=VERTICAL, command=self.listbox.yview)
		self.listScrolly.grid(row=1, column=5, sticky='nsw', rowspan=2)
		self.listScrollx = Scrollbar(master, orient=HORIZONTAL, command=self.listbox.xview)
		self.listScrollx.grid(row=2, column=3, sticky='swe', columnspan=2)
		self.listbox['yscrollcommand'] = self.listScrolly.set
		self.listbox['xscrollcommand'] = self.listScrollx.set

		# Frame for the radio buttons
		self.optionFrame = LabelFrame(master, text="SQL Server")
		self.optionFrame.grid(row=1, column=0, sticky='nw')

		self.rbValue = IntVar()
		self.rbValue.set(1)

		self.radio1 = Radiobutton(self.optionFrame, text="MSSQL", value=1, variable=self.rbValue,
								  command="")
		self.radio2 = Radiobutton(self.optionFrame, text="Postgres", value=2, variable=self.rbValue,
								  command="")
		self.radio3 = Radiobutton(self.optionFrame, text="MySQL", value=3, variable=self.rbValue,
								  command="")
		self.radio1.grid(row=0, column=0, sticky='w')
		self.radio2.grid(row=1, column=0, sticky='w')
		self.radio3.grid(row=2, column=0, sticky='w')

		# Frame for the DB connect
		self.DBConnectFrame = LabelFrame(master, text="DB Connect Config", width=60, padx=8, pady=8)
		self.DBConnectFrame.grid(row=2, column=0, sticky='nw')

		# DB connection
		self.hostLabel = Label(self.DBConnectFrame, text="Host:")
		self.hostLabel.grid(row=2, column=0, sticky='nw')
		self.hostEntry = Entry(self.DBConnectFrame, width=20)
		self.hostEntry.grid(row=2, column=1, sticky='sw')
		self.dsnLabel = Label(self.DBConnectFrame, text="DB:")
		self.dsnLabel.grid(row=3, column=0, sticky='nw')
		self.dsnEntry = Entry(self.DBConnectFrame, width=20)
		self.dsnEntry.grid(row=3, column=1, sticky='sw')
		self.userLabel = Label(self.DBConnectFrame, text="User:")
		self.userLabel.grid(row=4, column=0, sticky='nw')
		self.userEntry = Entry(self.DBConnectFrame, width=20)
		self.userEntry.grid(row=4, column=1, sticky='sw')
		self.pwdLabel = Label(self.DBConnectFrame, text="Password:")
		self.pwdLabel.grid(row=5, column=0, sticky='nw')
		self.pwdEntry = Entry(self.DBConnectFrame, width=20)
		self.pwdEntry.grid(row=5, column=1, sticky='sw')
		self.portLabel = Label(self.DBConnectFrame, text="Port:")
		self.portLabel.grid(row=6, column=0, sticky='nw')
		self.portEntry = Entry(self.DBConnectFrame, width=20)
		self.portEntry.grid(row=6, column=1, sticky='sw')

		# SQL statement frame
		self.queryFrame = LabelFrame(master, text="Write Query", width=100, padx=5, pady=5)
		self.queryFrame.grid(row=3, column=3, sticky='nw', columnspan=2, rowspan=2)

		# Write SQL statement
		self.queryEntry = Entry(self.queryFrame, width=100)
		self.queryEntry.grid(row=1, column=0, sticky='nw')

		# Buttons
		self.okButton = Button(master, text="RUN", command=self.run_button)
		self.quitButton = Button(master, text="QUIT", command=master.destroy)
		self.clearButton = Button(master, text="CLEAR QUERY", command=self.clear_button)
		self.exportButton = Button(master, text="EXPORT CSV", command=self.export_button)
		self.okButton.grid(row=4, column=3, sticky='e')
		self.quitButton.grid(row=4, column=4, sticky='w')
		self.clearButton.grid(row=3, column=4, sticky='se')
		self.exportButton.grid(row=4, column=4, sticky='ne')
		
		# file export options
		self.file_opt = options = {}
		options['filetypes'] = [('all files', '.*'), ('csv files', '.csv')]
		options['initialfile'] = 'myquery.csv'
		options['parent'] = master

	def db(self, dbtype):
		# connection param
		conn_opt = config = {}
		config['database'] = self.dsnEntry.get()
		config['port'] = self.portEntry.get()
		config['password'] = self.pwdEntry.get()
		config['host'] = self.hostEntry.get()
		config['user'] = self.userEntry.get()

		if dbtype == "postgres":
			conn = psycopg2.connect(**conn_opt)
			return conn
		elif dbtype == "mssql":
			conn = pymssql.connect(**conn_opt)
			return conn
		elif dbtype == "mysql":
			conn = pymysql.connect(**conn_opt)
			return conn
		else:
			raise Exception("DB not supported")

	def dbtype(self):
		if self.rbValue.get() == 1:
			return "mssql"
		elif self.rbValue.get() == 2:
			return "postgres"
		elif self.rbValue.get() == 3:
			return "mysql"
		else:
			raise Exception("No such DB found")

	def definemethod(self):
		query = self.queryEntry.get()
		select = '^[sS][eE][lL][eE][cC][tT]'
		update = '^[uU][pP][dD][aA][tT][eE]'
		insert = '^[iI][nN][sS][eE][rR][tT]'
		create = '^[cC][rR][eE][aA][tT][eE]'
		delete = '^[dD][eE][lL][eE][tT][eE]'
		drop = '^[dD][rR][oO][pP]'

		if re.search(select, query):
			return "select"
		elif re.search(update, query):
			return "update"
		elif re.search(insert, query):
			return "insert"
		elif re.search(create, query):
			return "create"
		elif re.search(delete, query):
			return "delete"
		elif re.search(drop, query):
			return "drop"
		else:
			return

	def pgcommand(self):
		command = self.queryEntry.get()
		dbtype = self.dbtype()
		# host = self.hostEntry.get()
		# db = self.dsnEntry.get()
		# user = self.userEntry.get()
		# password = self.pwdEntry.get()
		# port = self.portEntry.get()

		conn = None

		try:
			conn = self.db(dbtype)
			if self.definemethod() is "select":
				cur = conn.cursor()
				cur.execute(command)
				rows = cur.fetchall()
				cur.close()
				lists = []
				for row in rows:
					lists.append(row)
				return lists
			else:
				cur = conn.cursor()
				cur.execute(command)
				conn.commit()
				row = cur.lastrowid
				cur.close()
				return row
		except _mssql.MssqlDatabaseException as sql_error:
			return sql_error
		except (Exception, psycopg2.DatabaseError) as pg_error:
			return pg_error
		except (Exception, pymysql.DatabaseError) as mysql_error:
			return mysql_error
		# close the opened session
		finally:
			if conn is not None:
				conn.close()

	def run_button(self):
		query = "select", "insert", "create", "delete", "drop", "update"

		if self.definemethod() not in query:
			return messagebox.showerror("ERROR", "Enter a valid method such as {} ".format(query))
		if len(self.listbox.get(first=0, last=0)) is 0:
			result = self.pgcommand()
			if isinstance(result, list):
				for each in result:
					self.listbox.insert(END, each)
			else:
				self.listbox.insert(END, result)
		else:
			self.listbox.delete(0, END)
			self.run_button()

	def clear_button(self):
		self.listbox.delete(0, END)

	def export_button(self):
		if len(self.listbox.get(first=0, last=0)) is 0:
			return messagebox.showerror("ERROR", "No query result to export")
		else:
			filename = filedialog.asksaveasfilename(**self.file_opt)
			if filename:
				with open(filename, "w") as outfile:
					writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
					result = self.pgcommand()
					for each in result:
						writer.writerow(each)
				 

if __name__ == '__main__':
	mainWindow = Tk()
	SQLConnector(mainWindow)
	mainWindow.title("SQL Connector")
	mainWindow.geometry('860x620')
	mainWindow['padx'] = 8

	mainWindow.columnconfigure(0, weight=1)
	mainWindow.columnconfigure(1, weight=1)
	mainWindow.columnconfigure(2, weight=1)
	mainWindow.columnconfigure(3, weight=1)
	mainWindow.columnconfigure(4, weight=1)
	mainWindow.columnconfigure(5, weight=1)
	mainWindow.rowconfigure(0, weight=1)
	mainWindow.rowconfigure(1, weight=1)
	mainWindow.rowconfigure(2, weight=1)
	mainWindow.rowconfigure(3, weight=1)
	mainWindow.rowconfigure(4, weight=1)
	mainWindow.mainloop()
