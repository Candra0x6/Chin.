# OrbitControls Visual Guide

## Mouse Controls Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    3D Scene Canvas                          │
│                                                             │
│   ┌──────────────┐                                         │
│   │ LEFT BUTTON  │  Rotate Camera                          │
│   │ Click + Drag │  Orbit around scene center              │
│   └──────────────┘                                         │
│                                                             │
│   ┌──────────────┐                                         │
│   │ RIGHT BUTTON │  Pan Camera                             │
│   │ Click + Drag │  Move camera position in XZ plane       │
│   └──────────────┘                                         │
│                                                             │
│   ┌──────────────┐                                         │
│   │ MOUSE WHEEL  │  Zoom Camera                            │
│   │ Scroll Up/Dn │  Distance: 5-50 units                   │
│   └──────────────┘                                         │
│                                                             │
│   ┌──────────────┐                                         │
│   │ SHIFT + LEFT │  Alternative Pan                        │
│   │ Click + Drag │  Same as right-click                    │
│   └──────────────┘                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Touch Controls Diagram (Mobile/Tablet)

```
┌─────────────────────────────────────────────────────────────┐
│                  Touchscreen Canvas                         │
│                                                             │
│   ┌──────────────┐                                         │
│   │  ONE FINGER  │  Rotate                                 │
│   │    Touch +   │  Orbit around scene                     │
│   │     Drag     │                                         │
│   │      👆      │                                         │
│   └──────────────┘                                         │
│                                                             │
│   ┌──────────────┐                                         │
│   │ TWO FINGERS  │  Pan & Zoom                             │
│   │    Touch +   │  Drag to pan                            │
│   │     Drag     │  Pinch to zoom                          │
│   │    👆  👆    │                                         │
│   └──────────────┘                                         │
│                                                             │
│   ┌──────────────┐                                         │
│   │ PINCH ZOOM   │  Zoom In/Out                            │
│   │   👆    👆   │  Spread fingers: zoom in                │
│   │    👈👉     │  Pinch fingers: zoom out                │
│   └──────────────┘                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Camera Movement Diagram

### Rotation (Polar Angle - Vertical)

```
        Top View (0°)
             ↑
             │
        ┌────┴────┐
        │  Camera │
        │    ↓    │
        └─────────┘
             │
        Scene Below

        Isometric (45°)
             
        ┌─────────┐
        │  Camera │ ─────→
        └─────────┘
           ↙
        Scene

        Horizon (85°)
        
        Scene  ─────→  ┌─────────┐
        ────────────→  │  Camera │
                       └─────────┘
        
        ❌ Below Floor (90°+) - BLOCKED
```

### Rotation (Azimuth Angle - Horizontal)

```
                    North (0°)
                        ↑
                        │
                   ┌────┴────┐
                   │  Camera │
                   └─────────┘
                        │
West (-90°) ←───────────┼───────────→ East (90°)
                        │
                   ┌─────────┐
                   │  Scene  │
                   │ (0,0,0) │
                   └─────────┘
                        │
                   ┌────┴────┐
                   │  Camera │
                   └─────────┘
                        │
                        ↓
                   South (180°)

        360° Rotation Enabled ✅
```

### Zoom (Distance from Target)

```
    Close-Up (minDistance: 5 units)
    
    ┌─────────┐
    │  Camera │
    └────┬────┘
         │ 5 units
         ↓
    ┌─────────┐
    │  Scene  │  Detail View
    │  █████  │  Can see individual patients
    └─────────┘


    Medium (15-20 units)
    
         ┌─────────┐
         │  Camera │
         └────┬────┘
              │ 15-20 units
              ↓
         ┌─────────┐
         │  Scene  │  Balanced View
         │   ███   │  Can see 2-3 zones
         └─────────┘


    Wide (maxDistance: 50 units)
    
              ┌─────────┐
              │  Camera │
              └────┬────┘
                   │ 50 units
                   ↓
              ┌─────────┐
              │  Scene  │  Overview
              │    █    │  Full department
              └─────────┘
