# Quick Start Guide - Phase 3

## 🚀 See Your 3D Environment Now!

### Step 1: Run the Development Server
```bash
cd web
npm run dev
```

### Step 2: Open in Browser
Navigate to:
```
http://localhost:3000/ed-flow
```

## 🎨 What You Should See

You'll see a 3D emergency department environment with:

1. **Dark Gray Floor** - The main floor plane (#303030)
2. **Light Gray Walls** - Four walls (2m high) surrounding the space
3. **Red Triage Zone** - Highlighted area in the middle-left section
4. **Zone Boundaries** - Subtle lines dividing the five zones

## 🖱️ Current Interactions

- The camera is positioned at an isometric angle (15, 12, 15)
- The view is static for now (OrbitControls will be added in Phase 9)
- The canvas is responsive - try resizing your browser window!

## 🎯 What's Next?

**Phase 4** will add:
- 🛏️ Hospital beds in Treatment and Boarding zones
- 👤 Patient figures (white humanoid shapes)
- 👨‍⚕️ Staff figures (blue humanoid shapes)

## 🔍 Debugging

### Open Browser Console and Type:

```javascript
// Check if Three.js scene exists
console.log('Check canvas:', document.querySelector('canvas'));

// Verify zone layout constants
console.log('Zones loaded from module');
```

### Expected View:

```
     ┌─────────────────────┐
     │                     │
     │  ╔══╦═══╦════╦════╗ │
     │  ║  ║🔴 ║    ║    ║ │  ← Red triage zone visible
     │  ╚══╩═══╩════╩════╝ │
     │                     │
     └─────────────────────┘
     
Isometric view from top-right corner
```

## 📁 Files Created

### Core Implementation:
- ✅ `app/lib/environmentUtils.ts` - Environment creation utilities
- ✅ `app/components/ThreeScene.tsx` - Main scene component (updated)

### Documentation:
- ✅ `PHASE3_IMPLEMENTATION.md` - Complete Phase 3 documentation
- ✅ `ZONE_LAYOUT.md` - Visual zone layout guide
- ✅ `app/lib/exampleUsage.ts` - Helper function examples

## ✨ Features Implemented

### Environment System:
- [x] Modular environment creation
- [x] Zone-based coordinate system
- [x] Color palette constants
- [x] Helper functions for positioning
- [x] Type-safe zone definitions

### Visual Elements:
- [x] Main floor (20m x 12m)
- [x] Four walls (2m height)
- [x] Triage zone overlay
- [x] Zone boundary markers

### Performance:
- [x] Simple materials (MeshLambertMaterial)
- [x] Shadow-ready meshes
- [x] Grouped objects for easy management
- [x] Named objects for debugging

## 🛠️ Troubleshooting

### Problem: Black screen
**Solution**: Check browser console for errors. Ensure WebGL is supported.

### Problem: No red zone visible
**Solution**: The triage zone might be at the same level as the floor. It's elevated by 0.01m to prevent z-fighting.

### Problem: Can't see walls
**Solution**: Adjust camera position or wait for Phase 9 (OrbitControls) to rotate the view.

### Problem: TypeScript errors
**Solution**: Run `npm install` to ensure all dependencies are installed.

## 📊 Performance Stats

Expected performance:
- **FPS**: 60fps on modern hardware
- **Draw Calls**: ~10 (floor, 4 walls, triage zone, markers)
- **Triangles**: <100 (very low poly)
- **Memory**: <50MB

## 🎓 Learning Resources

### Understanding the Code:

1. **environmentUtils.ts** - Study the factory pattern for creating 3D objects
2. **ZONE_LAYOUT.md** - Visual guide to the coordinate system
3. **exampleUsage.ts** - Examples of how to use helper functions

### Next Phase Preview:

Phase 4 will use these helper functions:
- `getRandomPositionInZone()` - Place beds randomly in zones
- `getZoneCenter()` - Position objects at zone centers
- `COLORS` constants - Color the beds, patients, and staff

---

**🎉 Congratulations!** 

You've completed Phase 3! The environment is ready for populating with 3D objects in Phase 4.
