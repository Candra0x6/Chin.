# 3D Model Import Guide - Sketchfab to Three.js

## Step 1: Download Model from Sketchfab

### File Formats Supported by Three.js:
- **glTF (.glb, .gltf)** ⭐ **RECOMMENDED** - Best format, includes geometry, materials, textures, animations
- **OBJ (.obj)** - Basic geometry format, requires separate .mtl file for materials
- **FBX (.fbx)** - Complex format, needs special loader
- **USDZ (.usdz)** - Apple format, limited support

### How to Download from Sketchfab:
1. Go to Sketchfab.com and find your model
2. Click **Download** button (⬇️)
3. Select **Downloadable** format (usually **glTF** - recommended)
4. Choose format: **glTF** (.glb or .gltf) is best for Three.js
5. Download the file

---

## Step 2: Place Model Files in Project

Create a folder for models:
```
web/public/models/
├── beds/
│   ├── hospital-bed.glb
│   └── hospital-bed.gltf (with .bin and textures)
├── patients/
│   ├── patient-figure.glb
│   └── patient-textures/ (if needed)
└── staff/
    ├── doctor.glb
    ├── nurse.glb
    └── staff-textures/ (if needed)
```

---

## Step 3: Install GLTFLoader

The GLTFLoader is already available in Three.js examples. No additional npm install needed!

```typescript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
```

---

## Step 4: Loading Models (Code Examples)

### Example 1: Basic GLB File Loading

```typescript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();

function loadBedModel(): Promise<THREE.Group> {
  return new Promise((resolve, reject) => {
    loader.load(
      '/models/beds/hospital-bed.glb',
      (gltf) => {
        const model = gltf.scene;
        model.name = 'HospitalBed';
        
        // Enable shadows
        model.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        
        resolve(model);
      },
      (progress) => {
        console.log(`Loading bed: ${(progress.loaded / progress.total * 100).toFixed(0)}%`);
      },
      (error) => {
        console.error('Error loading bed model:', error);
        reject(error);
      }
    );
  });
}
```

### Example 2: Scale and Position Model

```typescript
async function createBedFromModel(position: THREE.Vector3): Promise<THREE.Group> {
  try {
    const bedModel = await loadBedModel();
    
    // Scale the model (adjust values as needed)
    bedModel.scale.set(1.5, 1.5, 1.5); // Scale 1.5x
    
    // Position the model
    bedModel.position.copy(position);
    
    // Rotate if needed (example: rotate 90 degrees around Y axis)
    // bedModel.rotation.y = Math.PI / 2;
    
    return bedModel;
  } catch (error) {
    console.error('Failed to create bed from model:', error);
    throw error;
  }
}
```

### Example 3: Load Multiple Models in Parallel

```typescript
async function loadAllModels() {
  try {
    const [bedModel, patientModel, staffModel] = await Promise.all([
      loadBedModel(),
      loadPatientModel(),
      loadStaffModel()
    ]);
    
    console.log('All models loaded successfully!');
    return { bedModel, patientModel, staffModel };
  } catch (error) {
    console.error('Error loading models:', error);
  }
}

function loadPatientModel(): Promise<THREE.Group> {
  return new Promise((resolve, reject) => {
    loader.load(
      '/models/patients/patient-figure.glb',
      (gltf) => {
        const model = gltf.scene;
        model.name = 'PatientFigure';
        model.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        resolve(model);
      },
      undefined,
      reject
    );
  });
}

function loadStaffModel(): Promise<THREE.Group> {
  return new Promise((resolve, reject) => {
    loader.load(
      '/models/staff/doctor.glb',
      (gltf) => {
        const model = gltf.scene;
        model.name = 'StaffFigure';
        model.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        resolve(model);
      },
      undefined,
      reject
    );
  });
}
```

### Example 4: Handling Model Animations (if model has animations)

```typescript
async function loadModelWithAnimation(modelPath: string): Promise<{ 
  model: THREE.Group; 
  animations: THREE.AnimationClip[] 
}> {
  return new Promise((resolve, reject) => {
    loader.load(
      modelPath,
      (gltf) => {
        const model = gltf.scene;
        const animations = gltf.animations;
        
        console.log(`Model has ${animations.length} animations`);
        
        // Setup mixer for animations if needed
        const mixer = new THREE.AnimationMixer(model);
        if (animations.length > 0) {
          const action = mixer.clipAction(animations[0]);
          action.play();
        }
        
        resolve({ model, animations });
      },
      undefined,
      reject
    );
  });
}
```

---

## Step 5: Material & Color Adjustment

### Change Model Color

```typescript
function changeBedColor(bedModel: THREE.Group, color: number) {
  bedModel.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      const material = child.material as THREE.MeshLambertMaterial;
      material.color.setHex(color);
    }
  });
}

// Usage:
// changeBedColor(bedModel, 0x88C999); // Change to green
```

