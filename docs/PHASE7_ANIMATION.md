# Phase 7: Animation System Implementation

## Overview
Phase 7 implements a complete patient flow animation system that moves patient figures through all emergency department zones with realistic waiting periods and smooth transitions.

## Implementation Date
November 10, 2025

## Features Implemented

### 1. Patient State Machine
A comprehensive state machine manages patient flow through the ED:

```
ENTERING → TRIAGING (3s wait) → TREATING (5s wait) → BOARDING (2s wait) → EXITING → Loop
```

**States:**
- `ENTERING`: Patient enters through entrance zone
- `TRIAGING`: Patient waits at triage zone (3 seconds)
- `TREATING`: Patient receives treatment (5 seconds)
- `BOARDING`: Patient waits for discharge (2 seconds)
- `EXITING`: Patient leaves through exit zone
- `EXITED`: Transition state before loop restart

### 2. Movement System

**Smooth Interpolation:**
- Uses ease-in-out cubic easing for natural-looking movement
- Delta-time based animation for consistent speed across different frame rates
- Position interpolation using THREE.js `lerpVectors()`

**Movement Parameters:**
- Speed: 2 units per second
- Random position offsets: ±0.75 units (prevents patient overlap)
- Height: Fixed at Y=0.9 (standing position)

**Easing Function:**
```typescript
easeInOutCubic(t) = t < 0.5 
  ? 4 * t³ 
  : 1 - (-2t + 2)³ / 2
```

### 3. Waiting Periods

Zone-specific waiting times simulate realistic ED workflow:

| Zone | Wait Time |
|------|-----------|
| Entrance | 0 seconds |
| Triage | 3 seconds |
| Treatment | 5 seconds |
| Boarding | 2 seconds |
| Exit | 0 seconds |

### 4. Staggered Animation Start

- Each patient starts with a delay
- Default stagger: 1 second between patients
- Creates natural flow without overcrowding
- Prevents all patients moving in sync

### 5. Continuous Loop Animation

- Patients automatically loop through the entire flow
- Seamless transition from exit back to entrance
- Infinite animation cycle

## File Structure

### New Files Created

#### `web/app/lib/animationUtils.ts`
Core animation system with the following exports:

**Enums:**
- `PatientState`: All possible patient states

**Interfaces:**
- `PatientAnimation`: Complete animation state for one patient

**Constants:**
- `STATE_TO_ZONE`: Maps states to zone names
- `WAIT_PERIODS`: Waiting time for each state
- `MOVEMENT_SPEED`: Movement speed constant

**Functions:**
- `createPatientAnimation()`: Initialize animation for one patient
- `createPatientAnimations()`: Initialize multiple patients with stagger
- `updatePatientAnimation()`: Update one patient per frame
- `updateAllPatientAnimations()`: Update all patients per frame
- `getAnimationStats()`: Get current state distribution (debugging)

### Modified Files

#### `web/app/components/ThreeScene.tsx`
**Changes:**
1. Import animation utilities
2. Add refs for patient animations and clock
3. Extract patient meshes from scene objects
4. Initialize patient animations with staggered start
5. Update animation loop to include delta time and animation updates

**Key Integration Points:**
```typescript
// Refs
const patientAnimationsRef = useRef<PatientAnimation[]>([]);
const clockRef = useRef<THREE.Clock>(new THREE.Clock());

// Initialization
patientAnimationsRef.current = createPatientAnimations(patientMeshes, 1.0);
clockRef.current.start();

// Animation Loop
const deltaTime = clockRef.current.getDelta();
updateAllPatientAnimations(patientAnimationsRef.current, deltaTime);
```

## Technical Details

