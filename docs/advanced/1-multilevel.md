# Multilevel IS-IS Deployments

In the past, multi-level IS-IS networks were used to improve the scalability of IS-IS networks. Since level-1 routers only know the topology of their zone, a multilevel IS-IS deployment presented two major scalability benefits.

Firstly, multilevel deployments resulted in a reduced routing table size in level-1 routers, thereby saving RAM.

Second, multi-level deployments limit the flooding domain for link-state PDUs to their area, saving control-plane CPU time for both LSP processing and SPF calculations. This naturally enabled faster convergence times after a change. 

In this exercise, I will explore multi-level IS-IS networks using a 5-router topology.

![Lab topology](topology-multiarea.png)

## Device Requirements

Use any device [supported by the _netlab_ IS-IS configuration module](https://netlab.tools/platforms/#platform-routing-support) that properly implements advertising intra-area routes into inter-area (level-2) backbone. Unfortunately, this leaves FRRouting devices off the table. As of August 2025, FRRouting's IS-IS implementation is incomplete and does not satisfy this requirement. Nevertheless, the implemented parts are solid, and FRR can be used without any problems for large level-2 IS-IS deployments. 

## Starting the Lab

You can start the lab [on your own lab infrastructure](../1-setup.md) or in [GitHub Codespaces](https://github.com/codespaces/new/bgplab/isis) ([more details](https://bgplabs.net/4-codespaces/)):

* Change directory to `advanced/1-multiarea`
* Execute **netlab up**
* Log into lab devices with **netlab connect**

## Existing Routing Protocol Configuration

When starting the lab, _netlab_ configures IPv4 addresses and IS-IS protocol on the lab routers.

All 5 routers are configured as L2 IS-IS routers, as recommended in [Configure IS-IS Routing for IPv4](../basic/1-simple-ipv4.md). This results in a flat level-2 multi-area topology. Routers use the following areas:

| Node | Router ID | IS-IS Area |
|----------|----------:|--------------------:|
| r1 | 10.0.0.1 | 49.0100 |
| c1 | 10.0.0.2 | 49.0100 |
| c2 | 10.0.0.3 | 49.0100 |
| x1 | 10.0.0.4 | 49.0001 |
| x2 | 10.0.0.5 | 49.0002 |


## Examination of initial state

First, with the lab in a pristine state, you should have full reachability between all routers' loopback interfaces. Convince yourself that in past times, people were rightfully concerned about the size of the routing table in a level-2-only network. 

Router R1 has a full topological view of the network. Its routing table is also fairly large, even for our small network of 5 routers.   Imagine a network with hundreds of routers, each advertising tens of networks, and you can quickly see that it can get out of hand fast.

Connect to r1:
{ .code-caption }
```
netlab connect r1
```

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

## Configuration task 1: Make r1 a level-1 router

Let's see if you can minimize the size of the routing table. Make router R1 a level-1 IS-IS router. The command you need for this should be pretty familiar to you. After all, you made it so far, through all those wonderful IS-IS labs.

Once the router is configured as a level-1 router, examine the routing table.  

IS-IS routes on R1 running Arista cEOS
{ .code-caption }
```
r1#show ip route isis

VRF: default
Source Codes:
       I L1 - IS-IS level 1,
       I L2 - IS-IS level 2,
....

```
We lost all IS-IS routes. 
Some troubleshooting is in order. On r1, check IS-IS adjacencies. All r1's neighbors are gone.  Your next task will be to restore the lost adjacencies. But before that, a short detour through the IS-IS adjacency rules is in order. It will explain why R1 lost all its neighbours. 


## Level-1 and Level-2 Adjacency Rules in IS-IS

As already mentioned, IS-IS uses areas (level-1 routing) connected via an overlay inter-area routing topology (level-2 routing). In many ways, the inter-area overlay is similar to an OSPF backbone, but with many important differences.

In OSPF, all inter-area traffic (backbone) must transit a specially designated area, the so-called "Area 0". Any other area must connect to Area 0 for transit, resulting in a strict hierarchical network, with the consequence that border routers must have at least an interface in Area 0. 

Compared to OSPF, IS-IS has more flexible requirements. Backbone routers, often referred to as "transit routers" in IS-IS parlance, are not required to be part of any area with a special designation. They are also not required to be part of the same area.  The same applies to  L1/L2 routers.

The only requirement imposed on an IS-IS transit network is that there is end-to-end level-2 continuity through L2 adjacencies across all transit routers. Both L2 and L1/L2 routers can ensure the required level-2 continuity. 

The rules governing adjacency formation in IS-IS are simple:

* Level-1 (intra-area) routers) only form adjacencies in the same area. They form L1 adjacencies with other level-1 routers, or with level-1-2 routers. A direct consequence of this is that they cannot be border routers. 
* Level-2 routers form L2 adjacencies with other level-2 routers, or with level-1-2 routers. They can form adjacencies with routers in other areas. This is important; the only way to connect two different areas in IS-IS is through an L2 adjacency.
* Level-1-2 routers can form both L1 and L2 adjacencies. They maintain a separate topological database for each of those levels. They act as border routers and manifest many similarities with OSPF Area Border Routers. 


## Configuration task 2: Make c1 and c2 level-1-2 routers

Now that you know the rules, it's easy to see why R1 lost its neighbor relation with both c1 and c2. A level-1 router cannot form a neighbor relation with a level-2 router. 

To fix the problem, change the type of c1 and c2 to level-1-2 IS-IS routers. Again, the command to do that should be familiar by now. When you are done, check if the solution solves the adjacency problem we had at the end of the previous configuration task. On r1:

IS-IS neighbours on R1
{ .code-caption }
```
r1#show isis neighbors
 
Instance  VRF      System Id        Type Interface          SNPA              State Hold time   Circuit Id          
Gandalf   default  c1               L1   Ethernet1          P2P               UP    24          24                  
Gandalf   default  c2               L1   Ethernet2          P2P               UP    21          26            

```


As expected, the adjacency problem is solved. Next, check if the goals of reducing the routing table size and flooding domain size have been reached. Again, on r1:

IS-IS database on R1
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

You will immediately notice that r1 lost full topological view of the network. The Is-Is database only contains LSPs originated by c1,c2, and r1.

Examine r1's routing table. Here is a cEOS Arista router responding:

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

Observe that the type of IS-IS routes changed from L2 to L1, and loopbacks for x1 and x2 are no longer in the routing table. It accurately reflects the fact that R1 lost view of the level-2 network topology. The actual changes in the routing table are small at the scale of a 5-router lab, but as you can easily imagine, they can be significant at scale.

Since the goal of all those changes was to showcase potential optimizations with multi-level IS-IS networks, and not fragmenting the network, let's confirm that we still have reach-ability to routers in other areas, such as  x1 and x2:

Inter-area connectivity
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
 

Despite no longer having an L2 route to x1 and x2's loopbacks, connectivity is still present. 

Astute people working in the lab might have already remarked something interesting in r1's routing table: the presence of an ECMP default route pointing towards c1 and c2. It's used for L2 default routing, and it's the key to reaching the level-2 backbone and, implicitly, other IS-IS areas.

Next, we will examine how this default route is originated:


## L2 Default routing mechanics, L1/L2 routers and Attached bit 

Examine the level-1 LSP database on router C1. 

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
    r1.00-00                      4  55525  1167    154 L2  0000.0000.0001.00-00  <DefaultAtt>
    c1.00-00                      4  18456  1167    131 L2  0000.0000.0002.00-00  <DefaultAtt>
    c2.00-00                      3  39601  1167    131 L2  0000.0000.0003.00-00  <DefaultAtt>

```

Notice that the LSPs have the ATT flag set. The full name of this flag is "Attached". In the words of ISO_IEC_10589_2002, a level-1-2 router considers itself attached when

*it can reach at least one other area using the corresponding routeing metric, or
*It has at least one enabled reachable address prefix with the corresponding metric defined.

If a router considers itself attached, it will originate L1 LSPs with the ATT flag set. This has the following effects:

* It signals  level-1 routers in the same area that it may carry traffic to the backbone and into other areas. Practically, it advertises itself as an exit point from a level-1 area. 
* It enables default routing in the area
* Level-1 routers receiving an LSP with the ATT bit set will originate a default route pointing to the router that sent the LSP.

Back to the default routes we saw earlier in R1's routing table. In our topology, both c1 and c2 consider themselves attached, and they both originate L1 LSPs with the ATT bit set. 

Router R1 has ECMP enabled by default, so it decides to use both c1 and c2 as  ABR routers and originates default routes for each one of them.

## L1 Route leaking

We already convinced ourselves that R1 can reach routers in other areas, in our case, routers x1 and x2, and we have full data-plane connectivity. There is another part of the puzzle that needs to be explored, namely, the specifics of how routers in area 49.0001 or 49.0002 learn about specific routes inside area 49.0100 in which R1 resides. 

On L1L2 routers, IS-IS automatically distributes intra-area information it receives through L1 LSPs into its L2 LSP database, as required by the IS-IS standard. This allows reachability inside the level 1 area. Let's confirm this.

On c1, lets examine both it's L1 database and L2 database:

IS-IS level-1 database on C1, r1.00-00 LSP detail, running Arista cEOS
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


IS-IS level-2 database on C1, c1.00-00 LSP detail, running Arista cEOS
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

Notice that the information in r1's L1 LSPs is duplicated in router's c1 L2 LSP database, and propagated into the backbone. We can see this by examining the routing table on x1 or x2. On x1:

IS-IS routing table on X1, running FRRrouting
{ .code-caption }
```
netlab connect x1 --show ip route isis


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


## Inter-area suboptimal routing

Every time you have an L1 area with multiple gateways, you open up the potential for sub-optimal routing. 


On r1, let's trace paths towards x1 and x2. With ECMP enabled, this is what Arista has to say:

Route tracing showcasing sub-optimal routing
{ .code-caption }
```
r1#traceroute x1
traceroute to x1 (10.0.0.4), 30 hops max,* it signals to level-1 routers in the same area that it's attached through an L2 adjacency to another area and can be used as a gateway to the transit 60 byte packets
 1  c1 (10.1.0.1)  0.043 ms  0.008 ms  0.007 ms
 2  x1 (10.0.0.4)  1.113 ms  1.132 ms  1.396 ms
 
 
r1#traceroute x2
traceroute to x2 (10.0.0.5), 30 hops max, 60 byte packets
 1  c1 (10.1.0.1)  0.040 ms  0.009 ms  0.007 ms
 2  c2 (10.1.0.10)  0.635 ms  0.656 ms  0.863 ms
 3  x2 (10.0.0.5)  2.034 ms  2.077 ms  2.205 ms

```

Notice the sub-optimal path taken by a packet towards x2. Although x2 is directly connected to c2, and c2 can be used as a gateway, the transit chosen for this flow goes through c1.

Disabling ECMP does not solve the problem. You can disable ECMP by setting maximum-paths to 1 for the IS-IS process. For some devices, this setting is under the address-family configuration hierarchy.

If you do that, you will also notice that one of the default gateways that R1 originated is gone. R1 router will choose just one from the multiple routers advertising LSPs with the ATT flag set in this L1 area as a gateway.

In both situations, the gateway is chosen by the algorithm below. When ECMP is active, a list of the best candidates is built, and then N candidates (corresponding to the maximum ECMP paths in use) are selected to be used as gateways. With ECMP disabled, only the top candidate is selected. 

* The closest level-1-2 router based on metric wins
* SystemID is used as a tie-breaking. Highest SystemID wins.

One important takeaway of this exercise is that you should carefully consider the use of level-1 areas and accept that sub-optimal routing can occur. (Some solutions alleviate the problem, but we will leave them for another exercise.) Consider the practical advice from [Configure IS-IS Routing for IPv4](../basic/1-simple-ipv4.md) before resorting to level-1 areas. Performance is no longer a good reason to deploy multi-level IS-IS networks. 


## Partitioning the transit network


Verify connectivity through the transit network:

Check reach-ability though transit
{ .code-caption }
```
netlab exec x1 ping 10.0.0.5

Connecting to clab-multiarea-x1 using SSH port 22, executing ping x2
PING x2 (10.0.0.5) 72(100) bytes of data.
80 bytes from x2 (10.0.0.5): icmp_seq=1 ttl=62 time=0.889 ms
80 bytes from x2 (10.0.0.5): icmp_seq=2 ttl=62 time=0.410 ms
....

```

Partition the transit network by disabling the link between  c1 and c2. Shutting down the Ethernet2 interface on the c1 router will do it. 

On x1, ping 10.0.0.5

Check reach-ability though transit, after partitioning
{ .code-caption }
```
netlab exec x1 ping 10.0.0.5

ping: connect: Network is unreachable


```

The loopback of x2 is no longer reachable. The take-home message here is:

* Design your transit network with plenty of redundancy, such that it never becomes partitioned.

Enable the Ethernet2 interface on c1.


## Validation

Congratulations. You have reached the end of this leg of the journey. 

There is no specific validation test included with the lab. However, at the end of the exercise, you should have:

* is-type should be level-1 on r1
* is-type should be level-1-2 on both c1 and c2
* r1 should be able to ping both x1 and x2
* x1 should be able to ping x2 (if did the very last bit of configuration)


**Next**: [Build an SR-MPLS Network with IS-IS](10-sr.md)

## Reference Information

### Lab Wiring

| Origin Device | Origin Port | Destination Device | Destination Port |
|---------------|-------------|--------------------|------------------|
| r1            | Ethernet1   | c1                 | Ethernet1        |
| r1            | Ethernet2   | c2                 | Ethernet1        |
| c1            | Ethernet2   | c2                 | Ethernet2        |
| c1            | Ethernet3   | x1                 | Ethernet1        |
| c2            | Ethernet3   | x2                 | Ethernet1        |


!!! Note
    The interface names depend on the lab devices you use. The printout was generated with lab devices running Arisa cEOS.


### Lab Addressing

| Node (Loopback) | Interface | IPv4 Address | IPv6 Address | Description |
|-----------------|-----------|--------------|--------------|-------------|
| r1 (10.0.0.1/32) | Ethernet1 | 10.1.0.2/30 | | r1 -> c1 |
| | Ethernet2 | 10.1.0.6/30 | | r1 -> c2 |
| c1 (10.0.0.2/32) | Ethernet1 | 10.1.0.1/30 | | c1 -> r1 |
| | Ethernet2 | 10.1.0.9/30 | | c1 -> c2 |
| | Ethernet3 | 10.1.0.13/30 | | c1 -> x1 |
| c2 (10.0.0.3/32) | Ethernet1 | 10.1.0.5/30 | | c2 -> r1 |
| | Ethernet2 | 10.1.0.10/30 | | c2 -> c1 |
| | Ethernet3 | 10.1.0.17/30 | | c2 -> x2 |
| x1 (10.0.0.4/32) | eth1 | 10.1.0.14/30 | | x1 -> c1 |
| x2 (10.0.0.5/32) | eth1 | 10.1.0.18/30 | | x2 -> c2 |