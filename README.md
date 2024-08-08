# Open-Source IS-IS Configuration Labs

This repository contains _netlab_ topology files for a series of IS-IS hands-on labs that will help you master numerous aspects of EBGP,  IBGP, and BGP routing policy configuration on a platform of your choice[^PC]. You can run them on [your laptop](https://netlab.tools/install/ubuntu-vm/) (including [Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon.html)), on a [local server](https://netlab.tools/install/ubuntu/), in the [cloud](https://netlab.tools/install/cloud/), or in a (free) [GitHub codespace](https://isis.bgplabs.net/4-codespaces/).

The labs cover:

* [Work with FRRouting](basic/0-frrouting)
* [Start the IS-IS Routing for IPv4](basic/1-simple-ipv4)
* [Explore IS-IS Data Structures](basic/2-explore)

Other labs are still under development. Follow [blog.ipspace.net](https://blog.ipspace.net/) or [Ivan Pepelnjak on LinkedIn](https://www.linkedin.com/in/ivanpepelnjak/) to find out when they will be ready.

See [lab documentation](https://isis.bgplabs.net/) for more details and the [complete list of planned labs](https://isis.bgplabs.net/3-upcoming/).

[^PC]: Some assembly required: while the Cumulus Linux VMs/containers used for external BGP speakers are easy to download, you'll have to build a Vagrant box or install a Docker container image for your platform.