import os

from netsim import __version__
from netsim.utils import log,strings
from netsim.augment import devices
from box import Box

def pre_transform(topology: Box) -> None:
  f_list = []

  for node,n_data in topology.nodes.items():
    if 'routing' not in n_data.get('module',[]):
      continue

    features = devices.get_device_features(n_data,topology.defaults)
    if 'routing.static' in features:
      continue

    f_list += [ f'{node}({n_data.device})' ]
    if 'routing' not in features:
      n_data.module = [ m for m in n_data.module if m != 'routing' ]
    
    n_data.pop('routing.static')

  if not f_list:
    return

  if 'message' not in topology:
    topology.message = ''

  topology.message += f'''
netlab cannot configure static routes on {", ".join(f_list)}.
You'll have to configure them manually.
'''
