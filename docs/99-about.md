# About the Project

In 2023, I started the [Open-Source BGP Labs project](https://bgplabs.net/) to recreate the labs I created in the early 1990s. As I [posted a status update a year later](https://blog.ipspace.net/2024/07/bgp-labs-year-later/), Henk Smit [made an excellent suggestion](https://blog.ipspace.net/2024/07/bgp-labs-year-later/#2330):

> If you ever want to do something similar for IS-IS, I'd be happy to help. I think it would already be helpful to just cover the basics of IS-IS. There is so little knowledge about IS-IS out there, that any new good resource would be awesome.

As I was involved in a similar project in the 1990s, it wasn't hard to persuade me to start a similar series of "_IS-IS from rookie to hero_" lab exercises. Welcome to the [Open-Source IS-IS Configuration Labs](https://isis.bgplabs.net/) project.

The project uses _[netlab](https://netlab.tools)_[^HT] to set up the labs and FRRouting containers or a [few other devices](1-setup.md#select-the-additional-devices-in-your-lab) as external BGP routers. You can use [whatever networking devices](1-setup.md#select-the-network-devices-you-will-work-with) you wish to work on, and if they happen to be supported by _netlab_, you'll get lab topology and basic device configuration for each lab set up in seconds[^XR]. Most lab exercises using external devices include device configurations for the external routers for people who love wasting time with GUI.

You'll find the lab topology files and initial device configurations in a [GitHub repository](https://github.com/bgplab/isis), but you might [explore the lab exercises first](https://isis.bgplabs.net/).

As always, everything starts with a [long wish list](3-upcoming.md). I probably missed something important -- please [open an issue](https://github.com/bgplab/isis/issues) or a [discussion](https://github.com/bgplab/isis/discussions), or (even better) become a contributor and submit a PR.

[^NL]: As long as it's supported by _netlab_.

[^HT]: When you happen to have a Hammer of Thor handy, everything looks like a nail waiting to be hit ;)

[^XR]: Unless you love using resource hogs like Nexus OS, IOS XR, or some Junos variants.
