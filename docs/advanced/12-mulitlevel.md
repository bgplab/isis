# Multilevel IS-IS Deployments

In this exercise, I will explore multi-level IS-IS networks using a 5-router topology.

![Lab topology](topology-multiarea.png)

## Device Requirements

Use any device [supported by the _netlab_ IS-IS configuration module](https://netlab.tools/platforms/#platform-routing-support) except FRRouting, or any other device that uses FRRouting in its control plane. As of August 2025, IS-IS implementation in FRR is still incomplete. 

## Starting the Lab

You can start the lab [on your own lab infrastructure](../1-setup.md) or in [GitHub Codespaces](https://github.com/codespaces/new/bgplab/isis) ([more details](https://bgplabs.net/4-codespaces/)):

* Change directory to `advanced/13-multiarea`
* Execute **netlab up**
* Log into lab devices with **netlab connect**

## Existing Routing Protocol Configuration

When starting the lab, _netlab_ configures IPv4 addresses and IS-IS protocol on the lab routers.

All 5 routers are configured as L1L2 IS-IS routers. The result is a flat Level 2 IS-IS topology connecting all the areas. Routers use the following areas:

| Node | Router ID | IS-IS Area |
|----------|----------:|--------------------:|
| r1 | 10.0.0.1 | 49.0100 |
| c1 | 10.0.0.2 | 49.0100 |
| c2 | 10.0.0.3 | 49.0100 |
| x1 | 10.0.0.4 | 49.0001 |
| x2 | 10.0.0.5 | 49.0002 |



## Level-1 and Level-2 Adjacency Rules in IS-IS

As already mentioned, IS-IS uses areas (level-1 routing) connected via an overlay inter-area routing topology (level-2 routing).  

OSPF utilizes a hierarchical backbone with a special designation, "Area 0". There is no such enforcement in IS-IS. Transit routers are not required to be part of any area with a special designation. The only requirement is that there is end-to-end level-2 connectivity across all transit routers. 

* Level-1 (intra-area) routers) only form adjacencies in the same area. They form L1 adjacencies with other level-1 routers, or with level-1-2 routers.
* Level-2 routers form level 2 adjacencies with other level-2 routers, or with level-1-2 routers. They can form adjacencies with routers in other areas. This is important; the only way to connect two areas in IS-IS is through an L2 adjacency.
* Level-1-2 routers can form both L1 and L2 adjacencies. They maintain a separate topological database for each of those levels. They act as border routers and manifest many similarities with OSPF Area Border Routers. 


## L1L2 routers and Attached bit 

After starting the lab, let's examine the level-1 LSP database on router c1. This is what an Arista has to say about it:
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

Notice that the LSPs have the ATT flag set. The full name of this flag is "Attached". A level-1-2 router that is connected through an L2 adjacency to another area and received routing information from that area will originate LSPs with the ATT flag set. It is used as follows:

* It signals to level-1 routers in the same area that it's attached through an l2 adjacency to another area and can be used as a gateway to the transit
* it enables default routing in the area
* level-1 routers receiving an LSP with ATT bit set will originate a default route pointing to the router that sent the LSP.




## Configure an IS-IS router as a level-1 router.

Log in to r1. It's a level-1-2 router, so it will maintain LSP databases for both levels and knows the full topology of the network. Check its routing table:

{ .code-caption }

```
r1#show ip route isis


 I L1     10.0.0.2/32 [115/20]
           via 10.1.0.1, Ethernet1
 I L1     10.0.0.3/32 [115/20]
           via 10.1.0.5, Ethernet2
 I L2     10.0.0.4/32 [115/30]
           via 10.1.0.1, Ethernet1
 I L2     10.0.0.5/32 [115/30]
           via 10.1.0.5, Ethernet2
 I L1     10.1.0.8/30 [115/20]
           via 10.1.0.1, Ethernet1
           via 10.1.0.5, Ethernet2
 I L1     10.1.0.12/30 [115/20]
           via 10.1.0.1, Ethernet1
 I L1     10.1.0.16/30 [115/20]
           via 10.1.0.5, Ethernet2
```

Next, change the is-type of the is-is routing process to  level-1. Check the LSP database:

{ .code-caption }
```
r1#show isis database
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 1 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
    r1.00-00                      8  50941  1151    154 L1  0000.0000.0001.00-00  <>
    c1.00-00                      8  16412  1150    131 L2  0000.0000.0002.00-00  <DefaultAtt>
    c2.00-00                      7  37557  1151    131 L2  0000.0000.0003.00-00  <DefaultAtt>
```

Notice that the level-2 database is gone. The router no longer knows the topology of the whole network, but just that of its area.

Check the routing table again:

{ .code-caption }
```
r1#show ip route isis

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

There are interesting changes. First, the router no longer has routes to x1 and x2. It lost all IS-IS L2 routes. Second, notice that the router originated two default routes, pointing towards c1 and c2. 

Where do they come from? Recall that both c1 and c2 send L1 LSPs with the ATT bit set, and this bit signals level-1 routers to originate default routes pointing to the border router sending them. In our topology, both c1 and c2 act as border routers, so they both advertise the ATT bit in their LSPs. 

Router r1 has ECMP enabled by default, so it decides to use both of the ABRs and originates default routes for both of them.

Also, despite x1 and x2 not being in the routing table, they are still reachable, thanks to the default routing:

{ .code-caption }
```
r1#ping x1
PING x1 (10.1.0.14) 72(100) bytes of data.
80 bytes from x1 (10.1.0.14): icmp_seq=1 ttl=63 time=0.512 ms
80 bytes from x1 (10.1.0.14): icmp_seq=2 ttl=63 time=0.163 ms
....

```

## External Reachability 

You may wonder, how can routers in area 49.0001 or 49.0002 learn about specific routes inside area 49.0100? 

On L1L2 routers, IS-IS automatically distributes intra-area information it receives through L1 LSPs into its L2 LSP database, as required by the IS-IS standard. Let's confirm this.

On c1, lets examine both it's L1 database and L2 database:

{ .code-caption }
```
show isis database level-1 r1.00-00 detail
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 1 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
    r1.00-00                      6  51963  1026    154 L1  0000.0000.0001.00-00  <>
      LSP received time: 2025-08-04 07:03:50
      Remaining lifetime received: 1199 s Modified to: 1200 s
      NLPID: 0xCC(IPv4)
      Hostname: r1
      Area addresses: 49.0100
      Interface address: 172.16.2.1
      Interface address: 172.16.1.1
      Interface address: 172.16.0.1
      Interface address: 10.1.0.6
      Interface address: 10.1.0.2
      Interface address: 10.0.0.1
      IS Neighbor          : c2.00               Metric: 10
      IS Neighbor          : c1.00               Metric: 10
      Reachability         : 172.16.2.0/24 Metric: 10 Type: 1 Up
      Reachability         : 172.16.1.0/24 Metric: 10 Type: 1 Up
      Reachability         : 172.16.0.0/24 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.4/30 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.0/30 Metric: 10 Type: 1 Up
      Reachability         : 10.0.0.1/32 Metric: 10 Type: 1 Up
      Router Capabilities: Router Id: 10.0.0.1 Flags: []
        Area leader priority: 250 algorithm: 0


```

{ .code-caption }
```
show isis database level-2 r1.00-00 detail
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
  IS-IS Level 2 Link State Database
    LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
 U  r1.00-00                      5  17009   204    201 L2  0000.0000.0001.00-00  <>
      LSP received time: 2025-08-04 06:52:21
      Remaining lifetime received: 1199 s Modified to: 1200 s
      NLPID: 0xCC(IPv4)
      Hostname: r1
      Area addresses: 49.0100
      Interface address: 172.16.2.1
      Interface address: 172.16.1.1
      Interface address: 172.16.0.1
      Interface address: 10.1.0.6
      Interface address: 10.1.0.2
      Interface address: 10.0.0.1
      IS Neighbor          : c2.00               Metric: 10
      IS Neighbor          : c1.00               Metric: 10
      Reachability         : 10.1.0.8/30 Metric: 20 Type: 1 Up
      Reachability         : 10.1.0.16/30 Metric: 20 Type: 1 Up
      Reachability         : 10.1.0.12/30 Metric: 20 Type: 1 Up
      Reachability         : 10.0.0.2/32 Metric: 20 Type: 1 Up
      Reachability         : 10.0.0.3/32 Metric: 20 Type: 1 Up
      Reachability         : 172.16.2.0/24 Metric: 10 Type: 1 Up
      Reachability         : 172.16.1.0/24 Metric: 10 Type: 1 Up
      Reachability         : 172.16.0.0/24 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.4/30 Metric: 10 Type: 1 Up
      Reachability         : 10.1.0.0/30 Metric: 10 Type: 1 Up
      Reachability         : 10.0.0.1/32 Metric: 10 Type: 1 Up
      Router Capabilities: Router Id: 10.0.0.1 Flags: []
        Area leader priority: 250 algorithm: 0


```


Notice the duplication of information in the two databases.


## Inter-area suboptimal routing

Every time you have an L1 area with multiple gateways, you open up the potential for sub-optimal routing. One important take away of this exercise is 
that you should carefully consider the use of level-1 areas and accept that suboptimal routing can take place (there are solutions that alleviate the problem, but we will leave them for another exercise ). In most modern network designs, level-1 areas are not a necessity. They were initially developed and included in standard to limit flooding domains of the routers, but today's silicon is so fast that hundreds level-2 routers can exist in a single area with no ill consequences. 


On r1, let's trace paths towards x1 and x2. With ECMP enabled, this is what Arista has to say:

{ .code-caption }
```
r1#traceroute x1
traceroute to x1 (10.0.0.4), 30 hops max,* it signals to level-1 routers in the same area that it's attached through a l2 adjacency to another area and can be used as a gateway to the transit 60 byte packets
 1  c1 (10.1.0.1)  0.043 ms  0.008 ms  0.007 ms
 2  x1 (10.0.0.4)  1.113 ms  1.132 ms  1.396 ms
 
 
r1#traceroute x2
traceroute to x2 (10.0.0.5), 30 hops max, 60 byte packets
 1  c1 (10.1.0.1)  0.040 ms  0.009 ms  0.007 ms
 2  c2 (10.1.0.10)  0.635 ms  0.656 ms  0.863 ms
 3  x2 (10.0.0.5)  2.034 ms  2.077 ms  2.205 ms

```

Notice the suboptimal path taken by a packet towards x2. Although x2 is directly connected to c2, and c2 can be used as a gateway, the path chosen for this flow goes through c1.

Disabling ECMP does not solve the problem. You can disable ECMP by setting maximum-paths to 1 for the IS-IS process. For some routers, the setting will be under address-family.

If you do that, you will also notice that one of the default gateways r1 originated is gone. r1 router will choose just one from the multiple routers advertising LSPs with ATT flag set into this L1 area as a gateway:

* The closest level-1-2 router based on metric wins
* SystemID is used as a tie-breaking. Highest SystemID wins.


## The perils of partitioning the transit network

Verify connectivity through the transit network:

{ .code-caption }
```
netlab exec x1 ping x2
Connecting to clab-multiarea-x1 using SSH port 22, executing ping x2
PING x2 (10.0.0.5) 72(100) bytes of data.
80 bytes from x2 (10.0.0.5): icmp_seq=1 ttl=62 time=0.889 ms
80 bytes from x2 (10.0.0.5): icmp_seq=2 ttl=62 time=0.410 ms
....

```

Partition the transit network by disabling the link between  c1 and c2. Shutting down the Ethernet2 interface on c1 router will do it (depending on the device used, names of interfaces can be different). 

On x1, ping 10.0.0.5

{ .code-caption }
```
x1#ping 10.0.0.5
ping: connect: Network is unreachable


```

The loopback of x1 is no longer reachable. The take-home message here is:

* Design your transit network with plenty of redundancy, such that it never becomes partitioned.


## Validation

TODO


**Next**: [Running IS-IS Over Unnumbered Interfaces](7-unnumbered.md)

## Reference Information

### Lab Wiring

|---------------|-------------|--------------------|------------------|
| Origin Device | Origin Port | Destination Device | Destination Port |
|---------------|-------------|--------------------|------------------|
| r1            | Ethernet1   | c1                 | Ethernet1        |
| r1            | Ethernet2   | c2                 | Ethernet1        |
| c1            | Ethernet2   | c2                 | Ethernet2        |
| c1            | Ethernet3   | x1                 | Ethernet1        |
| c2            | Ethernet3   | x2                 | Ethernet1        |


