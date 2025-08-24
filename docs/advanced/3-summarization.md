# Summarizing Level-1 Routes into Level-2 Backbone

By [Dan Partelly](https://github.com/DanPartelly)
{.author-byline }

In this exercise, we continue to reduce the amount of routing information in our network, this time on level-2 routers. At the same time, we'll address a critical instability issue in multilevel IS-IS networks. IS-IS was designed to limit the impact of topology changes in a CLNP[^CLNP] network to a single hierarchical level, but the addition of automatic distribution of level-1 IP routes into level-2 backbone broke that. Without route summarization, every change in IP reachability in a level-1 area is inevitably propagated into the level-2 backbone [^NE].

[^CLNP]: Connection-Less Network Protocol, the layer-3 protocol used in the long-obsolete ISO OSI network stack.

[^NE]: Network engineers with a background in programming will quickly realize that (besides hypothetical performance implications) minimizing information in routing tables and the shared state between level-1 and level-2 IS-IS hierarchy is also a tool to control complexity.

You'll practice the summarization of level-1 IS-IS routes (called *‌[Hierarchical Abbreviation of IP Reachability Information](https://datatracker.ietf.org/doc/html/rfc1195#section-3.2)* in [RFC 1195](https://datatracker.ietf.org/doc/html/rfc1195)) on a very simple three-router topology.

![Lab topology](topology-summarization.png)

[^SUM]: Summarization is a powerful techniques. It simplifies route tables, improves network scalability and decreases complexity, but it cannot be employed in all situations. There are situations where you want to maintain full L1-L2 wide visibility, to run BGP. Can you eat the cake and still have it? Perhaps. You can summarize everything, except /32 loopbacks. 

## Device Requirements

Use any device [supported by the _netlab_ IS-IS configuration module](https://netlab.tools/platforms/#platform-routing-support) that correctly implements the propagation of level-1 IP prefixes into the level-2 LSP database as required by RFC 1195.

Unfortunately, as of August 2025, FRRouting's IS-IS implementation does not distribute prefixes between level-1 areas and level-2 backbone, and thus cannot be used in this lab exercise.

## Starting the Lab

You can start the lab [on your own lab infrastructure](../1-setup.md) or in [GitHub Codespaces](https://github.com/codespaces/new/bgplab/isis) ([more details](https://bgplabs.net/4-codespaces/)):

* Change directory to `advanced/3-summarization`
* Execute **netlab up**
* Log into lab devices with **netlab connect**

## Existing Device Configuration

When starting the lab, _netlab_ configures IPv4 addresses and IS-IS protocol on the lab routers, resulting in a small multi-area, multi-level topology.

IS-IS parameters of individual lab devices are summarized in the following table:

| Node | IS-IS Area | System ID | IS type |
|------|-----------:|----------:|---------|
| x1 | 49.0001 | 0000.0000.0003 | level-2 |
| r1 | 49.0100 | 0000.0000.0001 | level-1 |
| c1 | 49.0100 | 0000.0000.0002 | level-1-2 |

R1 has three stub networks; their prefixes are advertised in the level-1 area 49.0100.

## Level-1 to Level 2 Spillover Effect

Before rushing into the router configuration, let's see what problem we're dealing with. This is what X1 has in its routing table after the lab is started:

IP routing table on X1 running FRR. It includes the three stub networks from the 172.16.0.0/16 range
{ .code-caption }
```
$ netlab connect x1 --show ip route
Connecting to container clab-summarization-x1, executing vtysh -c "show ip route"
...

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

This should not be surprising. We already know that L1/L2 routers perform automatic distribution of L1 routes into the L2  backbone. Let's confirm the presence of reachability TLVs for the stub networks in the L2 LSP of C1:

C1's level-2 LSP as viewed on X1. The stub networks are included in the LSP
{ .code-caption }
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

Next, let's verify that a change in the topology of the level-1 area 49.0100 propagates into the level-2 backbone and triggers the IS-IS Shortest Path First (SPF) algorithm on other level-2 routers.

Connect to the target router (X1) via SSH, ensure your session is configured to monitor logging messages[^TM], and enable debugging of IS-IS SPF events[^SN].

[^TM]: Logging messages are usually not sent to SSH sessions. You have to enable that on every SSH session with a command similar to **terminal monitor** (don't ask about the meaning of that command; it's a long story going all the way back to the 1980s).

[^SN]: On some network devices, including Arista cEOS, you do not have to enable SPF debugging. They have a command similar to **show isis spf log** that displays the relevant information on demand.

Enable IS-IS SPF debugging on X1 running FRRouting
```
x1# terminal monitor
x1# debug isis spf-events
```

Now we're ready to observe whether the changes in level-1 area 49.0100 are spilling over into the level-2 backbone. Let's connect to R1 in a separate session and shut down one of the stub network interfaces. Almost instantly, the SPF algorithm runs on X1:

SPF events on X1 (running FRRouting) triggered by a subnet loss on R1
{ .code-caption }
```
[DEBG] isisd: [SFWMK-K9QH2] ISIS-SPF (Gandalf) L2 SPF schedule called, lastrun 298 sec ago Caller: lsp_update isisd/isis_lsp.c:551
[DEBG] isisd: [KD9RA-6JFGA] ISIS-SPF (Gandalf) L2 SPF scheduled 0 sec from now
[DEBG] isisd: [N48RF-Z09QJ] ISIS-SPF (Gandalf) L2 SPF needed, periodic SPF
```

You can also check that the C1 L2 LSP has been changed:

C1's LSP on X1 after R1's Ethernet2 interface is shut down. The reachability TLV for 172.16.0.0/24 is missing
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

Let's recap the whole sequence of events triggered by the interface shutdown on R1:

* R1 generates and transmits an updated level-1 LSP to reflect the topology change
* C1 receives the LSP and updates its level-1 LSDB
* C1 runs L1 SPF and calculates the new best routes
* C1 updates its level-2 LSP to reflect the changes in level-1 routes
* C1 sends the updated Level-2 LSP to its neighbors
* The updated C1 level-2 LSP triggers the SPF algorithm on all L2 routers

This cascading effect demonstrates how a local topology change in a level-1 area can impact the entire level-2 backbone.

Before proceeding to the next section, re-enable any interfaces you shut down on R1. This action will trigger another SPF update on X1 (but now you know what's causing it).

## Configure Route Summarization

To minimize the impact of changes in a level-1 area[^WC], configure summarization of R1's stub networks on the Level-1-2 router C1 into a single level-2 summary route (172.16.0.0/22).

[^WC]: As long as the summary information won't change, the changes in the level-1 area won't be flooded into the level-2 backbone anymore. However, the summary prefix might be removed from the L2 LSP when all the level-1 routes within the prefix disappear. The L2 LSP should also change when the cost of the summary prefix (as calculated from the costs to reach the level-1 routes) changes.

!!! Tip
    Summarization of level-1 routes is often done under the IS-IS process with a **summary address** command. Other devices, including Arista EOS, use a  **redistribute** command somewhere in the routing process hierarchy. That command should accept a **summary-address** (or similar) parameter that allows you to specify the summary route.

## The Effects of Route Summarization

Here are the highlights of the [lengthy RFC 1195 section](https://datatracker.ietf.org/doc/html/rfc1195#section-3.2) describing the route summarization process (read the original if you're interested in gory details):

* Each level-2 router may be configured with one or more summary prefixes
* The set of reachable addresses from L1 LSP is compared against the set of reachable addresses in L2 LSP. Redundant information is not copied from L1 to L2.
* The metric of the summary prefixes is configured, not calculated from the costs of level-1 prefixes[^SPM]
* Summary prefixes are only included in the L2 LSP if they correspond to at least one in-area prefix.
* Any address in an L1 LSP that is not covered by a summary prefix is still copied in the L2 LSP.

[^SPM]: A stark deviation from how engineers familiar with OSPF would expect route summarization to work.

We should thus see the following effects of route summarization in our network:

* Individual reachability TLVs for the summarized level-1 prefixes are no longer present in Level-2 LSPs; they're replaced by the configured summary route. Instead of the three TLVs for the R1 stub subnets, the C1 L2 LSP should contain a single reachability TLV for the summary prefix.
* Level-1 routes without a corresponding summary prefix are still distributed into level-2 LSP (we should see R1's loopback 10.0.0.1/32 still being advertised)
* Level-2 routers have smaller routing tables.

An even more important consequence of summarization is enhanced network stability. Topological changes within a level-1 area no longer trigger the SPF algorithm in the L2 backbone *as long as the changes' results are limited to the summarized prefixes*. 

## Validation

You can use the **netlab validate** command if you’re using netlab release 1.8.4 or later and run FRRouting on the external routers. This is the printout you should get after completing the lab exercise:

![](validate-summary.png)

You could also do manual validation on C1 and X1:

After configuring the summary prefix, examine C1's L2 LSP:

C1's L2 LSP detail.
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

The three TLVs describing the R1 stub networks should be gone, replaced by a single 172.16.0.0/22 reachability TLV.

Next, examine X1's routing table and verify that it can still reach R1's stub networks.

IS-IS routes on X1 include the summary prefix advertised by C1
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

Finally, to confirm that the changes in stub networks are no longer propagated into the level-2 backbone:

* Enable SPF debugging on X1
* Shut down the loopback interface on R1. You should observe an SPF event on X1
* Shut down a stub interface on R1
* Verify that the change in a stub network reachability does not trigger an SPF event on X1[^SPF]
* Reenable all interfaces on R1.

[^SPF]: Unless you are unlucky and witness a periodic SPF run by pure coincidence. It's usually easy to distinguish between the two.

## Platform-Specific Behavior

Let's look at the effects produced by summarizing R1's stub networks. Examine the routing table on C1 again. You will notice that it's pretty much the same as before:

C1's routing table after summarization, as viewed on Arista cEOS
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

If you are on a device like cEOS, note the absence of any summary routes in the routing table. You will find it in the level 2 LSPs generated by C1.

Cisco IOS devices have a different behavior. Notice the presence of an IS-IS summary route with a next hop at interface Null0:

C1's routing table after summarization as viewed on Cisco IOL
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

The relevance of this route will become apparent soon.

Before configuring the route summarization, examine C1's current routing table (you'll see why we need this in a minute):

IP routing table on C1 running Arista cEOS
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

The routing table (as expected) contains the routes to R1'2 stub networks and the R1/X1 loopback interfaces.

If you run the lab on an Arista cEOS, we have the opportunity to illustrate additional summarization behavior.

Continue the exercise by shutting down all remaining stub network interfaces on R1. Assuming you are on an Arisa cEOS as I am, and disabled Ethernet2 earlier, shut down Ethernet3 and Ethernet4 interfaces.

Once the last stub network interface is shut down, the IS-IS SPF debug log reports a new SPF calculation as a result of an LSP change.

Let's unpack what is happening. On C1:

C1's routing table after shutting down all stub network interfaces on R1 (Arista cEOS)
{ .code-caption }
```
c1#show ip route isis

......

I L1     10.0.0.1/32 [115/20]
via 10.1.0.2, Ethernet1
I L2     10.0.0.3/32 [115/20]
via 10.1.0.6, Ethernet2
```


According to the IS-IS manual summarization rules outlined above, summary routes in L2 LSPs are maintained only when they correspond to at least one reachable address within the L1 area. When all constituent networks become unreachable, the summary route is withdrawn.

Let's confirm this:

C1's L2 LSP detail after shutting down all stub network interfaces on R1 (Arista cEOS)
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

In the printout above, you can see that the reachability TLV  for the 172.16.0.0/22 summary address is gone. The L2 LSP was updated, and the update propagated across the L2 backbone.

This stands in stark contrast to what happens on an IOS device. Shutting down all stub interfaces on R1 has no ill effects. The presence of the IS-IS summary route in the routing table is enough to prevent the removal of the summary route from the L2 LSP of C1. No new LSP will be generated.

Before moving on, enable all stub interfaces previously disabled on router R1.

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
	  The interface names depend on the lab devices you use. The printout was generated with R1 and C1 running Arista EOS, and X1 running FRRouting.

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
