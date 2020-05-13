import hashlib
import os
import sys
import threading
import time
from send2trash import send2trash
import csv
lock = threading.Lock()
class filetype:
    def __init__(self,path,name):
        self.path = path
        self.name = name
        hasher = hashlib.md5()
        try:
            with open(path, 'rb') as afile:
                buf = afile.read()
                hasher.update(buf)
            self.hash = hasher.hexdigest()
        except:
            print(sys.exc_info()[0])

    path = None
    name = None
    hash = "Unknown"

def clearFile(file):
    with open(file,'w') as f:
        f.write("path,name,hash\n")
def addLine(file,line):
    global lock
    lock.acquire()
    with open(file,"a") as f:
        f.write(line)
    lock.release()
def handleDir(dirname,filenames,outputcsv):

    res = ""
    for filename in filenames:
        file = filetype(os.path.join(dirname, filename), filename)
        # if "," in file.path or "," in file.name or "," in file.hash:
        #     print(file.path)
        #     print(file.name)
        #     print(file.hash)
        #     raise Exception("something went wrong")
        res += "\""+file.path + "\",\"" + file.name + "\",\"" + file.hash + "\"\n"


    addLine(outputcsv,res)
def readDir(directory,outputcsv):
    clearFile(outputcsv)
    if (directory[len(directory)-1] == "/"):
        directory = directory[0:len(directory)-1]
    threads = []
    for dirname, dirnames, filenames in os.walk(directory+'/.'):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            os.path.join(dirname, subdirname)

        # handleDir(dirname,filenames,outputcsv)
        threads.append(threading.Thread(target=handleDir, args=[dirname,filenames,outputcsv]))
        threads[-1].start()


        if '.git' in dirnames:
            dirnames.remove('.git')
    print("threads: ",len(threads))
    for i in threads:
        i.join()

def readCsv(outputcsv,movetotrash = False,interative = False):
    reader = None
    sortedlist = []
    with open(outputcsv,"r") as f:
        reader = csv.reader(f, delimiter=",")
        sortedlist = sorted(reader, key=lambda row: (row[2], row[0]), reverse=False)
    finishList = []
    if len(sortedlist) == 0:
        print("something went wrong")
        return

    if sortedlist[0][2] == sortedlist[1][2]:
        i = 0
        finishList.append("\""+sortedlist[i][0] + "\",\"" + sortedlist[i][1] + "\",\"" + sortedlist[i][2] + "\"\n")
    currentFile = []
    for i in range(1, len(sortedlist) - 1):
        if (sortedlist[i][2] == sortedlist[i + 1][2] and sortedlist[i][2] != "Unknown"):
            if movetotrash:
                send2trash(sortedlist[i][0])
            elif interative:
                if (currentFile == []):
                    currentFile.append(sortedlist[i])
                elif currentFile[0][2] == sortedlist[i][2]:
                    currentFile.append(sortedlist[i])
                elif len(currentFile) > 1:
                    print("Files to move to trash")
                    for i in range(len(currentFile)):
                        print(i,") ",currentFile[i][0], " (",currentFile[i][1],") ")
                    print(len(currentFile),")  move on to next file")
                    ans = input("")
                    while True:
                        if (ans == "e"):
                            print("Moving on")
                            break
                        while not ans.isnumeric():
                            print("please give only a number")
                            ans = input("")
                        while not int(ans) <= len(currentFile):
                            print("that number is out of bounds")
                            ans = input("")
                        ans = int(ans)
                        if (ans == len(currentFile)):
                            print("Moving on")
                            break
                        send2trash(sortedlist[i][ans])
                        print(currentFile[i][ans], "Removed")
                    currentFile = []

                else:
                    currentFile = []


        if (sortedlist[i][2] == sortedlist[i - 1][2] or sortedlist[i][2] == sortedlist[i + 1][2]):
            finishList.append(str("\""+sortedlist[i][0] + "\",\"" + sortedlist[i][1] + "\",\"" + sortedlist[i][2] + "\"\n"))
    if sortedlist[-1][2] == sortedlist[-2][2]:
        i = len(sortedlist) - 1
        finishList.append("\""+sortedlist[i][0] + "\"," + sortedlist[i][1] + "\",\"" + sortedlist[i][2] + "\"\n")
    with open(outputcsv+"out.csv","w") as f:

        # writer = csv.writer(f)
        # writer.writeheader()
        for row in finishList:
            f.write(row)
def main():
    if (len(sys.argv) < 2):
        return
    # readDir(sys.argv[1], sys.argv[2])
    readCsv(sys.argv[2],False, True)





if __name__ == "__main__":
    t = time.time()
    main()
    print(time.time()-t)