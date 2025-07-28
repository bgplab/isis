# Upcoming Labs

A large number of IS-IS labs are [already online](index.md), but we keep getting interesting ideas ([example](https://github.com/bgplab/isis/issues/4)). Here are some of them:

## Configure IS-IS Features

Route Redistribution into IS-IS
: * Configure static route and connected interface redistribution into IS-IS

Fast IS-IS Failure Detection and Convergence
: * Use BFD

## Advanced Labs

Multi-Level IS-IS Networks
: * Explain intra-area and inter-area routing
  * Configure a network with multiple areas and L1/L2 routers
  * Use L2 default routing (based on ATT bit) in L1 areas

Securing Multi-Level Networks at the Interface Level
: * Use interface *circuit-type* to stop L1 or L2 adjacencies from forming
  * Use level-specific passwords

Leaking L2 routes into L1 areas
: * Redistribute L2 routes into L1 areas
  * Combine redistributed routes with default routing

Graceful Shutdown
: * Use 'overload bit' or 'advertise-high-metric' functionality to shift traffic away from a router

Build an SR-MPLS Network with IS-IS
: * Build a BGP-free MPLS core using SR-MPLS with IS-IS

Configure IS-IS Fast Reroute Using TI-LFA
: * In a triangle network, configure the longer path as a backup path

Using IS-IS with SRv6
: * Build a BGP-free IPv6 core using SRv6 for end-to-end transport

Two-Way Redistribution
: * Redistribute routes between OSPF and IS-IS at multiple points
  * Use route filters to prevent routing loops

## Troubleshooting

Troubleshoot IS-IS Adjacencies
: This lab will include the most common mistakes that prevent an IS-IS adjacency from forming, including:

  * MTU mismatch
  * L1/L2 mismatch
  * Area mismatch on L1 adjacency
  * 3-way handshake on point-to-point links

