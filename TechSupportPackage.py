import os
from os.path import join
import tarfile
import sys, getopt
from optparse import OptionParser

source = 'c:\\backup'

"""FIXED Lists"""
FLists = [".log", ".conf"]
OLists = []
length = len(FLists)

def EXType(file):
	for i in range(length):
		if file.endswith(FLists[i]):
			return True

def addMoreExt(file):
	for i in range(len(OLists)):
		if file.endswith(OLists[i]):
			return True

def package(rootDir, _FILE_="TechSupportPkg.tar.gz"):
	with tarfile.open(_FILE_, "w:gz") as tar:
		for dirName, subdirList, fileList in os.walk(rootDir):
			for file in fileList:
				if EXType(file) or addMoreExt(file):
					FILE=join(dirName, file)
					print("A file {} archived".format(FILE))
					tar.add(FILE)

def readPackage(_FILE_):
	with tarfile.open(_FILE_, "r:gz") as tar:
		for tarinfo in tar:
			print(tarinfo.mtime, tarinfo.mode, tarinfo.size, tarinfo.name)

def main():
	usage = "usage: %prog -c [options] arg1 arg2"
	parser = OptionParser(usage=usage)
	parser.add_option("-c", "--create", action="store_true", dest="TSPackage",
				  	help="create a tech support package", metavar="FILE")
	parser.add_option("-d", "--dir", action="store", dest="dir",
					help="get data from additional directories")
	parser.add_option("-v", "--view", action="store", dest="view",
				  	help="view tech support package", metavar="FILE")
	parser.add_option("-a", "--append",	action="store_true", dest="append",
				  	help="add more file types")

	(options, args) = parser.parse_args()

	"""Required"""
	if len(sys.argv) == 1:
		parser.print_help()

	if (options.append and options.TSPackage) or \
			(options.dir or options.append):
		for arg in args:
			OLists.append(arg)

	if options.TSPackage:
		package(source)

	if options.dir:
		package(options.dir, "CustomPkg.tar.gz")

	if options.view:
		readPackage(options.view)


	# try:
	# 	opts, args = getopt.getopt(argv, "hip:v:",["TSPackage=", "Path=", "ViewTSP="])
	# except getopt.GetoptError as err:
	# 	print(err)
	# 	usage()
	# 	sys.exit(2)
	#
	# for opt, arg in opts:
	# 	if opt in ("-h"):
	# 		usage()
	# 	elif opt in ("-i", "--TSPackage"):
	# 		package(source)
	# 	elif opt in ("-p", "--Path"):
	# 		package(arg, "CustomSupportPackage.tar.gz")
	# 	elif opt in ("-v", "--ViewTSP"):
	# 		readPackage(arg)

if __name__ == "__main__":
	main()


