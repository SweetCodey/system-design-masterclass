## Introduction

### What is a Maps Service

Imagine you are traveling to a new place. You ask someone for directions for nearby restaurants, check traffic, and decide the best route to reach your destination. A maps service does the same thing digitally. It helps you understand where things are and how to reach them.

Instead of paper maps or asking people, you open a map application to search for places, explore nearby locations, and navigate. The app shows roads, buildings, landmarks, and real-time information like traffic or business hours. Behind the scenes, the system continuously collects geographic data, processes it, and presents it visually so you can understand your surroundings quickly.

![](Resources/Intro_MapService.png)

### How Maps Work

When you open a map application, the system first determines your location and displays the surrounding area. As you move the map, the backend fetches only the required geographic data and renders it on the screen. If you search for a place (e.g., “restaurants near me”), the search system finds relevant places and shows them on the map.

If you choose a destination, the routing system calculates possible paths, estimates travel time, and suggests the best route based on distance and traffic conditions. During navigation, the system continuously updates your position and adjusts directions in real time.

![](Resources/Intro_MapServiceWorking.png)

---

## Requirements

### Functional Requirements

In an ideal scenario, a user goes through a sequence of flows such as searching for a place, viewing place on a map, and navigating to the destination when using a map application. The functional requirements are derived from this user journey.

![](Resources/HighLevelFlow.png)

**Search**

* **Place Search** – Users can search for places by name or keywords and get ranked results. 
* **Nearby Search** - Users can search nearby places like "restuarants near me" or "malls within 5 kms"

**Rendering**
* **Map Rendering** – Display map tiles based on the user’s current viewport.

**Routing**
* **Route Calculation** – Compute a path between source and destination.
* **Real-time Navigation** – Continuously track user location and re-route if needed.

### Non-Functional Requirements

* **Low Latency** – Search, tile loading, and routing responses must be with in 100 ms.
* **High Availability** – Core features should remain 99.99% during peak usage.
* **Scalability** – System must handle millions of concurrent users.
* **Geospatial Accuracy** – Location tracking and routing must be precise with an acceptable error of + or - 100 meters.

---

## API Design
### Rendering

Rendering displays the map data into the user's device for visualization.

![](Resources/API_Rendering.png)

**HTTP Method & Endpoint**

We use `GET` since we are retrieving the map data. The endpoint would be: `GET /v1/tiles/vector/{z}/{x}/{y}`. Here `x` and `y` represents the coordinates and `z` is the zoom level.

**HTTP Request**
- x - X coordinate of the tile
- y - Y coordinate of the tile
- z - Zoom level

**HTTP Response**

