# Open-Source IS-IS Configuration Labs

This repository contains _netlab_ topology files for a series of IS-IS hands-on labs that will help you master numerous aspects of EBGP,  IBGP, and BGP routing policy configuration on a platform of your choice[^PC]. You can run them on [your laptop](https://netlab.tools/install/ubuntu-vm/) (including [Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon.html)), on a [local server](https://netlab.tools/install/ubuntu/), in the [cloud](https://netlab.tools/install/cloud/), or in a (free) [GitHub codespace](https://isis.bgplabs.net/4-codespaces/).

The initial lab exercises cover:

* [Work with FRRouting](basic/0-frrouting)
* [Start the IS-IS Routing for IPv4](basic/1-simple-ipv4)
* [Explore IS-IS Data Structures](basic/2-explore)
* [IS-IS on Point-to-Point Links](basic/3-p2p)
* [Using IS-IS Metrics](basic/4-metric)
* [Dual-Stack (IPv4+IPv6) IS-IS Routing](basic/5-ipv6)
* [Optimize Simple IS-IS Deployments](basic/6-level-2)
* [Running IS-IS Over IPv4 Unnumbered and IPv6 LLA-only Interfaces](basic/7-unnumbered)

The next set of exercises covers individual IS-IS features:

* [Passive IS-IS Interfaces](feature/1-passive)
* [Influence the Designated IS Election](feature/2-dis)
* [Protect IS-IS Routing Data with MD5 Authentication](feature/3-md5)
* [Hide Transit Subnets in IS-IS Networks](feature/4-hide-transit)
* [Drain Traffic Before Node Maintenance](feature/5-drain)
* [Adjust IS-IS Timers](feature/6-timers)
* [Route Redistribution into IS-IS](feature/7-redistribute)
* [Use BFD to Speed Up IS-IS Failure Detection](feature/8-bfd)

Interested in advanced concepts? How about:

* [Multilevel IS-IS Deployments](advanced/1-multilevel)
* [Distributing Level-2 IS-IS Routes into Level-1 Areas](advanced/2-route-leak)
* [Summarizing Level-1 Routes into Level-2 Backbone](advanced/3-summarization)
* [Suboptimal IS-IS Intra-area Routing](advanced/4-suboptimal)

Ready for a challenge? Try to solve these lab exercises:

* [Build an SR-MPLS Network with IS-IS](advanced/10-sr)
* [Configure IS-IS Fast Reroute Using TI-LFA](advanced/11-ti-lfa)

See [lab documentation](https://isis.bgplabs.net/) for more details and the [complete list of planned labs](https://isis.bgplabs.net/3-upcoming/). Follow [blog.ipspace.net](https://blog.ipspace.net/) or [Ivan Pepelnjak on LinkedIn](https://www.linkedin.com/in/ivanpepelnjak/) to find out when they will be ready.

[^PC]: Some assembly required: while the FRRouting, SR Linux, and VyOS containers are easy to download, you'll have to build a Vagrant box or install a Docker container image for other platforms.
