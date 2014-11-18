import requests
import json
import sys

def convert(fromC, toC):
	url="http://www.freecurrencyconverterapi.com/api/v2/convert?q=%s_%s&compact=y" % (fromC, toC)
	get=requests.get(url)
	data=get.text
	return data

if len(sys.argv) < 3:
	print "Usage : \n  Python %s currency currency [amount]" % sys.argv[0]
	print "Example : \n  python %s USD MYR 20" % sys.argv[0]
	sys.exit()

fromC = None
toC = None

if len(sys.argv) < 4:
	valT = 1
else:
	valT = float(sys.argv[3])

fromC = sys.argv[1].upper()
toC = sys.argv[2].upper()


data = convert(fromC, toC)
data2 = convert(toC, fromC)

jdata=json.loads(data)
jdata2=json.loads(data2)

finalD = float(jdata['%s_%s' % (fromC, toC)]['val'])*valT
finalD2 = float(jdata2['%s_%s' % (toC, fromC)]['val'])*valT

print "-"*20
print "%s %s = %s %s" % (valT, fromC, finalD, toC)
print "%s %s = %s %s" % (valT, toC, finalD2, fromC)