```

### Pan (Target Movement)

```
    Before Pan
    
    ┌─────────┐
    │  Camera │  ← Looking at
    └─────────┘     Scene Center
         ↓
    ┌─────────────────┐
    │  ★  │  │  │  │  │  Scene (★ = target)
    └─────────────────┘


    After Right-Click Drag →
    
         ┌─────────┐
         │  Camera │  ← Now looking at
         └─────────┘     different area
              ↓
    ┌─────────────────┐
    │  │  │  ★  │  │  │  Scene (★ = new target)
    └─────────────────┘
    
    Pan moves both camera AND target together
    maintaining same viewing angle
```

## Damping Visualization

```
    Without Damping (enableDamping: false)
    
    User stops dragging
            ↓
    Camera stops immediately
    ▓▓▓▓▓▓▓▓█ STOP
    
    Feels: Abrupt, mechanical


    With Damping (dampingFactor: 0.05)
    
    User stops dragging
            ↓
    Camera gradually decelerates
    ▓▓▓▓▓▓▓▓▒▒▒░░░ smooth stop
    
    Feels: Natural, professional
```

## Constraint Zones Diagram

```
    Allowed Camera Positions (Side View)
    
         ✅ Can orbit here (0-85°)
              ↗  ↑  ↖
            ↗    │    ↖
          ↗      │      ↖
        ↗        │        ↖
    ──────────────────────────── Horizon (90°)
    ═══════════════════════════ Floor (Y=0)
        ❌ Cannot orbit below floor
    
    
    Zoom Constraints (Top View)
    
              ┌─ Max Distance (50 units)
              │
              │    ┌─ Typical View (15-25)
              │    │
              │    │  ┌─ Close View (5-10)
              ↓    ↓  ↓
         ░░░░░▒▒▒▒▓▓▓▓▓█████ Scene
         ↑              ↑
         50 units       5 units
         
         ❌ Too far     ❌ Too close
```

## Common View Angles

### Top-Down View
```
         Camera
            ↓
        ┌───┴───┐
        │ Y+    │
        └───────┘
            │
            ↓
    ┌───────────────┐
    │  Scene (XZ)   │  Perfect for layout planning
    │  Z+ ↑         │  See all zones at once
    │     │         │  Clear flow paths
    │     └─→ X+    │
    └───────────────┘
    
    Position: (0, 25, 0)
    Target: (0, 0, 0)
    Polar Angle: ~0°
```

### Isometric View (Default)
```
              Camera
                ↙
            ┌─────┐
            │     │
            └─────┘
              ↙
    ┌───────────────┐
    │     Scene     │  Balanced 3D view
    │   ╱╲  ╱╲  ╱╲  │  Good depth perception
    │  ╱  ╲╱  ╲╱  ╲ │  Shows height and space
    └───────────────┘
    
    Position: (15, 10, 15)
    Target: (0, 0, 0)
    Polar Angle: ~45°
```

### Ground-Level View
```
    Camera ─────────────→
    ┌─────┐
    │     │══════════════▶
    └─────┘
                    ┌───────────┐
                    │  Scene    │  Patient perspective
                    │  ███ ███  │  Immersive view
                    │  ███ ███  │  Detail focused
                    └───────────┘
    
    Position: (25, 2, 0)
    Target: (0, 0, 0)
    Polar Angle: ~85°
```

## Zone Focus Examples

### Focus on Entrance Zone
```
    Camera Position: (-12, 8, 8)
    Target: (-7, 0, 0)
    
            Camera
              ↙
          ┌─────┐
          └─────┘
            ↙
    ┌─────────────────────────┐
    │ 🚪 ENTRANCE              │
    │ [Entrance Zone Focused]  │
    │  👤 👤                   │
    └─────────────────────────┘