The response will be binary data (pbf - Protocolbuffer Binary Format) containing layers such as roads, buildings, water, and places. Since it is binary, we cannot visualize the response. But after decoding, it looks something like below:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "class": "primary",
        "name": "Main Road"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [...]
      }
    }
  ]
}
```

### Routing

Routing finds the fastest possible route from source to destination and provides turn by turn instructions to reach the destination. This is the core "Point A to Point B" service. It uses algorithms on the static road graph to return a polyline (a compressed string of coordinates).

![](Resources/API_Routing.png)

**HTTP Method & Endpoint**
We use the endpoint `/v1/routes` to calculate a route between a source and a destination. The `POST` method is preferred because the request contains structured and potentially sensitive data, such as latitude and longitude, which reveal the user’s location.

If `GET` were used, these values would appear in the URL query string, making them more likely to be logged by servers, proxies, browser history, and intermediary systems. `POST` places the data in the request body, reducing unintended exposure and avoiding URL length limitations when sending complex routing parameters such as waypoints or preferences.

**HTTP Request**
```
{
  "routeId": 123, // Optional Id. Needed for re-routing
  "source": {
    "lat": 12.9941,
    "lng": 80.1709
  },
  "destination": {
    "lat": 13.0418,
    "lng": 80.2337
  },
  "mode": "car"
}
```

**HTTP Response**

The response contains an array consisting of multiple routes sorted in the order of durationSeconds (ETA) ascending.

```
[
  {
  "routeId": 123,
  "distanceMeters": 15200,
  "durationSeconds": 2400,
  "geometry": "encoded_polyline_string",
    "steps": [
      {
        "maneuver": "depart",
        "roadName": "GST Road",
        "distanceMeters": 1200,
        "durationSeconds": 180
      },
      {
        "maneuver": "turn-right",
        "roadName": "Anna Salai",
        "distanceMeters": 8000,
        "durationSeconds": 900
      },
      {
        "maneuver": "arrive",
        "roadName": "Destination",
        "distanceMeters": 0,
        "durationSeconds": 0
      }
    ]
  }
]
```

## High Level Design
Below are some of the terms we frequently come across in the upcoming sections of the document.

- **Bounding Box** — A bounding box is a rectangle used to represent an area on the map so the backend system can fetch only what lies inside it (e.g., the part of Chennai visible on your screen).

- **GIS (Geographic Information System)** — GIS is a software used to store, analyze, and visualize location data (e.g., city planners using GIS to study traffic patterns or land usage).

- **Image Pyramid** — An image pyramid is multiple versions of the same map image at different resolutions so that maps can load quickly at any zoom level (e.g., blurry world view when zoomed out and detailed streets when zoomed in).

- **Map Projection** — Map projection is the mathematical method used to convert the curved Earth into a flat map you can scroll on your screen (e.g., Web Mercator used by Google Maps).

- **Raster** — Raster maps are pre-rendered images made of pixels that show the map as a picture (e.g., satellite imagery tiles).

- **Spatial Database** — A spatial database stores geographic objects like places, roads, and regions so they can be queried by location (e.g., PostGIS storing all buildings in a city).

- **Tile** — A tile is a small square piece of the map that loads individually so only the visible area is fetched (e.g., the few squares you see when zooming into a neighborhood).

- **Vector** — Vector maps represent the world as shapes like points, lines, and polygons instead of images, allowing dynamic styling (e.g., roads drawn as lines that stay sharp when zooming).

### Rendering

Rendering is the process of turning geographic data into something user can see and understand. When thinking about rendering a map, a few questions naturally come to mind:

1. How is geographic data captured and stored in the system? Is it stored as images or in a special representation?
2. How is the stored geographic data displayed to users quickly?
3. The world is a sphere — how is a spherical shape rendered on a flat 2D screen?

By answering these questions, we can understand how maps are rendered.

At a high level, rendering works by dividing the world into small sections called **tiles**, deciding how geographic information is represented inside those tiles, and loading only what the user currently sees. A digital map is not a single large image stored somewhere. Instead, it is assembled piece by piece as you pan and zoom.

![](Resources/HLD_Rendering.png)

#### 1. How Geographic Data Is Captured and Stored

Map data comes from many sources such as satellites, aerial imagery, mapping vehicles, and user contributions. The world is not captured as a single image but as many raw images collected over time.

An ingestion pipeline processes this raw imagery to make it suitable for fast retrieval.

During ingestion:

1. Raw images are aligned and stitched together to create a seamless global view. This step corrects color differences perspective, and overlaps.  
2. Multiple versions of the imagery are generated at different resolutions. High-resolution data is used for close zoom levels, while lower-resolution versions are used when zoomed out. This set of resolutions is known as an **image pyramid**.  
3. Each resolution is divided into small square tiles. At the lowest zoom level the entire world may be a single tile, and with each zoom level the number of tiles grows rapidly.  
4. These tiles are stored as static image files in distributed storage for fast delivery.

Because this work happens ahead of time, opening the map does not require image processing. The client simply requests the tiles needed for the current viewport.

![](Resources/HLD_Rendering_Capture.png)

These pre-rendered image tiles are called **raster tiles**. Raster tiles reduce computation on the user’s device because they are just images, but they are bandwidth-heavy and have a fixed appearance. Changing the style — for example switching to dark mode — requires regenerating the tiles.

**Vector Model**

To overcome the limitations of raster tiles, modern mapping systems represent geographic data using **vectors**.

Vectors are not images. They are geometric descriptions of the world. A place is stored as a **point**, a road as a **line string**, and areas such as buildings or parks as **polygons**. Instead of sending pixels, the system sends instructions describing what exists in a region.

![](Resources/HLD_Rendering_Vector.png)

Vector geometry is typically stored in spatial databases such as PostgreSQL with the PostGIS extension. During preprocessing, this geometry is organized into vector tiles, where each tile contains only the features that intersect that region and zoom level. These tiles are stored in object storage and served through CDNs, making them highly cacheable and efficient to distribute.

As vectors are mathematical representations rather than fixed images, the map remains crisp at any zoom level and can be styled dynamically by the client. 

![](Resources/RasterVsVector.gif)

#### 2. How the Geographic Data Displayed to Users

For raster maps, tiles are generated during ingestion and stored as images. When a user opens the map, the client calculates which tiles are visible and requests them from the server. The request endpoint typically looks like: `https://tile.maps.com/.../z/x/y.png`. Here, `x` and `y` represent tile coordinates and `z` represents the zoom level. The server simply retrieves the pre-generated image and returns it.

