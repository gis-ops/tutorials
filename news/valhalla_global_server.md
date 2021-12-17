# Global Open Valhalla Server online!

Together with Valhalla's lead engineer Kevin Kreiser, we handed in a proposal to [FOSSGIS e.V.](https://www.fossgis.de) to fund the deployment of a [Valhalla](https://github.com/valhalla/valhalla) service with global coverage and **open access**. The proposal has since been approved :partying_face: :partying_face: 

The server is available on https://valhalla1.openstreetmap.de and accepts requests on all endpoints except for `/expansion`, `/height` and `/centroid`. The whole infrastructure consists of one server to build an updated routing graph continuously, while another server hosts the service on 16 threads. One server to answer requests also means we have to put tight-ish restrictions on the public access to the service: each user has a limit of 1 request per second and the service has a total rate limit of 100 requests per second. We still hope that this initiative will serve as in easy entrypoint for interested users and foster Valhalla's contributor community. 

On top of this, a web app is available on https://valhalla.openstreetmap.de with full support for all relevant [costing options](https://github.com/valhalla/valhalla/blob/master/docs/api/turn-by-turn/api-reference.md#costing-options).

FOSSGIS e.V. already funds the hosting of a [great variety of software projects](https://www.fossgis.de/aktivitäten/langzeitförderungen/) like JOSM, Overpass API, OSRM etc. Valhalla makes a great addition to this "portfolio" and we're very excited to monitor and maintain the service, and, saying this both as Valhalla co-maintainers and GIS • OPS, very grateful to FOSSGIS e.V. for the funding.
