

## 🧩 Animation System Specification  
### (Extension of PRD — FR2 & FR3)

---

### 1. Purpose
The animation system visually demonstrates how **patients progress through the emergency department** — from **Entrance → Triage → Treatment → Boarding → Exit** — over a set duration.  

Each patient moves along a fixed path, pauses at key zones, and exits the scene in a looped cycle.  
The animation timeline also drives a horizontal **“TIME” progress bar** to indicate elapsed time.

---

### 2. Key Requirements

| ID | Requirement | Description |
|----|--------------|-------------|
| AN1 | Patients follow a continuous path | Each figure moves along the X-axis from left to right through defined waypoints |
| AN2 | Movement includes pauses | At Triage, Treatment, and Boarding, patients pause for a short delay to simulate waiting |
| AN3 | Multiple patients run asynchronously | Several figures can be in different parts of the flow simultaneously |
| AN4 | “TIME” bar animates in sync | The horizontal bar fills over the full cycle duration |
| AN5 | Looping animation | Once a patient reaches Exit, they return to Entrance and repeat |

---

### 3. Animation Model

**Zones & Waypoints**
```
Entrance:  x = -8
Triage:    x = -4
Treatment: x =  0
Boarding:  x =  5
Exit:      x =  8
```

**Timing Parameters (in seconds):**

| Segment | Duration | Pause | Notes |
|----------|-----------|--------|------|
| Entrance → Triage | 2 | 1 | Arrival |
| Triage → Treatment | 2 | 2 | Assessment time |
| Treatment → Boarding | 3 | 1 | Medical procedure |
| Boarding → Exit | 2 | 0 | Discharge |

**Full Cycle Duration:** ~13 seconds per patient

---

### 4. System Design

**Components**
| Component | Description |
|------------|--------------|
| `PatientController` | Controls a single patient’s movement and timing |
| `FlowManager` | Manages all patients and synchronizes their animation cycles |
| `TimeBar` | Mesh that visually represents simulation time progression |

---

### 5. Example Implementation (with GSAP)

You can see this version live here:  
👉 [JSFiddle Example with Animation](https://jsfiddle.net/3jsmentor/p4k05wts/)  

```html
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.164.1/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.164.1/examples/jsm/",
    "gsap": "https://cdn.skypack.dev/gsap@3.12.5"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { gsap } from 'gsap';

// --- Scene setup ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x202020);
const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 100);
camera.position.set(8, 8, 12);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lights
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 10, 5);
scene.add(dirLight);

// Floor
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 12),
  new THREE.MeshStandardMaterial({ color: 0x303030 })
);
floor.rotation.x = -Math.PI / 2;
scene.add(floor);

// --- Helpers ---
function createPerson(color = 0xffffff) {
  const group = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.CapsuleGeometry(0.25, 0.7, 4, 8),
    new THREE.MeshStandardMaterial({ color })
  );
  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.2),
    new THREE.MeshStandardMaterial({ color: 0xffe0bd })
  );
  head.position.y = 0.7;
  group.add(body, head);
  return group;
}

// --- Create Patients ---
const patients = [];
for (let i = 0; i < 4; i++) {
  const p = createPerson(0xffffff);
  p.position.set(-8 - i * 2, 0, (Math.random() - 0.5) * 4);
  scene.add(p);
  patients.push(p);
}

// --- Time Bar ---
const timeBar = new THREE.Mesh(
  new THREE.BoxGeometry(0.1, 0.2, 4),
  new THREE.MeshStandardMaterial({ color: 0x3399ff })
);
timeBar.position.set(0, 0.1, 5.5);
scene.add(timeBar);

// --- Animation System ---
const waypoints = [-8, -4, 0, 5, 8];
const pauses = [1, 2, 1, 0];
const durations = [2, 2, 3, 2];

function animatePatient(patient, offset = 0) {
  const timeline = gsap.timeline({ repeat: -1, repeatDelay: 1, delay: offset });
  waypoints.forEach((x, i) => {
    if (i < waypoints.length - 1) {
      timeline.to(patient.position, {
        x: waypoints[i + 1],
        duration: durations[i],
        ease: "power1.inOut",
      });
      timeline.to({}, { duration: pauses[i] }); // pause
    }
  });
}

patients.forEach((p, i) => animatePatient(p, i * 2)); // stagger start times

// --- Animate Time Bar ---
gsap.to(timeBar.scale, {
  x: 20,
  duration: 13,
  ease: "none",
  repeat: -1,
  yoyo: true
});

// --- Labels ---
const loader = new FontLoader();
loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', font => {
  const zones = ['ENTRANCE', 'TRIAGE', 'TREATMENT', 'BOARDING', 'EXIT'];
  const positions = [-8, -4, 0, 5, 8];
  zones.forEach((label, i) => {
    const geo = new TextGeometry(label, { font, size: 0.5, height: 0.05 });
    const mat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.set(positions[i] - 1.5, 0.01, 5);
    scene.add(mesh);
  });
});

// --- Render loop ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
</script>
```

---

### 6. Developer Notes

- The GSAP timelines keep all patients looping independently.  
- Each patient has randomized `z` offsets for a more natural, non-uniform look.  
- Add easing for smoother acceleration and deceleration at each zone.  
- You can expand the `FlowManager` to dynamically add/remove patients or adjust timings from JSON input.

---

### 7. Testing Scenarios

| Test | Expected Behavior |
|------|--------------------|
| Patient enters | Smooth movement from left to first zone |
| Pause at each zone | Visible stop before moving again |
| Time bar | Expands linearly with cycle duration |
| Multiple patients | Movements overlap naturally |
| Loop | After Exit, patient reappears at Entrance |

---

### 8. Possible Enhancements
- Add “queue” behavior — if too many patients in one zone, delay movement.
- Add small camera dolly animation synced to time bar.
- Visualize bed occupancy (change bed color when occupied).
- Integrate real hospital timing data via JSON.
