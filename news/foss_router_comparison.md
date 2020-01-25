#

## Introduction

Free and open source (FOS) routing engines have gained massively in popularity, the latest after the shameless price increase of Google Maps in 2018. The clear advantages are

- **Flexibility**: use hosted services (Mapbox, GraphHopper or OpenRouteService) or host your own routing service
- **No vendor lock-in**: install your own routing service instance
- **Transparency**: open source code lets you examine the algorithms
- **Collaboration**: you can contribute and improve the routing service yourself or contract developers to do the job for you

In this article you'll learn about the details and differences of the following routing engines:

- Open Source Routing Machine (OSRM)
- GraphHopper
- OpenRouteService
- Valhalla

All these frameworks do a similar job, but differ heavily when looking at the details. Whether you wish to employ one of these services in your own server infrastructure or just use hosted versions from a hosting provider, we'll inform you about the most important questions.

## Routers

In the following sections you'll learn about the respective routing services in more detail. We'll mostly focus on the routing-related capabilities, i.e. **directions**, **isochrones** and **time/distance matrices**.

### Open Source Routing Machine (OSRM)

#### General

Arguably, OSRM has shaped the landscape of open source routing engines from the very beginning and set many important milestones since its publication in 2010. It has been first made public by Dennis Luxen (now Apple Maps, but pssht;)) during his research activities at the Karlsruhe Institute of Technology (KIT) and is up to this date the playground engine for all sorts of new algorithmic developments in the group of Prof. Wagner. In 2012 (and ever since) Mapbox hired a great deal of KIT routing experts and basically took over the day-to-day development of OSRM. However, these days Mapbox seemed to have dropped further development of OSRM silently in favor of Valhalla, an initial Mapzen product.

#### Capabilities

OSRM is generally aiming to be data source agnostic. While 99.99% of usages deploy OpenStreetMap as data source, it is technically capable to consume other data source as well, like TomTom or HERE. However, the process to do so is not well documented.

The OSRM framework comes with a number of services:

- `route`: classic routing and navigation service with rich output information
- `table`: **time only** aware origin-destionation matrix service
- `nearest`: snaps a coordinate to the road network and returns the `n` nearest matches
- `match`: matches GPS points/tracks to the road network in the most plausible way

It's worth noting, that **OSRM does not support isochrones** out-of-the-box. There used to be a [Mapbox extension](https://github.com/mapbox/osrm-isochrone), but hasn't been touched in 3 years.

##### Routing

OSRM's routing capabilities are almost legendary and have seen the longest development of any of the FOS routers we present here. The features most noteworthy are:

- Continental routes in milliseconds
- Possibility to include traffic information
- easy customization for new mobility profiles

OSRM saw the first ever implementation of a technology called Contraction Hierarchies (developed at KIT), which is also implemented in GraphHopper and OpenRouteService. This makes the calculation of extensively long routes super fast. Additionally OSRM deploys MLD (Mult Level Dijkstra)



## Open source and open data

Free and open source software (FOSS) had a questionable after taste for the longest time, being scolded for clunkiness and common user-unfriendliness. This concept has been overhauled in the past decade by a large army of developers who contributed millions of man hours to millions of open source projects. In some instances entire tech branches almost entirely rely on open source software, such as machine learning. Building software in the open with others to be able to review or even contribute source code makes the whole process entirely transparent.
