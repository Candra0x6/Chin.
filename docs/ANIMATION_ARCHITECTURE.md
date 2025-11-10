# Animation System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ThreeScene Component                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. Scene Initialization                                │    │
│  │     - Create scene, camera, renderer                    │    │
│  │     - Setup lighting, environment                       │    │
│  │     - Create objects (beds, patients, staff)            │    │
│  └────────────────────────────────────────────────────────┘    │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  2. Animation Setup                                     │    │
│  │     - Extract patient meshes from scene                 │    │
│  │     - createPatientAnimations(meshes, 1.0)             │    │
│  │     - Initialize THREE.Clock                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  3. Animation Loop (60 FPS)                            │    │
│  │     - deltaTime = clock.getDelta()                      │    │
│  │     - updateAllPatientAnimations(anims, deltaTime)     │    │
│  │     - renderer.render(scene, camera)                    │    │
│  │     - requestAnimationFrame(animate)                    │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    animationUtils Module                         │
│                                                                   │
│  updateAllPatientAnimations(animations, deltaTime)               │
│    │                                                             │
│    └──► For each patient:                                       │
│          updatePatientAnimation(patient, deltaTime)             │
│            │                                                     │
│            ├──► If Moving:                                      │
│            │      • Calculate progress                          │
│            │      • Apply easing (ease-in-out cubic)           │
│            │      • Interpolate position                        │
│            │      • Check if arrived                            │
│            │                                                     │
│            └──► If Waiting:                                     │
│                  • Increment wait timer                         │
│                  • Check if wait complete                       │
│                  • If complete: transitionToNextState()        │
│                                                                   │
│  transitionToNextState(patient)                                  │
│    │                                                             │
│    ├──► Get next state in flow                                 │
│    ├──► Get target zone position                               │
│    ├──► Add random offset (±0.75 units)                        │
│    ├──► Set target position                                     │
│    ├──► Start movement                                          │
│    └──► Reset timers                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Patient State Flow

```
                    ┌─────────────┐
                    │  ENTERING   │
                    │  (Entrance) │
                    │   Wait: 0s  │
                    └──────┬──────┘
                           │
                     Move (smooth)
                           │
                           ▼
                    ┌─────────────┐
                    │  TRIAGING   │
                    │  (Triage)   │
                    │   Wait: 3s  │
                    └──────┬──────┘
                           │
                     Move (smooth)
                           │
                           ▼
                    ┌─────────────┐
                    │  TREATING   │
                    │ (Treatment) │
                    │   Wait: 5s  │
                    └──────┬──────┘
                           │
                     Move (smooth)
                           │
                           ▼
                    ┌─────────────┐
                    │  BOARDING   │
                    │ (Boarding)  │
                    │   Wait: 2s  │
                    └──────┬──────┘
                           │
                     Move (smooth)
                           │
                           ▼
                    ┌─────────────┐
                    │   EXITING   │
                    │   (Exit)    │
                    │   Wait: 0s  │
                    └──────┬──────┘
                           │
                      Loop back
                           │
                           └──────────┐
                                      │
                           ┌──────────┘
                           ▼
                    Back to ENTERING
```

## Animation Data Structure

```
PatientAnimation {
  mesh: THREE.Group ───────────────► The patient figure in the scene
  state: PatientState ─────────────► Current state (TRIAGING, etc.)
  targetPosition: Vector3 ─────────► Where patient is moving to
  startPosition: Vector3 ──────────► Where movement started from
  moveProgress: number ────────────► 0.0 to 1.0 (interpolation)
  waitTimer: number ───────────────► Time spent waiting (seconds)
  isMoving: boolean ───────────────► true=moving, false=waiting
  totalCycleTime: number ──────────► Total time in animation
}
```

## Movement Timeline Example

```
Patient #1 Timeline:
0s  ───[E]───► Start at Entrance (ENTERING)
0s  ───────────► Move to Triage (2s travel)
2s  ───[T]───► Arrive at Triage (TRIAGING)
2-5s ──────────► Wait 3 seconds
5s  ───────────► Move to Treatment (2s travel)
7s  ───[Tr]──► Arrive at Treatment (TREATING)
7-12s ─────────► Wait 5 seconds
12s ───────────► Move to Boarding (2s travel)
14s ───[B]───► Arrive at Boarding (BOARDING)
14-16s ────────► Wait 2 seconds
16s ───────────► Move to Exit (2s travel)
18s ───[Ex]──► Arrive at Exit (EXITING)
18s ───────────► Move to Entrance (loop)
20s ───[E]───► Back at Entrance (cycle repeats)

Patient #2 Timeline (1s stagger):
1s  ───[E]───► Start at Entrance
... (same as Patient #1 but offset by 1s)

Patient #3 Timeline (2s stagger):
2s  ───[E]───► Start at Entrance
... (same as Patient #1 but offset by 2s)
```

## Easing Function Visualization

```
Ease-in-out Cubic:

Position
    1.0 │                    ┌─────────
        │                  ╱
        │                ╱
    0.5 │              ╱
        │            ╱
        │          ╱
    0.0 │────────╱
        └──────────────────────────► Time
        0.0    0.5    1.0

Formula:
  t < 0.5 → 4t³
  t ≥ 0.5 → 1 - (-2t + 2)³ / 2

Properties:
  • Slow start (ease in)
  • Fast middle
  • Slow end (ease out)
  • Smooth acceleration/deceleration
```

## Position Calculation

