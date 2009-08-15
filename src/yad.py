#!/usr/bin/env python

import time
import urllib2
import os,sys
from threading import Thread,Semaphore

'''
TODO
Always pause and resume the downloads
proxy support
'''

class Download:
    def __init__(self):
        self.headers = {	
    	    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1',
    	    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        	'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
	        'Accept-Language': 'en-us,en;q=0.5',
        } # connection headers 
        self.block_size=1024 # default block size
        self.threads = 4 # default number of threads
        self.semaphore = Semaphore(self.threads) # counting Semaphore with value equal to number of threads
        self.debug=False # if debug run
        self.working=True # for threads to work
        self.thread_objs=[] # for holding thread objects
        self.download_done={} # for holding downloaded blocks of individual threads 
        self.resume_support=None # if server supports part downloads 

    def getInfo(self,url):
        request = urllib2.Request(url,None,self.headers) # create the request object
        data = urllib2.urlopen(request) # make a request
        if self.debug:
            print data.info()
        return data.info() # return info about request

    def checkResumeSupport(self,info):
        if info.get('Accept-Ranges',None):
            self.resume_support=True # set resume support
        else:
            print "Server Does not support multiple downloads, using just 1 Thread"
            self.resume_support=False # set resume support
            self.threads=1 # set number of threads to one
            del(self.semaphore) # delete old semaphore object
            self.semaphore = Semaphore(1) # set new semaphore object with value =1

    def createThreads(self,url,filename,size,resume=0):
        '''
            creates normal download threads if not  resume, creates resume threads if resume is set
        '''
        #TODO - add support for resume if different number of threads are used in initial and current download
        start=0
        for i in xrange(0,self.threads):
            try:
                cur_size = os.stat(filename+"-part-"+str(i)).st_size # get size of the current file
                cur_start = start+cur_size # set curret start equal to start plus the current size
                print "resuming download of part-" +str(i)
            except:
                cur_start = start
            if cur_start>(start+size): # if download of current part file is finished
                continue # continue to next part
            thr = DownloadThread(url, # url of file
                           filename, # filename
                           cur_start, # start of download
                           start+size, # size of download
                           self,
                           i) # thread number
            start+=size # set start for next thread
            start+=1 # increment because we already downloaded the previous byte
            self.thread_objs.append(thr) # add to the list of threads
            thr.start() # start the thread

    def download(self,url,filename=None):
        if not filename:
            filename = url.split("/")[-1] # if filename is not set we set a filename
        serverInfo = self.getInfo(url) # get info about the server
        self.checkResumeSupport(serverInfo) # check if resume is supported
        #print serverInfo #CHECK
        length = serverInfo.get('Content-length',None) # get the length of file to be downloaded
        if length:
            size = int(length)/self.threads # get size of each part
            self.createThreads(url,filename,size) # create thread objects
            info = DownloadInfo(self) # DownloadInfo obj for displaying status info about current download
            info.start() # start the status display thread
            print "Started %d thread(s)" %(self.threads,)
            for i in xrange(0,self.threads):
                self.semaphore.acquire() # acquire semaphores self.threads times to make sure all threads are done downloading
                # TODO - find a better way for above, for any number of threads
            self.working=False # stop the DownloadInfo thread
            print "\nDownload Finished at %s\nJoining Part Files..." %(time.asctime(),)
            stream = open(filename,'wb') # open the main file
            for i in xrange(0,self.threads):
                file_stream=open(filename+"-part-"+str(i),'rb') # open the part file
                data = file_stream.read() # read data from part file
                while(data):
                    stream.write(data) # write data to the main file
                    data = file_stream.read() # read data from part file
                file_stream.close() # close the part file
                if self.debug:
                    print "combined file -> %d" %(i+1,)
            for i in xrange(0,self.threads): # remove part file after all other files have been added to the main file
                os.remove(filename+"-part-"+str(i)) # remove the part file
            print "Part Files Combined"
        else:
            print "Sorry cannot proceed, download lenght zero\nPlease check your link"


