#!/usr/bin/env python

# Author: Ankur Shrivastava
# mail : ankur [ at ] ankurs [ dot ] com
# License : GPLv3

import time
import urllib2
import os,sys
import getopt # command line argument parser
from threading import Thread,Semaphore

'''
TODO
Always pause and resume the downloads -- DONE (CHECK all cases)
proxy support
user options
remove part file by adding single file seek -- DONE
'''

class Download:
    def __init__(self,id,threads=4,proxy=None):
        '''
        constructor
        id -> helps keep track of all the downloads
        '''
        self.headers = {	
    	    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1',
    	    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        	'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
	        'Accept-Language': 'en-us,en;q=0.5',
        } # connection headers 
        if proxy:
            urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler(proxy))) # set global proxy handler
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor())) # set global cookie processor
        self.block_size=1024 # default block size
        self.threads = threads # total number of threads to use
        self.semaphore = Semaphore(self.threads) # counting Semaphore with value equal to number of threads
        self.debug=False # if debug run
        self.working=True # for threads to work
        self.thread_objs=[] # for holding thread objects
        self.download_done={} # for holding downloaded blocks of individual threads 
        self.resume_support=None # if server supports part downloads 
        self.file_length=0 # total length of file
        self.part_length=0 # length of each part file
        self.datastore = DataStore(self) # CHECK remove this
        self.ID = id # unique id for the thread
        self.info = DownloadInfo(self) # DownloadInfo obj for displaying status info about current download

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
            self.resume_support=False # clear resume support
            self.threads=1 # set number of threads to one
            del(self.semaphore) # delete old semaphore object
            self.semaphore = Semaphore(1) # set new semaphore object with value =1

    def createThreads(self,url,filename,size):
        '''
            creates normal download threads if not resume, creates resume threads if resume is set
        '''
        #TODO - add support for resume if different number of threads are used in initial and current download
        start=0
        for i in xrange(0,self.threads):
            thr = DownloadThread(url, # url of file
                           filename, # filename
                           start, # start of download
                           start+size, # size of download
                           self,
                           i) # thread number
            start+=size # set start for next thread
            start+=1 # increment because we already downloaded the previous byte
            self.thread_objs.append(thr) # add to the list of threads
            thr.start() # start the thread

    def download(self,url,filename=None,folder=None):
        if not filename:
            filename = url.split("/")[-1] # if filename is not set we set a filename
        print "getting server info..."
        serverInfo = self.getInfo(url) # get info about the server
        self.checkResumeSupport(serverInfo) # check if resume is supported
        #print serverInfo #CHECK
        if folder:
            filename = folder + filename # prefix folder name to file name
        length = serverInfo.get('Content-length',None) # get the length of file to be downloaded
        if length:
            self.file_length = int(length) # set the file length
            size = int(length)/self.threads # get size of each part
            if int(size) <1024: # check minimum size
                print "Error: size of each part file is smaller then 1 KiB\nPlease decrease the number of threads"
                sys.exit(1)
            self.datastore.filename=filename # set the file name
            self.datastore.start() # start the datastore thread
            self.part_length = size # set the size of part file
            self.createThreads(url,filename,size) # create thread objects
            self.info.start() # start the status display thread
            print "Started %d thread(s)" %(self.threads,)
            for i in xrange(0,self.threads):
                self.semaphore.acquire() # acquire semaphores self.threads times to make sure all threads are done downloading
                # TODO - find a better way for above, for any number of threads
            self.working=False # stop the DownloadInfo thread
            print "\nDownload Finished at %s" %(time.asctime(),)
        else:
            print "Sorry cannot proceed, download lenght zero\nPlease check your link"
            if self.debug:
                print serverInfo


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
        self.options.download_done[self.thread_num] = 0 # self.options.part_length - (self.end_byte - self.start_byte) CHECK
        # set the data downloaded by this thread to filesize (above) CHECK TODO
        while self.options.working: # if download is not cancled
            before=time.time() # time when we started to download the current block
            data_block = data.read(self.options.block_size) # download the data of size block_size
            after = time.time() # time when we finished downloading the block
            data_block_len=len(data_block) # length of the downloaded data
            if data_block_len==0:
                break # if length is 0 we stop the download
            self.options.datastore.list.append((data_block,self.start_byte)) # CHECK 
            self.options.download_done[self.thread_num]+=1 # increase the number of downloaded block by this thread
            self.start_byte+=data_block_len # increase the start byte by downloaded data's length (if we restart this thread because of error)
            speed = data_block_len/((after-before)*1024) # to claculate speed
            if self.options.debug:
                print u'\rThread-%d speed -> %d' %(self.thread_num+1,speed), # print speed of thread if debug enabled
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