For vector maps, the retrieval pattern is similar but the payload differs. Instead of returning an image, the server returns structured geographic data describing the features within the tile. The endpoint usually looks like: `https://tile.maps.com/.../z/x/y.pbf`. The `.pbf` file is a compact binary format that contains points, lines, polygons, and their attributes.

When the client receives a vector tile, it decodes the geometry, applies styling rules, and renders the map locally. This shifts rendering from the server to the client. Raster tiles deliver the final picture, while vector tiles deliver the instructions needed to draw that picture, enabling dynamic styling, filtering, and smoother interactions.

**Hybrid Rendering**

Hybrid rendering combines raster and vector data in the same map view to balance performance and clarity. Raster tiles are used for complex, static imagery like satellite or terrain backgrounds, while vector data is used for interactive elements such as roads, labels, and markers.

![](Resources/Rendering_Hybrid..png)

This approach keeps photographic backgrounds efficient to load while allowing text and map features to stay sharp, dynamic, and interactive.

**Dynamic / Real-time Layers**

Dynamic layers are map overlays that show frequently changing information like live traffic, transit delays, or weather. Unlike roads and buildings, which rarely change, these layers are fetched separately and rendered on top of the base map in real time.

![](Resources/Rendering_Dynamic.png)

By separating fast-changing data from the static map, the system avoids constantly regenerating base tiles whenever traffic or other live conditions update.

#### 3. How is a Spherical Shape Rendered on a Flat 2D Screen

The Earth is spherical, but screens are flat. To display geographic data on a 2D surface, mapping systems use a mathematical transformation called a **map projection**.

A map projection converts latitude and longitude — coordinates on a sphere — into x and y positions on a flat plane. This transformation allows the curved surface of the Earth to be represented as a scrollable rectangle that can be divided into tiles. Most modern web maps use the **Web Mercator projection**. Conceptually, you can imagine wrapping a cylinder around the Earth, projecting the surface onto that cylinder, and then unrolling it into a flat map. This creates a continuous coordinate space where every location can be positioned on a grid. Web mercator answers `where does this appear on the screen?`

![](Resources/HLD_Rendering_Projection.png)

Web Mercator preserves local shapes and angles, which makes roads, buildings, and navigation directions appear natural when zoomed in. However, this comes with distortion: areas near the poles appear larger than they are in reality. Digital maps accept this trade-off because usability and smooth interaction are more important than perfectly accurate global area representation.