```

### Focus on Treatment Zone
```
    Camera Position: (0, 6, 12)
    Target: (0, 0, 0)
    
               Camera
                 ↙
             ┌─────┐
             └─────┘
               ↙
    ┌─────────────────────────┐
    │    TREATMENT AREA        │
    │ [Treatment Zone Focused] │
    │  🛏️ 👤  🛏️ 👤  🛏️ 👤    │
    └─────────────────────────┘
```

## Movement Speed Indicators

### Rotation Speed (rotateSpeed: 1.0)

```
    Slow (0.5)      Normal (1.0)     Fast (2.0)
    
    ↺ ┄┄→           ↺ ──→            ↺ ══►
    Drag 10cm       Drag 10cm        Drag 10cm
    Rotate 30°      Rotate 60°       Rotate 120°
```

### Pan Speed (panSpeed: 1.0)

```
    Slow (0.5)      Normal (1.0)     Fast (2.0)
    
    ┄┄→             ──→              ══►
    Drag 10cm       Drag 10cm        Drag 10cm
    Move 2 units    Move 4 units     Move 8 units
```

### Zoom Speed (zoomSpeed: 1.0)

```
    Slow (0.5)      Normal (1.0)     Fast (2.0)
    
    ┄┄→             ──→              ══►
    1 wheel notch   1 wheel notch    1 wheel notch
    10% zoom        20% zoom         40% zoom
```

## Interactive Flow Diagram

```
    User Input
        ↓
    ┌─────────────────┐
    │ OrbitControls   │
    │ Event Listeners │
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ Damping Applied │  (if enabled)
    │ Factor: 0.05    │
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ Constraints     │
    │ Check & Apply   │
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ Camera Updated  │
    │ position/target │
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ controls.update()│  In animation loop
    └─────────────────┘
        ↓
    ┌─────────────────┐
    │ Scene Rendered  │
    │ New viewpoint   │
    └─────────────────┘
```

## Performance Visualization

```
    Frame Time Breakdown (60 FPS = 16.67ms)
    
    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Scene Rendering (12ms)
    ▓ Patient Animation (1ms)
    ▓ Time Bar Update (0.5ms)
    ░ OrbitControls Update (<0.1ms)
    
    Total: ~13.6ms ✅ Under 16.67ms budget
    
    OrbitControls: <1% of frame time
```

## User Journey Map

```
    1. Page Load
       ↓
    2. Default Isometric View
       Camera at (15, 10, 15)
       ↓
    3. User Explores
       ├─→ Left-Drag: Rotate view
       ├─→ Right-Drag: Pan to area of interest
       └─→ Scroll: Zoom in/out
       ↓
    4. Find Optimal View
       Custom camera position/angle
       ↓
    5. Observe Animation
       Watch patient flow from chosen angle
       ↓
    6. Re-adjust as Needed
       Continuous smooth interaction
```

## Comparison: Before vs After Phase 9

```
    BEFORE (Phases 2-8)
    
    ┌─────────────────┐
    │  Fixed Camera   │  ← Static viewpoint
    └────────┬────────┘
             ↓
        Single Angle
        
    User can:
    ❌ Cannot rotate
    ❌ Cannot pan
    ❌ Cannot zoom
    ✅ See animation
    
    
    AFTER (Phase 9)
    
         ↗ ↑ ↖        360° Freedom
    ┌─────────────────┐
    ← │  Interactive  │ →  Full control
    └─────────────────┘
         ↙ ↓ ↘
         
    User can:
    ✅ Rotate 360°
    ✅ Pan anywhere
    ✅ Zoom 5-50 units
    ✅ See animation from any angle
    ✅ Smooth damped movement
    ✅ Touch/mouse control
```

## Key Takeaways

1. **Left-Click Drag** = Rotate camera orbit
2. **Right-Click Drag** = Pan camera position
3. **Mouse Wheel** = Zoom in/out
4. **Damping** = Smooth natural feel
5. **Limits** = Prevent disorientation
6. **60 FPS** = Maintained performance
7. **Cross-Platform** = Desktop + Mobile

---

*Visual guide for Emergency Department 3D Flow Visualization - Phase 9 OrbitControls Implementation*
