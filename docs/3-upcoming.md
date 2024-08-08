# Upcoming Labs

The [first few labs are already online](index.md); the list of ideas is much longer. Here they are:

## Getting Started

IS-IS on Point-to-Point Links
: * Explore how long it takes for IS-IS to establish adjacency
  * Examine the IS-IS database; notice the pseudonodes and DIS.
  * Change a link to a point-to-point link
  * Configure 3-way handshake if available
  * Examine the changes in adjacency setup time and the reduced information in the topology database (no pseudonode).

Using IS-IS Metrics
: * Change IS-IS metrics to avoid a backup link
  * Explain narrow and wide metrics.
  * If available, test the transitional and wide metrics

Dual-Stack IS-IS Routing
: * Enable IS-IS for IPv4 and IPv6
  * Explore single-topology and multi-topology behavior

Optimize IS-IS Adjacencies
: * Change the IS-type to L2-only
  * Explain the difference between L1+L2 and L2-only adjacencies

Troubleshoot IS-IS Adjacencies
: This lab will include the most common mistakes that prevent an IS-IS adjacency from forming, including:

  * MTU mismatch
  * L1/L2 mismatch
  * Area mismatch on L1 adjacency
  * 3-way handshake on point-to-point links

## Configure IS-IS Features

Passive IS-IS Interfaces
: * Explain the need for passive interfaces
  * Configure passive IS-IS interfaces
  * If available, turn off the advertisement of inter-router prefixes

Influence the Designated IS Election
: * Explain the need for DIS priority
  * Configure DIS priority on a router

Protect IS-IS Adjacencies with MD5 Authentication
: * Configure IS-IS area- and interface passwords

Route Redistribution into IS-IS
: * Configure static route and connected interface redistribution into IS-IS

Fast IS-IS Failure Detection and Convergence
: * Configure IS-IS timers
  * Use BFD

## Advanced Labs

Multi-Level IS-IS Networks
: * Explain intra-area and inter-area routing
  * Configure a network with multiple areas and L1/L2 routers

Graceful Shutdown with IS-IS Overload Bit
: * Configure IS-IS overload bit or maximum metric to drain traffic from a transit router

Build an SR-MPLS Network with IS-IS
: * Build a BGP-free MPLS core using SR-MPLS with IS-IS

Configure IS-IS Fast Reroute Using TI-LFA
: * In a triangle network, configure the longer path as a backup path

Using IS-IS with SRv6
: * Build a BGP-free IPv6 core using SRv6 for end-to-end transport