Projection also enables the tiling system described earlier. Once geographic coordinates are converted into planar coordinates, the world can be split into a consistent grid, allowing tiles to align across zoom levels and making caching and retrieval efficient. In practice, rendering follows a sequence: geographic coordinates are projected into a flat coordinate space, the viewport determines which tiles intersect that space, and those tiles are fetched and drawn on the screen. Projection therefore acts as the mathematical bridge between the real world and the visual map.

#### End-to-End Rendering Flow

![](Resources/HLD_Rendering_Flow.png)

1. User interacts with the map and the client calculates viewport bounds, applies **Web Mercator projection**, and determines required tile coordinates `(z, x, y)`. Client fetches the tile if it is already available in the **Local HTTP/IndexedDB cache**.
2. If the tile is not in client cache, it requests tiles from the **CDN**, which serves cached tiles from the edge whenever possible.
3. On a CDN miss, the request is routed to the **API Gateway** of the Rendering Service.
4. The API Gateway performs **authentication and rate limiting** before routing the request to the **Tile Service**.
5. The **Tile Service** parses the tile coordinates and computes the bounding box (latitude and longitude) for that tile. Then it checks a **Distributed Cache (Tile Cache)** for a precomputed tile.
6. On cache miss, the precomputed tile is fetched from **Tile Storage**.
7. If the tile does not exist, the **Tile Service** queries the **Spatial Database** using **Quadtree or R-Tree indexing**. It retrieves raw geometry, clips it to tile bounds, and performs **line simplification** (e.g., via Douglas-Peucker algorithm).
    * **Quad Tree** - A spatial data structures used to quickly find geographic features (like buildings or roads) within a specific map tile without searching the entire global database. A Quad-Tree recursively divides a 2D area into four squares to pinpoint locations, while an R-Tree groups nearby objects into "minimum bounding rectangles" for efficient range queries. (TK - Add dive-deep)
    * **Douglas-Peucker Line Simplification** - This algorithm reduces the number of points in a complex curve (like a jagged coastline or a winding road) to create a simpler, "smoother" version that uses less data. It identifies and keeps only the most essential points that define the shape's overall structure, discarding minor details that wouldn't be visible at lower zoom levels. (TK - Add dive-deep)
8. The generated tile is stored in **Tile Storage** and cached in the **Tile Cache**.
9. The **Tile Service** returns the tile data via the API Gateway.
10. The tile data is cached in the CDN and sent to the client. Client decodes vector tiles, applies **Style JSON**, and renders via **WebGL/GPU**.
11. The client makes a parallel, lightweight request to a **Dynamic Data API Gateway** to fetch real-time layers like traffic or incidents.
12. The API Gateway routes the request to the **Traffic Service**.
13. The traffic data (segment speeds) is fetched from the **Traffic Cache**.
14. On cache miss, the traffic data is fetched from the **Traffic Database**.
15. The **Traffic Service** returns the traffic data to the client via the API Gateway. The API Gateway returns the traffic data to the client device, which performs **client-side composition** to render the overlay on top of the base map. (Step 15a and 15b)

> Traffic data is mainly collected from millions of smartphones and connected vehicles that continuously send GPS location and speed information. This data is matched to specific road segments, filtered to remove noise (like parked cars), and used to calculate real-time traffic speed. The processed results are stored in fast in-memory systems for live updates and in historical databases to help predict future traffic patterns.

### Routing
Routing is the process of finding a path between a source and a destination. The map system tries to provide the best possible path so that users can travel from source to destination faster. 

When thinking about routing, a few questions naturally arise:

1. How are roads represented inside the system?
2. How is the shortest or fastest path calculated?
3. How does navigation adjust in real time?

By answering these, we can understand how routing systems work.

#### 1. How are roads represented inside the system
In a map system, the world is modeled as a Directed Weighted Graph.