class DataStore(Thread): 
    '''
        used for storing data directly into the file, without using the part files
        TODO -- finalize the working
        CHECK - Do we need a thread for this?
    '''
    def __init__(self,options):
        Thread.__init__(self) # call Thread's __init__ method
        self.list=[] # list for holding dowlnoaded data
        self.options=options # configuration options
        self.file_obj = None # file handler
        self.filename=None # file for the file

    def store(self):
        '''
            stores the data at the mentioned position
        '''
        data,pos= self.list.pop() # retrive the data and position
        self.file_obj.seek(int(pos)) # move to position
        self.file_obj.write(data) # write the data at position

    def run(self):
        self.file_obj = open(self.filename,"wb") # open file where data is to be stored
        time_start = time.time()
        while self.options.working: # while download in progress
            while len(self.list): # while we have data in list
                self.store() # store the data
        self.file_obj.close() # close the file object
        print time.time() - time_start

class DownloadInfo(Thread):
    def __init__(self,download_obj,interval=2):
        Thread.__init__(self) # call Thread's __init__ method
        self.download_obj = download_obj # Download class object to read info from
        self.interval=interval # number of seconds to sleep after each update
        self.cur_speed = 0
        self.avg_speed = 0
        self.ET = 0
        self.progress = 0
        self.length = self.download_obj.file_length
        self.finished = False

    def formatTime(self,seconds):
        ' convert time from seconds to string of hr, min and sec'
        seconds = int(seconds)
        if seconds <60:
            return "%2d sec" %(seconds,)
        elif seconds <3600:
            min = seconds/60
            sec = seconds%60
            return "%2d:%2d min" %(min,sec)
        else:
            hr = seconds/3600
            seconds = seconds%3600
            min = seconds/60
            sec = seconds%60
            return "%d:%2d:%2d hr" %(hr,min,sec)

    def run(self):
        # below bytes reffer to KiB, that is block size
        # TODO change this to block size from KiB
        print "Download started at %s" %(time.asctime()) # print the start time
        start_time=time.time() # set start_time
        prev_downloaded_bytes=0 # set previous downloaded bytes
        time.sleep(2) # wait for download to start, then display the info
        downloaded_bytes=0
        while self.download_obj.working: # check if everything still working
            downloaded_bytes=0 # reset number of bytes downloaded during last sleep
            for i in self.download_obj.download_done.keys():
                try: # we will get erron on access of download info of a already done file ( if resume)
                    downloaded_bytes += self.download_obj.download_done[i] # get total blocks from all threads
                except: # on error do nothing just continue
                    pass
            cur_speed = (downloaded_bytes - prev_downloaded_bytes)/self.interval # get current speed
            cur_time = time.time() - start_time # get total time difference
            avg_speed = downloaded_bytes/cur_time # average speed
            percent = (downloaded_bytes*100*self.download_obj.block_size)/self.download_obj.file_length # calculate the percentage done
            if avg_speed:
                estimated_time = ((self.download_obj.file_length/self.download_obj.block_size) - downloaded_bytes)/avg_speed # calculate estimated time
            else:
                estimated_time = 0 # to prevent divide by zero when avg_speed is zero
            et = self.formatTime(estimated_time) # get the string representation
            print "\rcur-> %s KiB/sec, avg -> %s KiB/sec [%d%%] ET %s" %(cur_speed,int(avg_speed),percent,et),
            self.cur_speed = str(cur_speed) + " Kib/sec"
            self.avg_speed = str(avg_speed) + " Kib/sec"
            self.progress = str(percent) + "%"
            self.ET = et
            sys.stdout.flush() # to flush stdout
            prev_downloaded_bytes=downloaded_bytes # set current downloaded bytes as previous for next cycle
            time.sleep(self.interval) # sleep for self.interval seconds
        cur_time= time.time() - start_time
        avg_speed=downloaded_bytes/cur_time
        print "Download finished in %s  with avg speed of %d KiB/sec" %(self.formatTime(int(cur_time)),int(avg_speed))
        self.cur_speed = str(cur_speed) + " Kib/sec"
        self.avg_speed = str(avg_speed) + " Kib/sec"
        self.progress = "100%"
        self.ET = "0 sec"
        self.finished = True

