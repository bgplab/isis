# Manual Configuration of Summary Addresses

By [Dan Partelly](https://github.com/DanPartelly)
{.author-byline }


A foreshadowing of the problems we will solve today can be found in the first footnote of the [Multilevel IS-IS Deployments](../advanced/1-multilevel.md) exercise. Without summarization, changes in an L1 area will be propagated into L2 areas(backbone).

In this exercise, we will continue the trend of simplifying the routing tables and minimizing the shared state between level-1 and level-2 IS-IS hierarchies. [^NE]

You'll use manual configuration of summary addresses on the level-1 - level-2 boundary, a mechanism described in [RFC 1195](https://datatracker.ietf.org/doc/html/rfc1195), on a three-router topology.

![Lab topology](topology-summarization.png)

[^NE]: Network engineers with a background in programming will quickly realize that, besides performance implications, minimizing information in routing tables, and implicitly, the shared state between level-1 and level-2 IS-IS hierarchy is a good tool to control complexity.

## Device Requirements

Use any device [supported by the _netlab_ IS-IS configuration module](https://netlab.tools/platforms/#platform-routing-support) that correctly implements the propagation of level-1 IP prefixes into the level-2 LSP database as required by RFC 1195.

Unfortunately, this leaves FRRouting off the table. As of August 2025, FRRouting's IS-IS implementation cannot distribute prefixes between level-1 areas and level-2 backbone.

## Starting the Lab

You can start the lab [on your own lab infrastructure](../1-setup.md) or in [GitHub Codespaces](https://github.com/codespaces/new/bgplab/isis) ([more details](https://bgplabs.net/4-codespaces/)):

* Change directory to `advanced/3-summarization`
* Execute **netlab up**
* Log into lab devices with **netlab connect**

## Existing Device Configuration

When starting the lab, _netlab_ configures IPv4 addresses and IS-IS protocol on the lab routers, resulting in a small multi-area, multi-level topology.

Three stub networks are present on router R1, in the level-1 area.

IS-IS parameters of individual lab devices are summarized in the following table:

| Node | IS-IS Area | System ID | IS type |
|------|-----------:|----------:|---------|
| x1 | 49.0001 | 0000.0000.0003 | level-2 |
| r1 | 49.0100 | 0000.0000.0001 | level-1 |
| c1 | 49.0100 | 0000.0000.0002 | level-1-2 |



## The Problem

Let's illustrate how changes in the topology of a level-1 area can spill into the backbone. Start with an examination of the routing table on X1:

X1 routing table. Notice the presence of our stub networks (as viewed on FRR)
{ .code-caption }
```
$ netlab connect x1 -s ip route
Connecting to container clab-summarization-x1, executing vtysh -c "show ip route"
.....

IPv4 unicast VRF default:
I>* 10.0.0.1/32 [115/30] via 10.1.0.5, eth1, weight 1, 00:00:16
I>* 10.0.0.2/32 [115/20] via 10.1.0.5, eth1, weight 1, 00:00:17
L * 10.0.0.3/32 is directly connected, lo, weight 1, 00:00:35
C>* 10.0.0.3/32 is directly connected, lo, weight 1, 00:00:35
I>* 10.1.0.0/30 [115/20] via 10.1.0.5, eth1, weight 1, 00:00:17
I   10.1.0.4/30 [115/20] via 10.1.0.5, eth1 inactive, weight 1, 00:00:17
C>* 10.1.0.4/30 is directly connected, eth1, weight 1, 00:00:35
L>* 10.1.0.6/32 is directly connected, eth1, weight 1, 00:00:35
I>* 172.16.0.0/24 [115/30] via 10.1.0.5, eth1, weight 1, 00:00:16
I>* 172.16.1.0/24 [115/30] via 10.1.0.5, eth1, weight 1, 00:00:16
I>* 172.16.2.0/24 [115/30] via 10.1.0.5, eth1, weight 1, 00:00:16
```


This should not be surprising. We already know that L1/L2 routers perform automatic distribution of L1 Routes into L2 areas.

C1's level-2 LSP as viewed on X1. Notice extended reachability to our stub networks. { .code-caption }
```
x1# show isis database detail c1.00-00
Area Gandalf:
IS-IS Level-2 link-state database:
LSP ID                  PduLen  SeqNumber   Chksum  Holdtime  ATT/P/OL
c1.00-00                  142   0x00000007  0xd869     874    0/0/0
Protocols Supported: IPv4
Area Address: 49.0100
Hostname: c1
Router Capability: 10.0.0.2 , D:0, S:0
Extended Reachability: 0000.0000.0003.00 (Metric: 10)
IPv4 Interface Address: 10.1.0.5
IPv4 Interface Address: 10.1.0.1
IPv4 Interface Address: 10.0.0.2
Extended IP Reachability: 172.16.0.0/24 (Metric: 20)
Extended IP Reachability: 10.0.0.1/32 (Metric: 20)
Extended IP Reachability: 172.16.1.0/24 (Metric: 20)
Extended IP Reachability: 172.16.2.0/24 (Metric: 20)
Extended IP Reachability: 10.1.0.4/30 (Metric: 10)
Extended IP Reachability: 10.1.0.0/30 (Metric: 10)
Extended IP Reachability: 10.0.0.2/32 (Metric: 10)

```

Now let's look at what happens when a topology change occurs in the level-1 area.

Start by tracing in real-time the execution of the SPF algorithm in IS-IS, on X1.
Connect to X1 and ensure that your SSH session monitors the terminal.

Enable debugging of isis SPF events.[^SN] On FRR, the command is:

```
x1# debug isis spf-events
```

This will give you a trace of all executions of the SPF algorithm by the IS-IS process, and the execution reason.

Connect to R1 in a separate session. Shutdown one of the stub network interfaces. We are gonna shutdown R1's Ethernet2 here:

Almost instantly, on X1, you get a trace of SPF execution:

SPF execution trace on X1 as viewed on FRR)
{ .code-caption }
```
[DEBG] isisd: [SFWMK-K9QH2] ISIS-SPF (Gandalf) L2 SPF schedule called, lastrun 298 sec ago Caller: lsp_update isisd/isis_lsp.c:551
[DEBG] isisd: [KD9RA-6JFGA] ISIS-SPF (Gandalf) L2 SPF scheduled 0 sec from now
[DEBG] isisd: [N48RF-Z09QJ] ISIS-SPF (Gandalf) L2 SPF needed, periodic SPF
```

The SPF algorithm was executed in response to an LSP update. We now know the potential culprit. Look again at C1s  LSP:

C1's LSP on X1. Notice the propagation of reachability information from L1 (missing 172.16.0.0/24)
{ .code-caption }
```
x1# show isis database detail c1.00-00
Area Gandalf:
IS-IS Level-2 link-state database:
LSP ID                  PduLen  SeqNumber   Chksum  Holdtime  ATT/P/OL
c1.00-00                  134   0x00000008  0x6bc6    1195    0/0/0
Protocols Supported: IPv4
Area Address: 49.0100
Hostname: c1
Router Capability: 10.0.0.2 , D:0, S:0
Extended Reachability: 0000.0000.0003.00 (Metric: 10)
IPv4 Interface Address: 10.1.0.5
IPv4 Interface Address: 10.1.0.1
IPv4 Interface Address: 10.0.0.2
Extended IP Reachability: 10.0.0.1/32 (Metric: 20)
Extended IP Reachability: 172.16.1.0/24 (Metric: 20)
Extended IP Reachability: 172.16.2.0/24 (Metric: 20)
Extended IP Reachability: 10.1.0.4/30 (Metric: 10)
Extended IP Reachability: 10.1.0.0/30 (Metric: 10)
Extended IP Reachability: 10.0.0.2/32 (Metric: 10)
```

On interface shutdown, R1 sends an updated level-1 LSP to C1. C1 - a level-1-2 router -  receives the LSP, updates the level-1, and copies the relevant changes into the level-2 database. Then, a level-2 LSP is sent by C1 into the backbone, containing the topological changes, triggering the mass execution of the SPF algorithm.

Before moving on to the next section, make sure you enable the interface you previously disabled on R1. This, of course, will trigger an SPF update on X1.

[^SN]: On some network devices, including Arista cEOS, you do not necessarily need debug logging. They have a command similar to "show isis spf log" which will give you the same SPF information on demand. 

## Manual summarization

You are going to solve this problem by manually summarizing the stub networks from the level-1 area on the level-1-2 router C1. First, let's see the routing table on c1, so that we can refer back to it after the configuration task.

C1's routing table
{ .code-caption }
```
c1#show ip route isis

VRF: default
.....

I L1     10.0.0.1/32 [115/20]
via 10.1.0.2, Ethernet1
I L2     10.0.0.3/32 [115/20]
via 10.1.0.6, Ethernet2
I L1     172.16.0.0/24 [115/20]
via 10.1.0.2, Ethernet1
I L1     172.16.1.0/24 [115/20]
via 10.1.0.2, Ethernet1
I L1     172.16.2.0/24 [115/20]
via 10.1.0.2, Ethernet1

```

Unsurprisingly, we see L1 IS-IS routes to the loopback of R1, and all the stub networks attached to it. From the examination of C1's L2 LSP on X1, we also know that all those routes are propagated into the L2 backbone.

## Configuration Task

* On C1, summarize all the stub networks present on the R1 as a single level-2 summary route:

Summarization of level-1 routes is often done under the IS-IS process with a **summary address** command. Other devices, including cEOS, use a  **redistribute** command somewhere in the routing process hierarchy. That command should accept a **summary-address** (or similar) parameter that allows you to specify the summary route.

## Summarization Effects

The most important rules of manual summarization are simple: [^RF]

* the set of reachable addresses from L1 LSP is compared against the set of reachable addresses in L2 LSP. Redundant information is not copied from L1 to L2
* manually entered summary addresses are only included in the L2 LSP if they correspond to an address reachable in the level-1 area
* Any address in an L1 LSP that is not covered by a manually entered summary address is still copied in the L2 LSP.

Let's look at the effects produced by summarization in our case. Examine the routing table on C1 again. If you are on a modern device, like cEOS, note the absence of the summary route. You cannot see it in the routing table,  but you will find it in the level 2 LSPs generated by C1.

On a Cisco IOS device, you will see a slightly different view:

C1's routing table on IOS devices. Note the IS-IS summary route with a null0 next hop
{ .code-caption }
```
c1# show ip route isis

Gateway of last resort is not set

10.0.0.0/8 is variably subnetted, 7 subnets, 2 masks
i L1     10.0.0.1/32 [115/20] via 10.1.0.2, 00:07:19, Ethernet0/1
i L2     10.0.0.3/32 [115/20] via 10.1.0.6, 00:07:16, Ethernet0/2
172.16.0.0/16 is variably subnetted, 4 subnets, 2 masks
i su     172.16.0.0/22 [115/10], 00:03:41, Null0
i L1     172.16.0.0/24 [115/10] via 10.1.0.2, 00:07:19, Ethernet0/1
i L1     172.16.1.0/24 [115/10] via 10.1.0.2, 00:07:19, Ethernet0/1
i L1     172.16.2.0/24 [115/10] via 10.1.0.2, 00:07:19, Ethernet0/1

```

Cisco IOS has added an explicit summary route in the IS-IS process with a next hop of null0. The relevance of this route will become apparent soon.


C1's L2 LSP detail. Notice the presence of the summary route in the L2 LSP.
{ .code-caption }
```
c1#show isis database level-2 detail c1.00-00
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
IS-IS Level 2 Link State Database
LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
c1.00-00                     14   5909   619    126 L2  0000.0000.0002.00-00  <>
LSP generation remaining wait time: 0 ms
Time remaining until refresh: 319 s
NLPID: 0xCC(IPv4)
Hostname: c1
Area addresses: 49.0100
Interface address: 10.1.0.5
Interface address: 10.1.0.1
Interface address: 10.0.0.2
IS Neighbor          : x1.00               Metric: 10
Reachability         : 172.16.0.0/22 Metric: 10 Type: 1 Up
Reachability         : 10.0.0.1/32 Metric: 20 Type: 1 Up
Reachability         : 10.1.0.4/30 Metric: 10 Type: 1 Up
Reachability         : 10.1.0.0/30 Metric: 10 Type: 1 Up
Reachability         : 10.0.0.2/32 Metric: 10 Type: 1 Up
Router Capabilities: Router Id: 10.0.0.2 Flags: []
Area leader priority: 250 algorithm: 0

```

Observe that the presence of the summary route stopped individual propagation of the sub-networks it summarizes from level-1 to level-2. There are no reachability TLVs present for the individual stub networks anymore. The networks for which we do not have summary addresses are still propagated. Notice R1's loopback (10.0.0.1/32)  propagation.

In addition to simplifying the routing table of the devices in the L2 area, another immediate effect is that a topological change to any of the summarized networks will not be propagated into the L2 backbone anymore.

Lastly, ensure that changes in stub network topology from level-1 are no longer propagated to the L2 backbone:

On R1, shut down the Ethernet2 interface.
The SPF debug log on X1 should remain silent. [^SPF]

If you are on a cEOS device, as I am here, or any other devices that didn't introduce a summary route in the routing table of c1, continue shutting down all other stub network interfaces, Ethernet3, and Ethernet4.

Suddenly, once the last stub network interface is shut down, the IS-IS SPF debug log comes to life and reports the SPF calculation as a result of an LSP change.

Let's unpack what is happening. On C1:

C1's routing table after shutting down all stub network interfaces on R1
{ .code-caption }
```
c1#show ip route isis

......

I L1     10.0.0.1/32 [115/20]
via 10.1.0.2, Ethernet1
I L2     10.0.0.3/32 [115/20]
via 10.1.0.6, Ethernet2
```


According to the manual summarization rules outlined above, the summary route in the L2 LSP exists only as long as it corresponds to an address reachable in the level-1 area.

Confirm that the summary address was removed from the L2 LSP:

C1's L2 LSP detail after shutting down all stub network interfaces on R1
{ .code-caption }
```
c1#show isis database level-2 c1.00-00 detail
Legend:
H - hostname conflict
U - node unreachable

IS-IS Instance: Gandalf VRF: default
IS-IS Level 2 Link State Database
LSPID                   Seq Num  Cksum  Life Length IS  Received LSPID        Flags
c1.00-00                      9  42097  1184    118 L2  0000.0000.0002.00-00  <>
LSP generation remaining wait time: 0 ms
Time remaining until refresh: 884 s
NLPID: 0xCC(IPv4)
Hostname: c1
Area addresses: 49.0100
Interface address: 10.1.0.1
Interface address: 10.1.0.5
Interface address: 10.0.0.2
IS Neighbor          : x1.00               Metric: 10
Reachability         : 10.0.0.1/32 Metric: 20 Type: 1 Up
Reachability         : 10.1.0.0/30 Metric: 10 Type: 1 Up
Reachability         : 10.1.0.4/30 Metric: 10 Type: 1 Up
Reachability         : 10.0.0.2/32 Metric: 10 Type: 1 Up
Router Capabilities: Router Id: 10.0.0.2 Flags: []
Area leader priority: 250 algorithm: 0

```

In the printout above, you can see that the reachability TLV  for the 172.16.0.0/22 summary address is gone. The L2 LSP was updated, and consequently the update propagated across the L2 backbone.

This stands in stark contrast to what happens on an IOS device. Shutting down all stub interfaces on R1 has no ill effects. The presence of the IS-IS summary route in the routing table is enough to prevent the removal of the summary route from the L2 LSP of C1. No new LSP will be generated.



[^RF]: Manual summarization and the full rule set are described in detail in section 3.2 of RFC 1195


## Validation

Move to X1 and examine its routing table:

IS-IS routes on X1. The summary network is present. 
{ .code-caption }
```
x1# show ip route isis
.....
IPv4 unicast VRF default
I>* 10.0.0.1/32 [115/30] via 10.1.0.5, eth1, weight 1, 01:38:52
I>* 10.0.0.2/32 [115/20] via 10.1.0.5, eth1, weight 1, 01:38:53
I>* 10.1.0.0/30 [115/20] via 10.1.0.5, eth1, weight 1, 01:38:53
I   10.1.0.4/30 [115/20] via 10.1.0.5, eth1 inactive, weight 1, 01:38:53
I>* 172.16.0.0/22 [115/20] via 10.1.0.5, eth1, weight 1, 00:17:06

```

The summary network 172.16.0.0/22 should be present. 

Ensure we have end to end reachability :

Dataplane reachability test between X1 and r1
{ .code-caption }

```
x1# show ip route isis
x1# ping 10.0.0.1
PING 10.0.0.1 (10.0.0.1): 56 data bytes
64 bytes from 10.0.0.1: seq=0 ttl=63 time=1.877 ms
64 bytes from 10.0.0.1: seq=1 ttl=63 time=0.845 ms
....
--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.845/1.423/1.877 ms
```


[^SPF]: Unless you are unlucky and witness a periodic SPF run by pure coincidence. But it's easy to distinguish between the two.

**Next**: [Build an SR-MPLS Network with IS-IS](10-sr.md)

## Reference Information

### Lab Wiring

Point-to-Point Links

| Origin Device | Origin Port | Destination Device | Destination Port |
|---------------|-------------|--------------------|------------------|
| r1 | Ethernet1 | c1 | Ethernet1 |
| c1 | Ethernet2 | x1 | eth1 |


Stub Links

| Origin Device | Origin Port | Description          |
|---------------|-------------|----------------------|
| r1 | Ethernet2 | r1 -> stub |
| r1 | Ethernet3 | r1 -> stub |
| r1 | Ethernet4 | r1 -> stub |


!!! Note
The interface names depend on the lab devices you use. The printout was generated with user routers running Arista EOS and X1 running FRRouting.


### Lab Addressing

| Node/Interface | IPv4 Address | IPv6 Address | Description |
|----------------|-------------:|-------------:|-------------|
| **c1** |  10.0.0.2/32 |  | Loopback |
| Ethernet1 | 10.1.0.1/30 |  | c1 -> r1 |
| Ethernet2 | 10.1.0.5/30 |  | c1 -> x1 |
| **r1** |  10.0.0.1/32 |  | Loopback |
| Ethernet1 | 10.1.0.2/30 |  | r1 -> c1 |
| Ethernet2 | 172.16.0.1/24 |  | r1 -> stub |
| Ethernet3 | 172.16.1.1/24 |  | r1 -> stub |
| Ethernet4 | 172.16.2.1/24 |  | r1 -> stub |
| **x1** |  10.0.0.3/32 |  | Loopback |
| eth1 | 10.1.0.6/30 |  | x1 -> c1 |
