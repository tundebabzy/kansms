#!/usr/bin/env python
# vim:tabstop=4:noexpandtab


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import urlparse
import urllib2
import urllib
import re
from bs4 import BeautifulSoup
from lxml import etree

class SmsSender(object):
    """
    Other SmsSender classes should inherit from this class and at least
    over ride the send method. This class is meant to make a call to an
    sms gateway through its api protocol and return the response in a
    nice format for further processing.
    """
	def __init__(self, username, password, charset="utf-8", coding=2, server="localhost", port=13013):
		self.un = username
		self.pw = password
		self.charset = charset
		self.coding = coding
		self.server = server
		self.port = port
		self.buffer = []

    def send(self):
        """ over ride me """
        raise Exception
        
class RoutesmsSmsSender(SmsSender):
    def __init__(self, username, password, msg_type="0", dlr="0", server="localhost", port=13013):
        self.un = username
        self.pw = password
        self.msg_type = msg_type
        self.dlr = dlr
        self.server = server
        self.port = port
        self.text = None

    def send(self, message_instance_list, sent_by):
        """
        RouteSMS exposes an SMPP api via http. This function will build
        the url containing all the needed parameters and open the site
        """
        self.delivery_list = []
        source = sent_by
        
        for i in xrange(len(message_instance_list)):
            message = message_instance_list[i]
            if self.text:
                pass
            else:
                self.text = urllib.quote(message.message)
                
            # build a list that we will convert to a comma separated string later on
            self.delivery_list.append(message.destination)

        destination = ','.join(self.delivery_list)
        destination = urllib.quote(destination)

        # Sorry for the next very loong line....I just have to else there'll be errors
        request = urllib2.Request('http://%s:%s/bulksms/bulksms?username=%s&password=%s&type=%s&dlr=%s&destination=%s&source=%s&message=%s' %(self.server, self.port, self.un, self.pw, self.msg_type, self.dlr, destination, source, self.text),
                                    headers={'Content-Type':'application/xml', 'Cache-Control':'no-cache',
                                  'Pragma':'no-cache'}
                    )

        try:
            res = urllib2.urlopen(request).read()
            status = self.analyse_response(res)
            return status
            
        except urllib2.HTTPError as e:
            #print 'HTTPError'
            #print e.code
            pass 

        except urllib2.URLError as e:
            #print 'URLError'
            #print e.reason
            pass 

        except IOError:
            pass 
            
        except Exception as e:
            #print 'other error'
            #print e
            pass

        return [('','')]
            
    def analyse_response(self, response):
        """
        ROutesms will reply with something like this:
        <4 DIGIT CODE>|<CELL NUM>|<MESSAGE ID>
        This function will extract the 4 digit code and the cell num
        """
        res = []
        data = response.split(',')
        for i in data:
            temp = i.split('|')
            res.append((temp[0], temp[1]))
        return res
            
class InfobipSmsSender(SmsSender):
    def send(self, message_instance_list, sent_by, buffer=False):
        """
        Builds infobip xml tree and POSTs to the api. It returns a list
        of tuples:
        [(0, 2347007007000), (0, 2348038038003)]
        where in each tuple, tuple[0] = status returned by infobip and
        tuple[1] = destination number of the sms
        """
        self.text = None
        sms = etree.Element('SMS')
        
        authentication = etree.SubElement(sms, 'authentication')
        username = etree.SubElement(authentication, 'username')
        username.text = self.un
        password = etree.SubElement(authentication, 'password')
        password.text = self.pw
        
        message = etree.SubElement(sms, 'message')
        sender = etree.SubElement(message, 'sender')
        sender.text = sent_by

        text = etree.SubElement(message, 'text')
        recipients = etree.SubElement(sms, 'recipients')

        for i in xrange(len(message_instance_list)):
            message = message_instance_list[i]
            if self.text:
                pass
            else:
                self.text = urllib.quote(message.message) # cos message is the same for all the instances
                text.text = self.text
            gsm = etree.SubElement(recipients, 'gsm')
            gsm.text = message.destination

        xml = etree.tostring(sms)

        parameters = 'XML=%s' %xml
        # Yeah i know you might cringe cos i'm hardcoding the url :p
        request = urllib2.Request('http://api.infobip.com/api/v3/sendsms/xml',data=parameters,
                        headers={'Content-Type':'application/xml', 'Cache-Control':'no-cache',
                                  'Pragma':'no-cache'})
        
        try:
            res = urllib2.urlopen(request).read()
            status = self.analyse_response(res)
            return status
        except urllib2.HTTPError as e:
            #print e.code
            pass 

        except urllib2.URLError as e:
            #print e.reason
            pass 

        except Exception as e:
            #print e
            pass

        except IOError:
            pass 

        return [('','')]
        
    def analyse_response(self, response):
        """
        Infobip sends it response with xml (but there's also a json
        # response. However, I choose the xml so this method will parse
        # the return xml and we will build a tuple containing the
        # status for each message sent
        Sample xml reply from infobip is:
        ...
        <results>
            <result>
                <status>0</status>
                <messageid>0225</messageid>
                <destination>2348058008000</destination>
            </result>
            <result>
                <status>0</status>
                <messageid>0226</messageid>
                <destination>2348058008001</destination>
            </result>
        </results>

        analyse_response() will extract for each result tag the child
        status and destination tags and return them as a tuple of tuple
        """
        res = []
        soup = BeautifulSoup(response)
        stat_and_dest = soup.find_all(['status', 'destination'])
        for x in range(0, len(stat_and_dest), 2):
            res.append((stat_and_dest[x].string, stat_and_dest[x+1].string))
            
        return res


class SmsReceiver():
	class RequestHandler(BaseHTTPRequestHandler):
		def do_GET(self):
			try:
				# all responses from this handler are pretty much the
				# same - an http status and message - so let's abstract it!
				def respond(code, message=None):
					self.send_response(code)
					self.end_headers()

					# recycle the full HTTP status message if none were provided
					if message is None: message = self.responses[code][0]
					self.wfile.write(message)
					self.wfile.close()

				# explode the URI to pluck out the
				# query string as a dictionary
				parts = urlparse.urlsplit(self.path)
				vars = cgi.parse_qs(parts[3])

				# if this event is valid, then thank kannel, and
				# invoke the receiver function with the sms data
				if vars.has_key("sender") and vars.has_key("message"):
					caller = re.compile('\D').sub("", vars["sender"][0])
					self.server.receiver(caller, vars["message"][0])
					respond(200, "SMS Received OK")

				# the request wasn't valid :(
				else: respond(400)

			# something went wrong during the
			# request (probably within the receiver),
			# so cause an internal server error
			except:
				respond(500)
				raise

		# we don't need to see every request in the console, since the
		# app will probably log it anyway. note: errors are still shown!
		def log_request(self, code="-", size="-"):
			pass

	def __init__(self, receiver, port=4500):
		handler = self.RequestHandler
		self.serv = HTTPServer(("", port), handler)
		self.serv.receiver = receiver

	def run(self):
		self.serv.serve_forever()
