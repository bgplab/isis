from box import Box
from netsim.data import append_to_list

def init(topology: Box) -> None:
  if not topology.get('sr',None):
    return

  append_to_list(topology.groups.routers,'module','sr')
  topology.pop('sr',None)

  if 'message' not in topology:
    topology.message = ''

  topology.message += f'''
SR-MPLS is already configured in your lab.
'''
