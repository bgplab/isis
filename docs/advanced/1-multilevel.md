# Multilevel IS-IS Deployments

By [Dan Partelly](https://github.com/DanPartelly)
{.author-byline }

Like OSPF, IS-IS was designed when router memory was measured in megabytes and CPU speeds in MHz. The scalability of a routing protocol and the reduced memory footprint on the edge (access) routers were crucial. OSPF solved that conundrum with *areas*, and IS-IS solved it with *multi-level* topology; some IS-IS routers know only about prefixes in their area (*level-1* routers), while others know the whole network topology (*level-2* routers), but might not be aware of the internal structure of other areas.

Decent modern IS-IS implementations have no problems running a single-level IS-IS network with hundreds of routers, and the memory requirements are usually a non-issue. However, you might still find edge cases where a multi-level deployment might be beneficial. For example, your edge switches might have small hardware forwarding tables, or you might want to limit the *blast radius* of network failures -- IS-IS limits the LSP flooding to a single area (or the level-2 backbone)[^SPO].

[^SPO]: The flooding of changed LSPs is limited to a single level (area or backbone), but without the L1 → L2 route summarization, the changes in a level-1 area always spill over into the level-2 backbone.

In this exercise, you'll explore multi-level IS-IS deployment using a simple 5-router topology:

![Lab topology](topology-multiarea.png)

## Device Requirements

Use any device [supported by the _netlab_ IS-IS configuration module](https://netlab.tools/platforms/#platform-routing-support) that correctly implements the distribution of intra-area (level-1) routes into inter-area (level-2) backbone.

Unfortunately, this leaves FRRouting off the table. As of August 2025, FRRouting's IS-IS implementation is incomplete and does not propagate level-1 IP prefixes into the level-2 LSP database as required by [RFC 1195](https://datatracker.ietf.org/doc/html/rfc1195). Nevertheless, the implemented parts are solid, and FRR can be used without problems in single-level IS-IS deployments.

## Starting the Lab

You can start the lab [on your own lab infrastructure](../1-setup.md) or in [GitHub Codespaces](https://github.com/codespaces/new/bgplab/isis) ([more details](https://bgplabs.net/4-codespaces/)):

* Change directory to `advanced/1-multiarea`
* Execute **netlab up**
* Log into lab devices with **netlab connect**

## Existing Device Configuration

When starting the lab, _netlab_ configures IPv4 addresses and IS-IS protocol on the lab routers.

All five routers are configured as L2 IS-IS routers, as recommended in [Configure IS-IS Routing for IPv4](../basic/1-simple-ipv4.md). This results in a flat level-2 multi-area topology. Routers use the following areas:

| Node | Router ID | IS-IS Area |
|----------|----------:|--------------------:|
| r1 | 10.0.0.1 | 49.0100 |
| c1 | 10.0.0.2 | 49.0100 |
| c2 | 10.0.0.3 | 49.0100 |
| x1 | 10.0.0.4 | 49.0001 |
| x2 | 10.0.0.5 | 49.0002 |


## Initial Routing Tables

After starting the lab, you should have full reachability between all routers' loopback interfaces.

For example, router R1 has a full topological view of the network. Its routing table is also relatively large, even for our small network of 5 routers. Now imagine a network with hundreds of routers, each advertising tens of networks. Remember that in past times, people were rightfully concerned about the routing (and forwarding) table size in a single-level network, and you can quickly see the need for smaller forwarding tables.

IS-IS routes on R1 running Arista cEOS
{ .code-caption }
```
r1#show ip route isis

VRF: default
Source Codes:
       I L1 - IS-IS level 1,
       I L2 - IS-IS level 2,
....

 I L2     10.0.0.2/32 [115/20]
           via 10.1.0.1, Ethernet1
 I L2     10.0.0.3/32 [115/20]
           via 10.1.0.5, Ethernet2
 I L2     10.0.0.4/32 [115/30]
           via 10.1.0.1, Ethernet1
 I L2     10.0.0.5/32 [115/30]
           via 10.1.0.5, Ethernet2
 I L2     10.1.0.8/30 [115/20]
           via 10.1.0.1, Ethernet1
           via 10.1.0.5, Ethernet2
 I L2     10.1.0.12/30 [115/20]
           via 10.1.0.1, Ethernet1
 I L2     10.1.0.16/30 [115/20]
           via 10.1.0.5, Ethernet2

```

## Initial Optimization: Make R1 a Level-1 Router

Let's see if we can minimize the size of the R1 routing table. Make router R1 a level-1 IS-IS router. The configuration command you need should be pretty familiar (after all, you configured the routers to be level-2 routers in one of the [early lab exercises](../basic/6-level-2.md)).

Examine the R1 routing table once it's configured as a level-1 router.

IS-IS routes on R1 (Arista cEOS) running as a level-1 router
{ .code-caption }
```
r1#show ip route isis

VRF: default
Source Codes:
       I L1 - IS-IS level 1,
       I L2 - IS-IS level 2,
....

```

We lost all IS-IS routes. Let's figure out what went wrong, starting with the IS-IS interfaces and IS-IS adjacencies:

R1 (Arista cEOS) runs IS-IS on two Ethernet interfaces, but has no IS-IS adjacencies
{ .code-caption }
```
r1#show isis interface brief

IS-IS Instance: Gandalf VRF: default

Interface Level IPv4 Metric IPv6 Metric Type           Adjacency
--------- ----- ----------- ----------- -------------- ---------
Loopback0 L1             10          10 loopback       (passive)
Ethernet2 L1             10          10 point-to-point         0
Ethernet1 L1             10          10 point-to-point         0

r1#show isis neighbors
```

Let's restore the lost adjacencies. Before doing that, we need a short detour through the IS-IS adjacency rules to understand why R1 lost all its neighbors.

## Level-1 and Level-2 Adjacency Rules in IS-IS

As already mentioned, IS-IS uses areas (level-1 routing) connected via an overlay inter-area routing topology (level-2 routing). In many ways, the inter-area overlay is similar to an OSPF backbone, but with many significant differences. Every router can participate in intra-area routing (level-1 router), inter-area routing (level-2 router), or both (level-1-2 router).

In OSPF, all inter-area traffic must go through area zero (the backbone area). Any other area must connect to the backbone area, resulting in a strict hierarchical network. Consequently, border routers must have at least one interface in the backbone area.

Compared to OSPF, IS-IS has more flexible requirements. Backbone routers (L2 routers), often referred to as "transit routers" in IS-IS parlance, are not required to be part of a "transit area" or belong to the same area.

The only requirement imposed on an IS-IS transit network is the end-to-end level-2 continuity through L2 adjacencies across all transit routers. Both L2 and L1/L2 routers can ensure the required level-2 continuity.

The rules governing adjacency formation in IS-IS are simple:

* Level-1 (intra-area) routers) only form adjacencies with level-1 or level-1-2 routers in the same area. A direct consequence of this is that they cannot be border routers.
* Level-2 routers form L2 adjacencies with other level-2 routers, or with level-1-2 routers. They can form adjacencies with routers in other areas. This is important; the only way to connect two different areas in IS-IS is through an L2 adjacency.
* Level-1-2 routers can form both L1 and L2 adjacencies. They maintain a separate topological database for each of those levels. They act as border routers and manifest many similarities with the OSPF Area Border Routers.

The adjacency that two routers try to establish depends on their configuration. You can specify the router type in the IS-IS routing process, or limit the adjacency type on a single interface with an interface configuration command. The two parameters limit the IS-IS hellos (ISH) sent through an interface[^EX], thus directly limiting the adjacencies formed through that interface.

[^EX]: For example, you could have a level-1-2 router, but limit an interface to be a level-1 circuit. The router will only send level-1 ISHs on that interface. You can also configure a router to be a level-1 router and limit an interface to be a level-2 circuit, resulting in no ISHs.

## Make C1 and C2 Level-1-2 Routers

Now that you know the rules, it's easy to see why R1 lost its adjacency with C1 and C2. A level-1 router cannot form an adjacency with a level-2 router.

To fix the problem, change the IS-IS router type of C1 and C2 to level-1-2. Again, the command to do that should be familiar by now.

When you are done, check the IS-IS adjacencies on R1 to see if you solved the adjacency problem we found at the end of the previous configuration task.

IS-IS neighbors on R1 running Arista cEOS
{ .code-caption }
```
r1#show isis neighbors

Instance  VRF      System Id        Type Interface          SNPA              State Hold time   Circuit Id
Gandalf   default  c1               L1   Ethernet1          P2P               UP    29          B0
Gandalf   default  c2               L1   Ethernet2          P2P               UP    24          AF
```

As expected, the adjacency problem is solved. Next, check if we managed to reduce the size of the routing table:

IS-IS database on R1 running Arista cEOS
{ .code-caption }
```
r1#show isis database
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 1 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
    r1.00-00                      7  24422   834    118 L1  0000.0000.0001.00-00  <>
    c1.00-00                      4  12846   835    131 L2  0000.0000.0002.00-00  <DefaultAtt>
    c2.00-00                      4  61785   835    131 L2  0000.0000.0003.00-00  <DefaultAtt>

```

You will immediately notice that R1 lost the full topological view of the network. The IS-IS database contains only LSPs originated by C1, C2, and R1.

Finally, examine the R1 routing table:

IS-IS routes on R1 
{ .code-caption }
```
r1#show ip route isis

VRF: default
	 I L1 - IS-IS level 1,
     I L2 - IS-IS level 2,
...
Gateway of last resort:
 I L1     0.0.0.0/0 [115/10]
           via 10.1.0.1, Ethernet1
           via 10.1.0.5, Ethernet2

 I L1     10.0.0.2/32 [115/20]
           via 10.1.0.1, Ethernet1
 I L1     10.0.0.3/32 [115/20]
           via 10.1.0.5, Ethernet2
 I L1     10.1.0.8/30 [115/20]
           via 10.1.0.1, Ethernet1
           via 10.1.0.5, Ethernet2
 I L1     10.1.0.12/30 [115/20]
           via 10.1.0.1, Ethernet1
 I L1     10.1.0.16/30 [115/20]
           via 10.1.0.5, Ethernet2

```

Observe that the type of IS-IS routes changed from L2 to L1, and X1/X2 loopbacks are no longer in the routing table. The routing table accurately reflects the fact that R1 lost visibility of the level-2 network topology. The reduction in the IP routing table size is trivial at the scale of a 5-router lab, but as you can easily imagine, it can be significant in large networks.

Since we're aiming to optimize the R1 routing and not to fragment the network, let's confirm that we still have reachability to routers in other areas:

Inter-area connectivity tests on R1
{ .code-caption }
```
r1#ping 10.0.0.4
PING 10.0.0.4 (10.0.0.4) 72(100) bytes of data.
80 bytes from 10.0.0.4: icmp_seq=1 ttl=63 time=0.479 ms
80 bytes from 10.0.0.4: icmp_seq=2 ttl=63 time=0.144 ms
....

r1#ping 10.0.0.5
PING 10.0.0.5 (10.0.0.5) 72(100) bytes of data.
80 bytes from 10.0.0.5: icmp_seq=1 ttl=63 time=0.801 ms
80 bytes from 10.0.0.5: icmp_seq=2 ttl=63 time=0.345 ms
....

```
 
Despite no longer having a route to X1 and X2's loopbacks, R1 can still reach them.

Astute engineers might have already noticed something interesting in the R1 routing table: an ECMP default route pointing towards C1 and C2. This route is used for L2 default routing, and it's the key to reaching the level-2 backbone and, implicitly, other IS-IS areas.

Let's see how this default route is created.

## L2 Default Routing Mechanics

We'll start our exploration at C1. Here's its level-1 LSP database:

IS-IS level-1 database on C1, running Arista cEOS
{ .code-caption }
```
c1#show isis database level-1
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 1 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
    r1.00-00                     18  32061   726    118 L1  0000.0000.0001.00-00  <>
    c1.00-00                     20   6734  1193    120 L2  0000.0000.0002.00-00  <DefaultAtt>
    c2.00-00                     20   6712  1193    120 L2  0000.0000.0003.00-00  <DefaultAtt>
```

Notice that the LSPs originated by C1 and C2 have the ATT flag set. The full name of this flag is "Attached", and in the words of ISO_IEC_10589_2002, a level-1-2 router considers itself *attached* when

* it can reach at least one other area using the corresponding routeing metric, or
* It has at least one enabled reachable address prefix with the corresponding metric defined.

If a router considers itself attached, it will originate L1 LSPs with the ATT flag set. This has the following effects:

* The ATT flag signals level-1 routers in the same area that the router advertising it can carry traffic to the level-2 backbone and into other areas. The level-1-2 router advertises itself as an exit point from a level-1 area.
* Level-1 routers receiving an LSP with the ATT bit set will insert a default route pointing to the router that sent the LSP into their IP routing table.

Back to the default routes we saw earlier in R1's routing table. In our topology, both C1 and C2 consider themselves attached to the level-2 backbone, and they both originate L1 LSPs with the ATT bit set. 

Router R1 has ECMP enabled by default, so it uses both C1 and C2 as the exit points from the level-1 area and adds two default routes to its IP routing table.

## Distribution of L1 Routes into L2 Backbone

We have already checked that R1 can reach routers in other areas (X1 and X2), but there is another part of the puzzle that needs to be explored: how do X1 and X2 know about R1? After all, they are in different areas, and know nothing about the internal structure of R1's area (49.0100)

IS-IS solves this problem by automatically distributing level-1 prefixes into level-2 LSPs on level-1-2 routers. Straight from RFC 1195:

> Level 2 routers include in their level 2 LSPs a complete list of [IP address, subnet mask, metric] specifying all IP addresses reachable in their area. As described in section 3, this information may be obtained from a combination of the level 1 LSPs (obtained from level-1 routers in the same area) and/or by manual configuration.

Distributing intra-area information into L2 LSP allows routers from other areas to reach destinations within the area.

Let's check whether C1 is doing the right thing and inspect the contents of its level-1 and level-2 LSP databases:

R1 LSP as observed in the IS-IS level-1 database on C1 (running Arista cEOS)
{ .code-caption }
```
c1#show isis database level-1 r1.00-00 detail
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 1 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
    r1.00-00                     15  20334  1148    118 L1  0000.0000.0001.00-00  <>
      LSP received time: 2025-08-12 13:50:15
      Remaining lifetime received: 1199 s Modified to: 1200 s
      NLPID: 0xCC(IPv4)
      Hostname: r1
      Area addresses: 49.0100
      Interface address: 10.1.0.6
      Interface address: 10.1.0.2
      Interface address: 10.0.0.1
      IS Neighbor          : c2.00               Metric: 10
      IS Neighbor          : c1.00               Metric: 10
      Reachability         : 10.1.0.4/30 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.0/30 Metric: 10 Type: 1 Up
      Reachability         : 10.0.0.1/32 Metric: 10 Type: 1 Up
      Router Capabilities: Router Id: 10.0.0.1 Flags: []
        Area leader priority: 250 algorithm: 0

```

Level-2 LSP originated by C1 running Arista cEOS
{ .code-caption }
```
c1#show isis database level-2 c1.00-00 detail
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 2 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
    c1.00-00                     30  49359   687    169 L2  0000.0000.0002.00-00  <>
      LSP generation remaining wait time: 0 ms
      Time remaining until refresh: 387 s
      NLPID: 0xCC(IPv4)
      Hostname: c1
      Area addresses: 49.0100
      Interface address: 10.1.0.9
      Interface address: 10.1.0.13
      Interface address: 10.1.0.1
      Interface address: 10.0.0.2
      IS Neighbor          : c2.00               Metric: 10
      IS Neighbor          : x1.00               Metric: 10
      Reachability         : 10.1.0.16/30 Metric: 20 Type: 1 Up
      Reachability         : 10.0.0.3/32 Metric: 20 Type: 1 Up
      Reachability         : 10.0.0.1/32 Metric: 20 Type: 1 Up
      Reachability         : 10.1.0.4/30 Metric: 20 Type: 1 Up
      Reachability         : 10.1.0.8/30 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.12/30 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.0/30 Metric: 10 Type: 1 Up
      Reachability         : 10.0.0.2/32 Metric: 10 Type: 1 Up
      Router Capabilities: Router Id: 10.0.0.2 Flags: []
        Area leader priority: 250 algorithm: 0


```

As you can see, C1 inserted the information from R1 L1 LSP into its own L2 LSP. When that information is propagated across the level-2 backbone, other level-2 routers use it in their routing tables.

IS-IS routing table on X1 running FRRouting
{ .code-caption }
```
$ netlab connect x1 --show ip route isis
Connecting to container clab-multiarea-x1, executing vtysh -c "show ip route isis"
Codes: K - kernel route, C - connected, L - local, S - static,
       R - RIP, O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric, t - Table-Direct,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

IPv4 unicast VRF default:
I>* 10.0.0.1/32 [115/30] via 10.1.0.13, eth1, weight 1, 01:52:10
I>* 10.0.0.2/32 [115/20] via 10.1.0.13, eth1, weight 1, 04:46:37
I>* 10.0.0.3/32 [115/30] via 10.1.0.13, eth1, weight 1, 01:51:40
I>* 10.0.0.5/32 [115/40] via 10.1.0.13, eth1, weight 1, 01:51:41
I>* 10.1.0.0/30 [115/20] via 10.1.0.13, eth1, weight 1, 04:46:37
I>* 10.1.0.4/30 [115/30] via 10.1.0.13, eth1, weight 1, 01:52:10
I>* 10.1.0.8/30 [115/20] via 10.1.0.13, eth1, weight 1, 04:46:37
I   10.1.0.12/30 [115/20] via 10.1.0.13, eth1 inactive, weight 1, 04:46:37
I>* 10.1.0.16/30 [115/30] via 10.1.0.13, eth1, weight 1, 01:51:40
```

## Suboptimal Inter-Area Routing

Every time you have an L1 area with multiple gateways, you might get suboptimal routing toward some external destinations, as the level-1 routers always send their traffic toward the nearest level-2 router.

Let's trace the paths towards X1 and X2 from R1. This is what Arista EOS has to say[^ECMP]:

[^ECMP]: Even though ECMP is enabled on Arista cEOS, only the first ECMP entry is inserted into the underlying Linux routing table. All inter-area traffic is thus sent to the first default gateway (C1). Other implementations might spray the probe packets across all potential next hops, resulting in an even more interesting *traceroute* printout.

The **traceroute** command shows suboptimal routing from R1 toward X2
{ .code-caption }
```
r1#traceroute 10.0.0.4
traceroute to x1 (10.0.0.4), 30 hops max,* it signals to level-1 routers in the same area that it's attached through an L2 adjacency to another area and can be used as a gateway to the transit 60 byte packets
 1  c1 (10.1.0.1)  0.043 ms  0.008 ms  0.007 ms
 2  x1 (10.0.0.4)  1.113 ms  1.132 ms  1.396 ms
 
 
r1#traceroute 10.0.0.5
traceroute to x2 (10.0.0.5), 30 hops max, 60 byte packets
 1  c1 (10.1.0.1)  0.040 ms  0.009 ms  0.007 ms
 2  c2 (10.1.0.10)  0.635 ms  0.656 ms  0.863 ms
 3  x2 (10.0.0.5)  2.034 ms  2.077 ms  2.205 ms

```

Notice the suboptimal path R1 takes to reach X2. Although X2 is directly connected to C2, and C2 can be used as a default gateway, the outgoing traffic flows through C1.

Disabling ECMP [^ECAF] does not solve the problem. If you do that, R1 will generate just one default route from the LSP database and choose the LSP with the ATT flag set following these rules[^ECBC]:

* The closest (based on the metric) level-1-2 router with the ATT flag set
* When multiple equidistant level-1-2 routers exist, choose the one with the highest SystemID.

[^ECAF]: You can disable ECMP by setting **maximum-paths** to 1 in the IS-IS process. Some devices expect **maximum-paths** configured for a routing process, others expect it configured for individual address families.

[^ECBC]: When an IS-IS process uses N-way ECMP, it chooses the top N equidistant level-1-2 routers based on their SystemID.

**Takeaway:** Carefully consider using level-1 areas and accept that sub-optimal routing can occur. Consider the practical advice from [Configure IS-IS Routing for IPv4](../basic/1-simple-ipv4.md) before resorting to level-1 areas. In most cases, performance or scalability is no longer a good reason to deploy multi-level IS-IS networks.

## Partitioning the Transit Network

Finally, let's see what happens when the level-2 backbone breaks (the official term is *partitions*). Before starting, let's verify that we have connectivity from X1 to X2:

Check transit connectivity through the IS-IS area 49.0100
{ .code-caption }
```
$ netlab connect -q x1 ping 10.0.0.5
PING x2 (10.0.0.5): 56 data bytes
64 bytes from 10.0.0.5: seq=0 ttl=62 time=1.427 ms
64 bytes from 10.0.0.5: seq=1 ttl=62 time=1.377 ms
....
```

Next, shut down the link between C1 and C2 (shutting down the Ethernet2 interface on C2 will do the trick). Although there's the physical path between X1 and X2 (X1→C1→R1→C2→X2), X1 cannot reach X2:

X1 cannot reach X2 once the C1-C2 link is shut down
{ .code-caption }
```
$ netlab connect -q x1 ping 10.0.0.5
PING x2 (10.0.0.5): 56 data bytes
ping: sendto: Network unreachable
```

**Takeaway:** The level-2 backbone MUST NOT become partitioned. IS-IS has no mechanism like OSPF virtual links that could stitch together a partitioned level-2 backbone.

## Before Moving On

Congratulations. You have completed the first step of the multi-level IS-IS journey.

There is no specific validation test included with the lab. However, at the end of the exercise (and once you restored the C1-C2 link), you should have:

* R1 working as level-1 router
* C1 and C2 working as level-1-2 routers
* R1 being able to ping X1 and X2
* X1 being able to ping X2

**Next**: [Build an SR-MPLS Network with IS-IS](10-sr.md)

## Reference Information

### Lab Wiring

| Origin Device | Origin Port | Destination Device | Destination Port |
|---------------|-------------|--------------------|------------------|
| r1 | Ethernet1 | c1 | Ethernet1 |
| r1 | Ethernet2 | c2 | Ethernet1 |
| c1 | Ethernet2 | c2 | Ethernet2 |
| c1 | Ethernet3 | x1 | eth1 |
| c2 | Ethernet3 | x2 | eth1 |

!!! Note
    The interface names depend on the lab devices you use. The printout was generated with user routers running Arista EOS and X1/X2 running FRRouting.

### Lab Addressing

| Node/Interface | IPv4 Address | IPv6 Address | Description |
|----------------|-------------:|-------------:|-------------|
| **r1** |  10.0.0.1/32 |  | Loopback |
| Ethernet1 | 10.1.0.2/30 |  | r1 -> c1 |
| Ethernet2 | 10.1.0.6/30 |  | r1 -> c2 |
| **c1** |  10.0.0.2/32 |  | Loopback |
| Ethernet1 | 10.1.0.1/30 |  | c1 -> r1 |
| Ethernet2 | 10.1.0.9/30 |  | c1 -> c2 |
| Ethernet3 | 10.1.0.13/30 |  | c1 -> x1 |
| **c2** |  10.0.0.3/32 |  | Loopback |
| Ethernet1 | 10.1.0.5/30 |  | c2 -> r1 |
| Ethernet2 | 10.1.0.10/30 |  | c2 -> c1 |
| Ethernet3 | 10.1.0.17/30 |  | c2 -> x2 |
| **x1** |  10.0.0.4/32 |  | Loopback |
| eth1 | 10.1.0.14/30 |  | x1 -> c1 |
| **x2** |  10.0.0.5/32 |  | Loopback |
| eth1 | 10.1.0.18/30 |  | x2 -> c2 |