class DownloadThread(Thread):
    def __init__(self,url,filename,start_byte,end_byte,options,num):
        Thread.__init__(self) # call Thread's __init__ method
        self.options=options # set options
        self.options.semaphore.acquire() # acquire the semaphore
        if self.options.debug:
            print "Semaphore acquired by thread-%d" %(num,)
        self.url=url # set the url
        self.filename=filename # set the filename
        self.start_byte=start_byte # set the start byte for download
        self.end_byte=end_byte # set the end byte for download
        self.thread_num=num # set thread number
        self.options.download_done[num]=0 # for finding number of blocks downloaded by each thread

    def _download(self):
        self.options.headers["Range"]="bytes=%d-%d" %(self.start_byte,self.end_byte) # adding byte range in header
        if self.options.debug:
            print "Thread %d bytes=%d-%d" %(self.thread_num,self.start_byte,self.end_byte)
        request = urllib2.Request(self.url,None,self.options.headers) # making the request
        data = urllib2.urlopen(request)
        stream = open(self.filename+"-part-"+str(self.thread_num),'ab') # naming the file as part <number>
        while self.options.working: # if download is not cancled
            before=time.time() # time when we started to download the current block
            data_block = data.read(self.options.block_size) # download the data of size block_size
            after = time.time() # time when we finished downloading the block
            data_block_len=len(data_block) # length of the downloaded data
            if data_block_len==0:
                break # if length is 0 we stop the download
            stream.write(data_block) # write the data to file
            self.options.download_done[self.thread_num]+=1 # increase the number of downloaded block by this thread
            speed = data_block_len/((after-before)*1024) # to claculate speed
            if self.options.debug:
                print u'\rThread-%d speed -> %d' %(self.thread_num+1,speed), # print speed of thread if debug enabled
        stream.close() # close the stream
        print "Thread-%d Done" %(self.thread_num+1,) # announce the finishing of this thread
        self.options.semaphore.release() # release the semaphore
        if self.options.debug:
            print "Semaphore released by Thread-%d" %(self.thread_num+1,)
        return 0
   
    def run(self):
        num =1
        while num:
            try:
                num = self._download()
            except:
                print "Error Occurred in Thread-%d retrying..." %(self.thread_num+1,)


class DownloadInfo(Thread):
    def __init__(self,download_obj,interval=2):
        Thread.__init__(self) # call Thread's __init__ method
        self.download_obj = download_obj # the download object
        self.interval=interval # number of seconds to sleep after each update

    def run(self):
        # below bytes reffer to KiB, that is block size
        # TODO change this to block size from KiB
        print "Download started at %s" %(time.asctime()) # print the start time
        start_time=time.time() # set start_time
        prev_downloaded_bytes=0 # set previous downloaded bytes
        while self.download_obj.working: # check if everything still working
            time.sleep(self.interval) # sleep for self.interval seconds
            downloaded_bytes=0 # reset number of bytes downloaded during last sleep
            for i in self.download_obj.download_done.keys():
                try: # if one part is already done if we access that we will get an error
                    downloaded_bytes += self.download_obj.download_done[i] # get total blocks from all threads
                except: # on error do nothing just continue
                    pass
            cur_speed = (downloaded_bytes - prev_downloaded_bytes)/self.interval # get current speed
            cur_time = time.time() - start_time # get total time difference
            avg_speed = downloaded_bytes/cur_time # average speed
            print "\rcurrent speed -> %s KiB/sec Avg speed -> %s KiB/sec" %(cur_speed,int(avg_speed))
            prev_downloaded_bytes=downloaded_bytes # set current downloaded bytes as previous for next cycle
        cur_time= time.time() - start_time
        avg_speed=downloaded_bytes/cur_time
        print "Download finished in %s sec with avg speed of %s KiB/sec" %(int(cur_time),int(avg_speed))


if __name__=="__main__":
    usage = "usage :-\n\t./yad.py <url to download> [<filename>]"
    d = Download() # create the download object
    if len(sys.argv) < 2: # check if we have all arguments or not
        print usage
    else:
        do_download=0 # clear initialy for no downloads
        if len(sys.argv) ==3:
            filename = sys.argv[2]
        else:
            filename = sys.argv[1].split("/")[-1] # generate the file name from url
        main_file=None # clear initially
        part_file=None # clear initially
        try:
            main_file = os.stat(filename) # check for main file
            part_file = os.stat(filename+"-part-0") # check for part file
        except:
            pass

        if main_file and part_file: # if main file and part file exists
            print "previous download found will try to continue/resume it"
            do_download=1 # set as we need to download
        elif main_file: # if only the main file exists
            user_action = raw_input("file ' "+filename+" ' already exists do you want to overwrite[y/n] ") # ask user if he wants to overwrite
            while user_action != "y" and user_action != "n" and user_action != "Y" and user_action != "N": # ask until user answers y or n
                user_action = raw_input("file ' "+filename+" ' already exists do you want to overwrite[y/n] ") # ask user if he wants to overwrite
            if user_action == "y": # overwrite the file
                do_download=1 # set to proceed download, will overwrite automatically
            else:
                print "\n\nDownload cancled\nplease select other filename for download\n"+usage
                sys.exit(1) # exit if not overwrite
        else:
            do_download=1 # if main file and resume file do not exists, set as we need to download
        
        if do_download:
            d.download(sys.argv[1],filename) # download the file