### Apply Different Materials

```typescript
function applyMaterials(model: THREE.Group) {
  const material = new THREE.MeshStandardMaterial({
    color: 0x88C999,
    metalness: 0.3,
    roughness: 0.4,
  });
  
  model.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.material = material;
    }
  });
}
```

---

## Step 6: Integration with Existing Code

### Replace objectUtils.ts Functions

**Before (Geometric Shapes):**
```typescript
export function createBed(position: THREE.Vector3): THREE.Group {
  const bedGroup = new THREE.Group();
  const bedGeometry = new THREE.BoxGeometry(1.8, 0.3, 0.9);
  const bedMaterial = new THREE.MeshLambertMaterial({ color: 0x88C999 });
  // ... etc
}
```

**After (3D Model):**
```typescript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();

export async function createBed(position: THREE.Vector3): Promise<THREE.Group> {
  return new Promise((resolve, reject) => {
    loader.load(
      '/models/beds/hospital-bed.glb',
      (gltf) => {
        const bedModel = gltf.scene.clone();
        bedModel.position.copy(position);
        bedModel.scale.set(1, 1, 1);
        
        bedModel.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        
        resolve(bedModel);
      },
      undefined,
      reject
    );
  });
}
```

---

## Step 7: Common Issues & Solutions

### Issue 1: Model Appears Too Large/Small
**Solution:** Adjust scale
```typescript
bedModel.scale.set(0.5, 0.5, 0.5); // Make smaller
bedModel.scale.set(2, 2, 2);       // Make larger
```

### Issue 2: Model Texture Not Loading
**Solution:** Ensure textures are in the same folder or use texture loader
```typescript
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load('/models/beds/texture.png');
```

### Issue 3: Model Orientation Wrong
**Solution:** Rotate the model
```typescript
bedModel.rotation.x = Math.PI / 2;  // Rotate around X
bedModel.rotation.y = Math.PI / 2;  // Rotate around Y
bedModel.rotation.z = Math.PI / 2;  // Rotate around Z
```

### Issue 4: Model Loading Slow
**Solution:** Use .glb format (binary) instead of .gltf (text)
- .glb is compressed and loads faster
- .gltf with separate .bin file is good for large projects

### Issue 5: Models Not Casting Shadows
**Solution:** Enable shadows on all meshes
```typescript
model.traverse((child) => {
  if (child instanceof THREE.Mesh) {
    child.castShadow = true;
    child.receiveShadow = true;
  }
});
```

---

## File Format Comparison

| Format | File Size | Quality | Materials | Textures | Animations | Recommendation |
|--------|-----------|---------|-----------|----------|------------|-----------------|
| **glTF (.glb)** | 📦 Small | ⭐⭐⭐⭐⭐ | ✅ Yes | ✅ Yes | ✅ Yes | **BEST** |
| **glTF (.gltf)** | 📄 Medium | ⭐⭐⭐⭐⭐ | ✅ Yes | ✅ Yes | ✅ Yes | Good |
| **OBJ** | 📄 Large | ⭐⭐⭐ | ⚠️ Partial | ❌ No | ❌ No | Basic |
| **FBX** | 📦 Medium | ⭐⭐⭐⭐ | ✅ Yes | ✅ Yes | ✅ Yes | Complex |

---

## Recommended Sketchfab Models to Look For

### Hospital Beds:
- Search: "hospital bed", "medical bed", "patient bed"
- Filter: Free, Downloadable

### Patient Figures (Rigged):
- Search: "human character", "patient character", "medical staff"
- Filter: Free, Downloadable, Rigged (if you want animations)

### Doctor/Nurse Characters:
- Search: "doctor", "nurse", "medical staff character"
- Filter: Free, Downloadable

### Medical Equipment:
- Search: "medical equipment", "hospital furniture"
- Filter: Free, Downloadable

---

## Quick Start Implementation

Replace content in `web/app/lib/objectUtils.ts`:

```typescript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { COLORS } from './environmentUtils';

const loader = new GLTFLoader();

// Load models asynchronously
export async function createBedFromModel(position: THREE.Vector3): Promise<THREE.Group> {
  return new Promise((resolve, reject) => {
    loader.load(
      '/models/beds/hospital-bed.glb',
      (gltf) => {
        const bed = gltf.scene.clone();
        bed.position.copy(position);
        bed.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        resolve(bed);
      },
      undefined,
      reject
    );
  });
}

// Keep other functions similar with model loading...
```

---

## Next Steps

1. ✅ Find models on Sketchfab
2. ✅ Download as .glb format
3. ✅ Place in `/public/models/` folder
4. ✅ Update `objectUtils.ts` to use GLTFLoader
5. ✅ Test and adjust scaling/positioning
6. ✅ Fine-tune materials and colors if needed

