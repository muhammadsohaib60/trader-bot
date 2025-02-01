import ntplib
from time import ctime
c = ntplib.NTPClient()
response = c.request('europe.pool.ntp.org', version=3)
response.offset
-0.143156766891
response.version
3
ctime(response.tx_time)
'Sun May 17 09:32:48 2009'
>>> ntplib.leap_to_text(response.leap)
'no warning'
>>> response.root_delay
0.0046844482421875
>>> ntplib.ref_id_to_text(response.ref_id)
193.190.230.66