- **Nodes**: Intersections or dead ends.
- **Edges**: Road segments connecting nodes.
- **Weights (Costs)**: A numerical value representing the "cost" to traverse an edge. It isn't just distance. It’s a function of speed limits, road type, turn restrictions, and live traffic.

![](Resources/HLD_Routing_Representation.png)

At a global scale, a single road graph is too large to fit in memory. So, the global graph is divided into smaller, manageable "shards" or partitions based on geography (e.g., by city or state).

The road data is stored in a Spatial Database (like PostgreSQL with PostGIS). For routing, the data is extracted from the spatial database and converted into a **Directed Weighted Graph** aka **Road Graph**. An offline job reads the spatial data, identifies intersections (Nodes) and roads (Edges), and builds the Road Graph. This graph is "sharded" (e.g., a "South India" shard, a "Karnataka" shard) so the Routing/navigation Service can load only what it needs.

#### 2. How is the shortest or fastest path calculated?

We know that roads are modeled as a graph, where intersections are nodes and road segments are edges. To navigate from a source to a destination, we need to compute the shortest or fastest path between them. A straightforward way to do this is **Dijkstra’s Algorithm**.

Dijkstra starts from the source and repeatedly expands the node with the smallest accumulated distance. It continues this process until the destination is reached, guaranteeing the shortest path.

![](Resources/Routing_Djikstra.png)

The limitation is that Dijkstra has no awareness of the destination’s direction (**uninformed search**). It expands outward uniformly, exploring many unnecessary nodes. In large road networks with millions of nodes, this leads to excessive computation and higher latency.

Since modern map systems must compute routes in milliseconds and often recompute during navigation, running full Dijkstra each time is inefficient. Therefore, production systems use more optimized techniques such as **A\* (A-Star)** and **Contraction Hierarchies** that reduce the search space while still guaranteeing optimal results.

**A\*  (A-Star)**

Assume you are driving from Chennai Airport to Marina Beach. The road network includes small residential streets, arterial roads, and highways. If we ran Dijsktra, it would expand in all directions even though Marina Beach lies northeast of the airport.

A* is a superior modified version of Djikstra's algorithm. It uses straight-line distance to Marina Beach as a **heuristic**. That is, at each intersection (node), it evaluates:
* How far have I driven so far?
* How far does this road appear from Marina Beach?

If one road heads generally toward the coast and another heads inland, A* prioritizes the coastal direction. It does not blindly expand all neighborhoods.

![](Resources/HLD_Routing_AStar.png)

**Contraction Hierarchies**

Assume another scenario, where you are driving from Chennai to Banglore. The road netwrok includes thousands of local streets, city arterial roads, and national highways. In reality, long-distance travel looks like: `local road → city arterial → National highway → city arterial → local road`. So, you do not evaluate every residential street between the two cities.

So, if we use A*, it still explores many nodes in large-scale routing (e.g., Chennai → Bangalore). It improves direction but does not shrink the graph.

Contraction hierarchies instead of improving the search strategy, it changes the graph itself. Contraction hierachies work by preprocessing the road network graph and add shortcut edges by bypassing unnecessary edges such as small residential intersections.

So, instead of exploring hundreds of local streets, arterials, hundreds more streets, and highway, the graph contains `Chennai Arterial → National Highway Entry → National Highway Exit → Bangalore Arterial`. At query time, Contraction Hierarchies run a **bidirectional djikstra** search — one from the source and one from the destination — and only move through higher-level roads in the hierarchy. By avoiding lower-level streets and meeting in the middle, the algorithm explores far fewer nodes than a full graph search.


![](Resources/HLD_Routing_Contraction_Hierarchies.png)

