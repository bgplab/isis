import os

from netsim import __version__
from netsim.utils import log,strings
from netsim.augment import devices
from box import Box

def pre_transform(topology: Box) -> None:
  if __version__ >= '25.09':
    return

  l_list = []
  for link in topology.get('links',[]):
    if 'isis.type' in link:
      l_name = '->'.join([ intf.node for intf in link.interfaces ])
      l_name = f'{l_name} ({link.isis.type})'
      l_list.append(l_name)

  if not l_list:
    return

  topology.message = topology.get('message','') + f'''
The version of netlab you're using cannot IS-IS circuit type on links
{", ".join(l_list)}.

You'll have to configure them manually.
'''
