import os

from netsim import __version__
from netsim.utils import log,strings
from box import Box

def init(topology: Box) -> None:
  if not topology.get('validate',None):
    return

  v_version = topology.get('_validate_version','1.8.4')
  if __version__ >= v_version:
    return

  topology.pop('validate',None)
  if 'message' not in topology:
    topology.message = ''

  topology.message += f'''
Upgrade to netlab release {v_version} to use 'netlab validate' command to
check the results of your configuration work.
'''

  return

def post_transform(topology: Box) -> None:
  if not topology.get('validate',None):
    return

  if 'message' not in topology:
    topology.message = ''

  # Find the most relevant device group
  v_groups = [ topology.groups[grp] for grp in ['validate','external'] if grp in topology.groups ]
  if not v_groups:
    return
  
  v_group = v_groups[0]
  x_device = v_group.get('device',None)
  if x_device is None:
    n_devices = list(set([ topology.nodes[node].device for node in v_group.members ]))
    if not n_devices:
      return
    x_device = n_devices[0]

  v_dlist = topology.validate[0].devices
  if x_device in v_dlist:
    topology.message += '''
You can use the 'netlab validate' command to check whether you successfully
completed the lab exercise.
'''
    return
  
  v_nodes = ", ".join(v_group.members)
  topology.message += "\n".join(strings.wrap_text_into_lines(
    f"\nYou're using {x_device} on {v_nodes}. " + \
    "Lab validation is not yet supported on that device. If you want to use 'netlab validate' command, " + \
    f'use one of these devices on {v_nodes}: {", ".join(v_dlist)}',width=80))