> Contraction Hierarchies (CH) work well when edge weights are mostly static because shortcut weights are precomputed and fixed. When traffic frequently changes travel times, classic CH becomes unsuitable since updating weights would require rebuilding the hierarchy.
> **Customizable Contraction Hierarchies (CCH)** solve this by separating structure from weights. The hierarchy (node order and shortcuts) is built once, while shortcut weights are recomputed quickly whenever traffic updates occur. This enables fast routing with dynamic traffic without rebuilding the entire graph. CCH separates structure from weights — the hierarchy is built once, and only shortcut weights are efficiently recomputed when traffic changes, avoiding a full rebuild.

#### 3. How does navigation adjust in real time

Consider a scenario where you are driving from Chennai Airport to T Nagar during evening traffic. The initial route is `Airport → GST Road → Kathipara → Anna Salai → T Nagar` and the estimated time is **40 mins**. While you drive, your phone sends location updates every few seconds via GPS (Global Positioning System). Each update contains atitude, longitude, speed, and direction. 

Raw GPS data is noisy. You may appear slightly off the road. So the system performs **map matching**. It snaps your GPS coordinate to the most likely road segment using proximity, and direction. Now the system knows “You are on GST Road, heading north”. Typically we use **Hidden Markov Model (HMM)** for map matching. A Hidden Markov Model is a probabilistic model used to infer a sequence of hidden states from noisy observations, assuming each state depends only on the previous one. (TK - Add dive deep)

![](Resources/Routing_HMM.png)

Suppose there is a right turn and you missed it, the original route expected is "Turn right at Kathipara". But you continued straight. The routing system checks: Is the user still on planned route? and Is current position within allowed deviation threshold?. If not, it triggers re-routing. Re-routing considers the current GPS location as source and computes the new best possible route to reach the destination. 

**ETA Update in Real-time**

ETA (Estimated Arrival Time) tells the remaining travel time to reach the destination from the user's current position. It is initially calculated during route computation from the source to the destination. However, as time passes and traffic conditions change along the route, the ETA is expected to change as well.

Every few seconds, the device sends updated GPS coordinates. The map matching logic snaps the raw GPS coordinates to the nearest road segment. At this point, the system has both the planned route (a list of edges) and the user’s current position on that route. Using the latest traffic weights, the system recomputes the ETA based on the remaining segments of the route.

![](Resources/Routing_ETA.png)

#### End to End Flow

![](Resources/HLD_Routing_Flow.png)

1. Client calls `POST /v1/routes` endpoint with source, destination, and travel mode (Eg: Bike, Car, etc)
2. The API Gateway of the Navigation Service handles the request and route it to the Navigation Service.
3. The **Navigation Service** uses HMM algorithm to snap the raw latitude and longitude to the nearest road segments using spatial index (Eg: R-tree). It then converts the coordinates into graph node IDs
4. The **Navigation Service** checks the **Route Cache** for cached route for the combination of source node, destination node, and travel mode. If a route exists, it returns immediately.
5. If route doesn't exist in cache, the **Navigation Service** loads the graph from **Road Graph Cache**. This contains the pre-computed CCH heirarchy structure
6. The **Navigation Service** fetches the traffic weights of the edges from in-memory **Traffic Cache**. We use the cache instead of invoking **Traffic Service** to provide ultra low-latency response for route calculation.
    * a) **Traffic Stream Processor Service** listens to the **Traffic Stream** for traffic events published by the **Traffic Service**
    * b) The traffic events from the **Traffic Stream** are processed and stored in the **Traffic Cache** with a shorter TTL (Eg: 3 mins) as traffic rapidly change.
7. The **Navigation Service** use the real-time traffic weights and runs the customization phase of CCH where the shortcut weights are recomputed based on the traffic weigths.
8. The **Navigation Service** runs bi-directional Djikstra's on the CCH hierarchy to find the best route. Finally it expands the shortcut edges back into original road segments to produce full geometry.
9. For turn by turn direction, the path segments are converted to human-readable maneuvers using road metadata (e.g., turn angle, road name, restrictions).
10. Finally, the response is returned to the client via the API Gateway. (Step 10a and 10b)

## Dive Deep Insights
TK - Yet to start