### Patient Detection Logic
Patients are identified from the scene by:
1. Traversing all scene objects
2. Finding `THREE.Group` objects with 2+ children
3. Checking if first child has white material (#FFFFFF)
4. White color indicates patient figure (vs green beds or blue staff)

### Animation Update Flow

```
Each Frame:
  1. Get delta time from THREE.Clock
  2. For each patient:
     a. If moving: interpolate position toward target
     b. If waiting: increment wait timer
     c. If wait complete: transition to next state
  3. Render scene
```

### Performance Considerations

**Optimizations:**
- Delta-time based updates (frame-rate independent)
- Simple linear interpolation with easing
- No complex physics calculations
- Efficient state machine with minimal branching
- Reuses THREE.Vector3 objects where possible

**Memory Usage:**
- Each patient: ~500 bytes of animation state
- 10 patients: ~5 KB total
- Negligible overhead for 3D scene

## Testing & Verification

### Visual Checks
- [x] Patients start at entrance zone
- [x] Smooth movement between zones
- [x] No jittery or stuttering motion
- [x] Patients wait at appropriate zones
- [x] Continuous loop without gaps
- [x] Staggered start creates natural flow

### Performance Checks
- [x] Consistent 60 FPS on modern hardware
- [x] No memory leaks over extended runtime
- [x] Animation speed consistent across frame rates

## Usage Example

```typescript
// Extract patient meshes from scene
const patientMeshes: THREE.Group[] = [];
scene.traverse((child) => {
  if (isPatientFigure(child)) {
    patientMeshes.push(child);
  }
});

// Initialize animations with 1-second stagger
const animations = createPatientAnimations(patientMeshes, 1.0);

// In animation loop
const clock = new THREE.Clock();
function animate() {
  const deltaTime = clock.getDelta();
  updateAllPatientAnimations(animations, deltaTime);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Configuration Options

### Adjustable Parameters

**In `animationUtils.ts`:**
```typescript
// Movement speed (units per second)
export const MOVEMENT_SPEED = 2;

// Waiting periods (seconds)
export const WAIT_PERIODS = {
  TRIAGING: 3,
  TREATING: 5,
  BOARDING: 2,
  // ...
};
```

**In `ThreeScene.tsx`:**
```typescript
// Stagger delay between patients (seconds)
createPatientAnimations(patientMeshes, 1.0);
```

**Position Randomization:**
```typescript
// In transitionToNextState()
const randomOffsetX = (Math.random() - 0.5) * 1.5; // ±0.75 units
const randomOffsetZ = (Math.random() - 0.5) * 1.5;
```

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

Requires:
- WebGL support
- `requestAnimationFrame` API
- ES6+ JavaScript features

## Future Enhancements

Potential improvements for later phases:
- [ ] Variable patient speeds based on urgency
- [ ] Patient ID labels (name tags)
- [ ] Color-coded urgency levels
- [ ] Click patient to view details
- [ ] Path visualization (trails)
- [ ] Animation pause/play controls
- [ ] Speed controls (1x, 2x, 4x)
- [ ] Bed assignment logic
- [ ] Staff interaction animations

## Troubleshooting

### Issue: Patients not moving
**Solution:** Check that patient meshes were correctly identified and extracted from scene

### Issue: Jerky movement
**Solution:** Verify delta time is being calculated correctly with THREE.Clock

### Issue: Patients overlap
**Solution:** Increase random offset range in `transitionToNextState()`

### Issue: Wrong waiting times
**Solution:** Check WAIT_PERIODS configuration in animationUtils.ts

## Code Quality

- ✅ TypeScript strict mode enabled
- ✅ Comprehensive JSDoc comments
- ✅ Type-safe interfaces and enums
- ✅ No linting errors
- ✅ Modular architecture
- ✅ Follows React best practices

## Integration Checklist

- [x] Import animation utilities in ThreeScene
- [x] Add animation refs (patientAnimationsRef, clockRef)
- [x] Extract patient meshes from scene
- [x] Initialize animations with stagger
- [x] Update animation loop with delta time
- [x] Update all patient animations each frame
- [x] Verify no TypeScript errors
- [x] Test visual appearance
- [x] Update documentation

## Next Steps

Proceed to **Phase 8: Time Bar** which will:
- Create visual time progress indicator
- Sync with animation cycle
- Display total elapsed time
- Provide visual feedback of flow progress
