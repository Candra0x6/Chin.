# Animation System Implementation

Implementation of the patient flow animation system that visually demonstrates how patients progress through the emergency department (Entrance → Triage → Treatment → Boarding → Exit).

## Completed Tasks

- [x] Review AnimationPRD.md specification
- [x] Create task list structure

## In Progress Tasks

- [ ] Set up animation dependencies (GSAP)
- [ ] Create PatientController component
- [ ] Implement FlowManager component
- [ ] Create TimeBar visualization component

## Future Tasks

### Core Animation System (AN1-AN5)

- [ ] **AN1: Patient Path System**
  - [ ] Define waypoint coordinates for all zones
  - [ ] Implement continuous path movement along X-axis
  - [ ] Add smooth transitions between waypoints

- [ ] **AN2: Pause Mechanism**
  - [ ] Implement pause logic at Triage (1 second)
  - [ ] Implement pause logic at Treatment (2 seconds)
  - [ ] Implement pause logic at Boarding (1 second)
  - [ ] Add visual indicators for paused patients

- [ ] **AN3: Multi-Patient Support**
  - [ ] Create patient spawning system
  - [ ] Implement asynchronous patient animations
  - [ ] Add staggered start times for patients
  - [ ] Support multiple patients in different zones simultaneously

- [ ] **AN4: Time Bar Synchronization**
  - [ ] Create horizontal TIME progress bar mesh
  - [ ] Sync time bar with full cycle duration (13 seconds)
  - [ ] Implement smooth bar fill animation
  - [ ] Add time bar visual styling

- [ ] **AN5: Looping Animation**
  - [ ] Implement patient return to Entrance after Exit
  - [ ] Set up infinite loop with GSAP timeline
  - [ ] Add repeat delay configuration
  - [ ] Test continuous looping behavior

### Visual Enhancements

- [ ] Create patient 3D models (capsule body + sphere head)
- [ ] Add color variations for different patient types
- [ ] Implement zone labels (ENTRANCE, TRIAGE, TREATMENT, BOARDING, EXIT)
- [ ] Add easing functions for natural movement
- [ ] Implement randomized Z-axis offsets for natural spacing

### Integration & Testing

- [ ] Integrate animation system with existing 3D scene
- [ ] Add animation controls (play/pause/reset)
- [ ] Test all animation scenarios from PRD section 7
- [ ] Performance optimization for multiple patients
- [ ] Add error handling and edge cases

### Optional Enhancements

- [ ] Queue behavior when zones are crowded
- [ ] Camera dolly animation synced to time bar
- [ ] Bed occupancy visualization (color changes)
- [ ] JSON configuration for timing parameters
- [ ] Real hospital data integration

## Implementation Plan

### Architecture Overview

The animation system consists of three main components:

1. **PatientController**: Controls individual patient movement and timing
   - Manages single patient's animation timeline
   - Handles waypoint transitions
   - Controls pause durations at each zone

2. **FlowManager**: Orchestrates all patient animations
   - Spawns and manages multiple patients
   - Synchronizes animation cycles
   - Handles patient lifecycle (entrance to exit)

3. **TimeBar**: Visual progress indicator
   - Represents simulation time progression
   - Syncs with full cycle duration
   - Provides visual feedback to users

### Zone Configuration

```
Entrance:  x = -8
Triage:    x = -4
Treatment: x =  0
Boarding:  x =  5
Exit:      x =  8
```

### Timing Parameters

| Segment | Duration | Pause | Total |
|---------|----------|-------|-------|
| Entrance → Triage | 2s | 1s | 3s |
| Triage → Treatment | 2s | 2s | 4s |
| Treatment → Boarding | 3s | 1s | 4s |
| Boarding → Exit | 2s | 0s | 2s |
| **Full Cycle** | **9s** | **4s** | **13s** |

### Technology Stack

- **Three.js**: 3D scene rendering and patient models
- **GSAP**: Animation timeline and easing
- **Next.js/React**: Component structure and UI integration
- **TypeScript**: Type safety for animation parameters

### Data Flow

```
User Initiates Animation
    ↓
FlowManager spawns patients with staggered delays
    ↓
PatientController manages individual timelines
    ↓
GSAP animates position along waypoints
    ↓
Pauses executed at designated zones
    ↓
TimeBar scales in sync with cycle duration
    ↓
Patient reaches Exit → Returns to Entrance
    ↓
Loop continues indefinitely
```

## Relevant Files

### To Be Created

- `web/app/components/animation/PatientController.tsx` - Individual patient animation logic
- `web/app/components/animation/FlowManager.tsx` - Multi-patient orchestration
- `web/app/components/animation/TimeBar.tsx` - Progress bar visualization
- `web/app/components/animation/types.ts` - Animation type definitions
- `web/app/components/animation/constants.ts` - Waypoints and timing configuration
- `web/app/hooks/usePatientAnimation.ts` - React hook for animation control

### To Be Modified

- `web/app/components/Scene3D.tsx` - Integration of animation system
- `web/package.json` - Add GSAP dependency
- `web/app/page.tsx` - Add animation controls UI

## Testing Scenarios

| Test ID | Scenario | Expected Behavior |
|---------|----------|-------------------|
| T1 | Patient enters scene | Smooth movement from Entrance (x=-8) to Triage |
| T2 | Pause at Triage | Patient stops for 1 second before moving |
| T3 | Pause at Treatment | Patient stops for 2 seconds before moving |
| T4 | Pause at Boarding | Patient stops for 1 second before moving |
| T5 | Time bar progression | Bar expands linearly over 13 seconds |
| T6 | Multiple patients | 4 patients move independently without collision |
| T7 | Loop completion | Patient reappears at Entrance after reaching Exit |
| T8 | Continuous operation | Animation runs smoothly for 5+ minutes |
| T9 | Staggered starts | Patients begin with 2-second delays |
| T10 | Visual accuracy | Zone labels appear at correct positions |

## Implementation Notes

- Use `gsap.timeline()` for sequential waypoint animation
- Apply `power1.inOut` easing for smooth acceleration/deceleration
- Implement `repeat: -1` for infinite looping
- Add `repeatDelay: 1` for brief pause between cycles
- Randomize Z-axis positions between -2 and 2 for natural spacing
- Use GSAP's `stagger` feature for patient spawning delays
- Store animation references for cleanup on component unmount

## Success Criteria

- ✅ All 5 animation requirements (AN1-AN5) implemented
- ✅ Patients move smoothly through all waypoints
- ✅ Pauses occur at correct zones with accurate durations
- ✅ Multiple patients animate independently
- ✅ Time bar syncs with full 13-second cycle
- ✅ Animation loops continuously without errors
- ✅ All 10 testing scenarios pass
- ✅ Performance maintained with 4+ simultaneous patients
- ✅ Code is type-safe and well-documented
