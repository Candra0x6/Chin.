

## 🧭 Product Requirements Document (PRD)

**Project Title:**
Emergency Department 3D Flow Visualization

**Goal:**
Create an interactive, low-poly 3D visualization showing how patients move through an emergency department — from **Entrance → Triage → Treatment → Boarding → Exit** — over time.

**Purpose:**
This visualization helps non-technical stakeholders (hospital planners, operations teams) understand bottlenecks in patient flow at a glance.

---

### 1. Overview

The scene is a **3D isometric layout** showing simplified rooms of an emergency department.
The view should look clean, modern, and minimal — no textures, only solid colors.
Each department (Triage, Treatment, Boarding) is clearly separated by walls and floor color zones.
Simple human figures and beds represent patients and staff.

---

### 2. Core Features

| Feature                    | Description                                                                                                            |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **3D Scene Layout**        | A top-down isometric camera showing 4 main zones (Entrance, Triage, Treatment, Boarding, Exit).                        |
| **Low-poly Design**        | Simplified geometry for walls, beds, and people — minimal detail, pastel colors, soft lighting.                        |
| **Patient Flow Animation** | Small humanoid figures move along a defined path from Entrance → Exit over time.                                       |
| **Labels**                 | Each section has large, flat white 3D text labels on the floor: “ENTRANCE”, “TRIAGE”, “TREATMENT”, “BOARDING”, “EXIT”. |
| **Lighting**               | Ambient + Directional lighting with soft shadows. No reflections or metallic effects.                                  |
| **Interactivity**          | OrbitControls for simple camera movement (pan, zoom, rotate). No click interactions required.                          |
| **Time Bar**               | A flat horizontal bar at the bottom labeled “TIME”, showing progress of the simulation.                                |

---

### 3. Visual Style Guide

| Element         | Shape                           | Color                | Notes                               |
| --------------- | ------------------------------- | -------------------- | ----------------------------------- |
| **Floor**       | Flat rectangular plane          | Dark gray (#303030)  | Main background floor               |
| **Walls**       | BoxGeometry                     | Light gray (#B0B0B0) | 2m high partitions separating zones |
| **Beds**        | BoxGeometry + pillow cube       | Green (#88C999)      | Simple medical beds                 |
| **Patients**    | Capsule + sphere                | White (#FFFFFF)      | Small humanoid shapes               |
| **Staff**       | Capsule + sphere                | Blue (#3399FF)       | Distinguish from patients           |
| **Triage Zone** | Red floor plane                 | Dark red (#882222)   | Highlights patient intake area      |
| **Labels**      | 3D Text                         | White (#FFFFFF)      | Labeled floor text for each zone    |
| **Lighting**    | AmbientLight + DirectionalLight | Soft white           | Shadows optional for readability    |

---

### 4. Scene Layout Specification

```
Coordinate System:
- X-axis: left → right (Entrance → Exit)
- Z-axis: top → bottom (Depth of each section)
- Y-axis: vertical height (camera elevation)

Zone Dimensions:
- Entrance Area: small open space (width 2, depth 4)
- Triage Area: 4x10 plane, red tint
- Treatment Rooms: 4x10 with internal walls dividing rooms
- Boarding Area: 4x10 with multiple beds in open space
- Exit: small area (2x4)

Object Count Estimate:
- 8–10 beds total
- 8–10 humanoid figures
- 3–4 walls separating zones
- 5 zone labels
```

---

### 5. Functional Requirements

| ID  | Requirement                                            | Priority |
| --- | ------------------------------------------------------ | -------- |
| FR1 | The system must render a 3D scene with 5 labeled zones | High     |
| FR2 | Patients move gradually from Entrance to Exit          | High     |
| FR3 | The time bar animates in sync with patient flow        | Medium   |
| FR4 | Camera can orbit, zoom, and pan                        | Medium   |
| FR5 | Scene resizes responsively to window size              | Medium   |

---

### 6. Technical Specification

**Framework:** [Three.js](https://threejs.org/)
**Rendering:** WebGLRenderer (antialias = true)
**Modules:**

* `OrbitControls` for navigation
* `TextGeometry` + `FontLoader` for 3D text
* Optional `gsap` for smooth animations

**Scene Units:**
1 unit = 1 meter (approximate scale)

**Animation Flow Example:**

1. Patient enters from `x = -8`
2. Moves to `x = -4` (Triage)
3. Waits 3 seconds
4. Moves to `x = 0` (Treatment)
5. Waits 3 seconds
6. Moves to `x = 5` (Boarding)
7. Exits at `x = 8`

---

### 7. Deliverables

| Deliverable          | Description                                          |
| -------------------- | ---------------------------------------------------- |
| **Three.js Scene**   | Fully functional scene with static layout and labels |
| **Animation System** | Script for moving patients along the path            |
| **Documentation**    | Setup guide and parameter definitions                |
| **JSFiddle Demo**    | Online preview of implementation                     |

---

## 🧑‍💻 Developer Implementation Guide

### File Structure

```
project/
│
├── index.html
├── /js
│   ├── main.js
│   ├── scene.js
│   ├── animation.js
│   └── utils.js
└── /assets
    └── font/
        └── helvetiker_regular.typeface.json
```

### Development Steps

1. **Set up Three.js environment**
   Import via ES6 import map from unpkg.
2. **Create scene, camera, and renderer**
   Initialize with dark gray background and 60° FOV.
3. **Add walls and zones**
   Use simple BoxGeometry for partitions, PlaneGeometry for floors.
4. **Add beds and people**
   Use Groups for movable elements.
5. **Load font and create labels**
   Use `FontLoader` and `TextGeometry`.
6. **Animate patient flow**
   Use GSAP timelines or position interpolation.
7. **Add “TIME” bar animation**
   A simple flat mesh that scales over time.
8. **Enable OrbitControls**
   Allow users to view from different angles.
9. **Test and optimize**
   Check performance and spacing.

---

### Future Enhancements

* **Dynamic data input** (JSON of patient queue)
* **Heatmap of congestion**
* **Tooltips or popups per patient**
* **Day/night lighting toggle**

