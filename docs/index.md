---
title: Labs Overview
---
# Open-Source IS-IS Configuration Labs

This series of hands-on labs will help you master the IS-IS routing protocol configuration on a [platform of your choice](https://netlab.tools/platforms/#platform-routing-support)[^PC], including:

* Arista EOS
* Cisco ASAv, IOSv, IOS XE, IOS XR and Nexus OS
* FRRouting
* Dell OS10
* Juniper vSRX, vMX and vPTX
* Nokia SR OS and SR Linux
* Vyatta VyOS

[^PC]: Some assembly required: the virtual machines or containers that we recommend to use as external IS-IS speakers are easy to download, but you'll have to build a Vagrant box or install a vendor-supplied Vagrant box or Docker container image for most other platforms. See [installation and setup](1-setup.md) for details.

!!! tip
    If this is your first visit to this site, you should start with the [Installation and Setup](1-setup.md) documentation or [run labs in GitHub codespaces](4-codespaces.md).

The initial lab exercises will help you configure basic IS-IS features:

* [Work with FRRouting](basic/0-frrouting.md) (optional)
* [Start the IS-IS Routing for IPv4](basic/1-simple-ipv4.md)
* [Explore IS-IS Data Structures](basic/2-explore.md)
* [IS-IS on Point-to-Point Links](basic/3-p2p.md)
* [Using IS-IS Metrics](basic/4-metric.md)
* [Dual-Stack (IPv4+IPv6) IS-IS Routing](basic/5-ipv6.md)
* [Optimize Simple IS-IS Deployments](basic/6-level-2.md)
* [Running IS-IS Over IPv4 Unnumbered and IPv6 LLA-only Interfaces](basic/7-unnumbered.md)<!--new-->

The next set of exercises covers individual IS-IS features:

* [Passive IS-IS Interfaces](feature/1-passive.md)
* [Influence the Designated IS Election](feature/2-dis.md)
* [Protect IS-IS Routing Data with MD5 Authentication](feature/3-md5.md)<!--new-->
* [Hide Transit Subnets in IS-IS Networks](feature/4-hide-transit.md)<!--new-->
* [Drain Traffic Before Node Maintenance](feature/5-drain.md)<!--new-->
* [Adjust IS-IS Timers](feature/6-timers.md)<!--new-->
* [Route Redistribution into IS-IS](feature/7-redistribute.md)<!--new-->
* [Use BFD to Speed Up IS-IS Failure Detection](feature/8-bfd.md)<!--new-->

Interested in advanced concepts? How about:

* [Multilevel IS-IS Deployments](advanced/1-multilevel.md)<!--new-->
* [Distributing Level-2 IS-IS Routes into Level-1 Areas](advanced/2-route-leak.md)<!--new-->

Ready for a challenge? Try to solve these lab exercises:

* [Build an SR-MPLS Network with IS-IS](advanced/10-sr.md)<!--new-->
* [Configure IS-IS Fast Reroute Using TI-LFA](advanced/11-ti-lfa.md)<!--new-->

Want to know what other advanced labs we have planned? Check the [Upcoming Lab Exercises](3-upcoming.md) document.