```
Each Frame:

1. Get delta time
   ┌────────────────────────────────┐
   │ deltaTime = clock.getDelta()   │
   │ (e.g., 0.016s for 60 FPS)     │
   └────────────────────────────────┘

2. Calculate movement progress
   ┌────────────────────────────────┐
   │ distance = start → target      │
   │ duration = distance / speed    │
   │ progress += deltaTime / duration│
   └────────────────────────────────┘

3. Apply easing
   ┌────────────────────────────────┐
   │ easedProgress = easeInOut(     │
   │   progress                     │
   │ )                              │
   └────────────────────────────────┘

4. Interpolate position
   ┌────────────────────────────────┐
   │ newPos = lerp(                 │
   │   start,                       │
   │   target,                      │
   │   easedProgress                │
   │ )                              │
   └────────────────────────────────┘

5. Update mesh
   ┌────────────────────────────────┐
   │ mesh.position.copy(newPos)     │
   └────────────────────────────────┘
```

## Stagger Pattern

```
Time →
0s   1s   2s   3s   4s   5s   6s   7s   8s   9s   10s

P1:  [E]──────►[T]──wait──►[Tr]──wait──►[B]──►[Ex]──►
P2:       [E]──────►[T]──wait──►[Tr]──wait──►[B]──►[Ex]
P3:            [E]──────►[T]──wait──►[Tr]──wait──►[B]
P4:                 [E]──────►[T]──wait──►[Tr]──wait
P5:                      [E]──────►[T]──wait──►[Tr]

Legend:
[E]   = Entrance
[T]   = Triage
[Tr]  = Treatment
[B]   = Boarding
[Ex]  = Exit
──►   = Moving
wait  = Waiting at zone
```

## Zone Layout (Top View)

```
                 EMERGENCY DEPARTMENT
     ╔════════════════════════════════════════╗
     ║  WALL (light gray #B0B0B0)            ║
     ╠════════════════════════════════════════╣
     ║    │    │         │         │    │    ║
     ║ E  │ T  │    Tr   │    B    │ Ex │    ║
     ║ N  │ R  │    E    │    O    │ I  │    ║
     ║ T  │ I  │    A    │    A    │ T  │    ║
     ║ R  │ A  │    T    │    R    │    │    ║
     ║ A  │ G  │    M    │    D    │    │    ║
     ║ N  │ E  │    E    │    I    │    │    ║
     ║ C  │    │    N    │    N    │    │    ║
     ║ E  │    │    T    │    G    │    │    ║
     ║    │    │         │         │    │    ║
     ╠════════════════════════════════════════╣
     ║  WALL                                  ║
     ╚════════════════════════════════════════╝

X-axis zones:
-8 to -6: Entrance
-6 to -2: Triage (red overlay #882222)
-2 to +2: Treatment (beds here)
+2 to +6: Boarding (beds here)
+6 to +8: Exit

Patient movement: Left → Right → Loop back to Left
```

## Code Flow Diagram

```
ThreeScene.tsx
    │
    ├──► useEffect (mount)
    │      │
    │      ├──► Create scene objects
    │      │      │
    │      │      └──► createAllSceneObjects()
    │      │              │
    │      │              └──► Returns Group with:
    │      │                     - Beds (green)
    │      │                     - Patients (white)
    │      │                     - Staff (blue)
    │      │
    │      ├──► Extract patient meshes
    │      │      │
    │      │      └──► Filter white meshes
    │      │
    │      ├──► Initialize animations
    │      │      │
    │      │      └──► createPatientAnimations(meshes, 1.0)
    │      │              │
    │      │              └──► Returns PatientAnimation[]
    │      │
    │      └──► Start animation loop
    │             │
    │             └──► animate()
    │                     │
    │                     ├──► getDelta()
    │                     ├──► updateAllPatientAnimations()
    │                     ├──► render()
    │                     └──► requestAnimationFrame(animate)
    │
    └──► useEffect cleanup
           │
           └──► Stop clock, dispose resources

animationUtils.ts
    │
    ├──► createPatientAnimations()
    │      │
    │      └──► For each mesh:
    │             createPatientAnimation(mesh, i * stagger)
    │
    ├──► updateAllPatientAnimations()
    │      │
    │      └──► For each patient:
    │             updatePatientAnimation(patient, deltaTime)
    │
    └──► updatePatientAnimation()
           │
           ├──► If moving:
           │      ├──► Calculate progress
           │      ├──► Apply easing
           │      ├──► Interpolate position
           │      └──► Check arrival
           │
           └──► If waiting:
                  ├──► Increment timer
                  └──► Check wait complete
                        │
                        └──► transitionToNextState()
```

## Performance Optimization

```
Frame Budget (60 FPS = 16.67ms per frame)

┌──────────────────────────────────────────┐
│  1. Input Processing       : ~0.1ms      │
│  2. Animation Updates       : ~0.5ms     │ ← Our code
│  3. Physics (none)          : 0ms        │
│  4. Rendering              : ~10ms       │
│  5. Other overhead         : ~2ms        │
│  ───────────────────────────────────     │
│  Total                     : ~12.6ms     │
│  Headroom                  : ~4ms        │
└──────────────────────────────────────────┘

Optimization strategies used:
✓ Reuse Vector3 objects
✓ Minimal branching
✓ Simple state machine
✓ No complex physics
✓ Efficient interpolation
✓ Delta-time based (not frame-based)
```

## Future Integration Points

```
Phase 8 (Time Bar):
  • Can read patient.totalCycleTime
  • Can use getAnimationStats() for progress
  • Can sync with state transitions

Phase 9 (Interactivity):
  • Can pause/resume animations
  • Can add click handlers to patient meshes
  • Can display patient.state on hover

Phase 10 (Testing):
  • Can monitor FPS with animation load
  • Can stress-test with 50+ patients
  • Can validate state transitions
```

---

**Legend:**
- `[X]` = Zone/State
- `──►` = Movement/Flow
- `│` = Connection
- `┌─┐` = Container/Box
- `╔═╗` = Structure/Wall
