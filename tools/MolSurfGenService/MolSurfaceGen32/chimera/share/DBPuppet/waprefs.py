#
# Initialize web access preferences
#

## name of category
WEBACCESS_PREF = "Web Access"

## actual preferences..
WA_ACCEPT_DATA   = "Accept web data"
WA_TRUSTED_HOSTS = "Trusted hosts"
# preference controls for proxy settings
WA_PROXY = "Use HTTP proxy"
WA_PROXY_HOST = "Proxy server"
WA_PROXY_PORT = "Proxy port"

WA_WARN_LEVEL    = "Confirm open of commands or code"
WA_WARN_ONCE     = "once per session"
WA_WARN_ALWAYS   = "each time"
WA_WARN_NEVER    = "never"

from chimera import tkoptions, preferences

class AskAgainOption(tkoptions.SymbolicEnumOption):
	labels = WA_WARN_ONCE, WA_WARN_ALWAYS, WA_WARN_NEVER
	values = (1, 2, 3)

def _proxyChangeCB(opt=None):
	if opt is None:
		doProxy = preferences.get(WEBACCESS_PREF, WA_PROXY)
	else:
		doProxy = opt.get()
	import os
	if doProxy:
		os.environ['http_proxy'] = "http://" + preferences.get(WEBACCESS_PREF, WA_PROXY_HOST) + ":" + str(preferences.get(WEBACCESS_PREF, WA_PROXY_PORT))
		os.environ['HTTP_PROXY'] = os.environ['http_proxy']
	else:
		try:
			del os.environ['http_proxy']
			del os.environ['HTTP_PROXY']
		except KeyError:
			pass
	import urllib
	urllib._urlopener = None # clear cached instance

_webAccessPrefs = {
	WA_WARN_LEVEL:
		(AskAgainOption, 1, None),
	WA_PROXY:
		(tkoptions.BooleanOption, False, _proxyChangeCB, {"balloon": 'Use HTTP proxy to connect to the internet\nthrough a firewall.'}),
	WA_PROXY_HOST:
		(tkoptions.StringOption, "", None, {"balloon": "Proxy server's IP address or host name"}),
	WA_PROXY_PORT:
		(tkoptions.IntOption, 80, None, {"balloon": 'Proxy port number'})
}

_waPreferencesOrder = [ WA_WARN_LEVEL, WA_PROXY, WA_PROXY_HOST, WA_PROXY_PORT ]
import sys
if sys.platform != 'darwin':
        import DBPuppet
	_webAccessPrefs[WA_ACCEPT_DATA] = (tkoptions.BooleanOption, 1,
						DBPuppet.activate_puppet)
	_waPreferencesOrder.insert(1, WA_ACCEPT_DATA)
def _init():
	preferences.register(WEBACCESS_PREF, _webAccessPrefs)
	preferences.setOrder(WEBACCESS_PREF, _waPreferencesOrder)
	from DBPuppet import run_puppet
	if sys.platform == 'darwin':
		run_puppet(True)
	else:
		onoff = preferences.get(WEBACCESS_PREF, WA_ACCEPT_DATA)
		run_puppet(onoff)
import chimera
if not chimera.nogui:
	## Since DBPuppet uses TCL ports to listen, it's not
	## available in nogui mode where there is no tcl event loop
	chimera.registerPostGraphicsFunc(_init)
