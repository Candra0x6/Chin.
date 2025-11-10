# OrbitControls Quick Reference

## Mouse Controls

| Action | Control | Effect |
|--------|---------|--------|
| **Rotate** | Left-click + Drag | Orbit camera around scene center |
| **Pan** | Right-click + Drag | Move camera parallel to view plane |
| **Pan (Alt)** | Shift + Left-click + Drag | Alternative panning method |
| **Zoom** | Mouse Wheel | Move camera closer/farther |

## Touch Controls (Mobile)

| Action | Gesture | Effect |
|--------|---------|--------|
| **Rotate** | One finger drag | Orbit camera around scene |
| **Pan** | Two finger drag | Move camera position |
| **Zoom** | Pinch gesture | Zoom in/out |

## Configuration Settings

### Current Implementation

```typescript
// Target (orbit center)
controls.target.set(0, 0, 0);

// Damping (smooth movement)
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Zoom limits
controls.minDistance = 5;    // Closest zoom
controls.maxDistance = 50;   // Farthest zoom

// Rotation limits
controls.minPolarAngle = 0;                  // Top-down view (0°)
controls.maxPolarAngle = Math.PI / 2 + 0.3;  // Near horizon (85°)

// Speed settings (all 1.0 = standard)
controls.panSpeed = 1.0;
controls.zoomSpeed = 1.0;
controls.rotateSpeed = 1.0;

// Features
controls.enablePan = true;
controls.enableZoom = true;
controls.enableRotate = true;
controls.autoRotate = false;
controls.screenSpacePanning = false;  // World-space panning
```

## Angles Explained

### Polar Angle (Vertical Rotation)
- **0 radians (0°)**: Camera looking straight down (top view)
- **π/4 radians (45°)**: Isometric-style view
- **π/2 radians (90°)**: Camera at horizon level (side view)
- **π/2 + 0.3 (85°)**: Our maximum (near horizon, can't go under floor)

### Azimuth Angle (Horizontal Rotation)
- **No limits set**: Full 360° rotation allowed
- **-π to +π**: Complete circle around scene center

## Common Adjustments

### Faster Controls
```typescript
controls.panSpeed = 2.0;
controls.zoomSpeed = 1.5;
controls.rotateSpeed = 1.5;
```

### Slower Controls (Precise)
```typescript
controls.panSpeed = 0.5;
controls.zoomSpeed = 0.5;
controls.rotateSpeed = 0.5;
```

### Tighter Zoom
```typescript
controls.minDistance = 3;   // Get even closer
controls.maxDistance = 30;  // Limit far view
```

### Restrict Vertical Rotation
```typescript
controls.minPolarAngle = Math.PI / 6;  // Min 30° from top
controls.maxPolarAngle = Math.PI / 3;  // Max 60° from top
```

### Enable Auto-Rotation
```typescript
controls.autoRotate = true;
controls.autoRotateSpeed = 2.0;  // degrees per second
```

### Screen-Space Panning
```typescript
controls.screenSpacePanning = true;  // Pan relative to screen
```

## Integration Pattern

### Setup (in useEffect)
```typescript
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
// ... other settings
controls.update();
controlsRef.current = controls;
```

### Update (in animation loop)
```typescript
if (controlsRef.current) {
  controlsRef.current.update();  // Required when damping enabled
}
```

### Cleanup (in useEffect return)
```typescript
if (controlsRef.current) {
  controlsRef.current.dispose();
}
```

## Distance Limits Guide

| Distance | View Type | Use Case |
|----------|-----------|----------|
| 5 units | Close-up | Examine individual patients/beds |
| 10-15 units | Medium | View 2-3 zones at once |
| 20-30 units | Wide | Full department overview |
| 40-50 units | Far | Strategic planning view |

## Polar Angle Guide

| Angle | Degrees | View Type | Use Case |
|-------|---------|-----------|----------|
| 0 | 0° | Top-down | Layout planning |
| π/6 | 30° | High angle | Good for zones |
| π/4 | 45° | Isometric | Balanced view |
| π/3 | 60° | Low angle | Patient level |
| π/2 | 90° | Horizon | Ground level |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Controls not working | Call `controls.update()` in animation loop |
| Jumpy movement | Enable damping and set reasonable factor (0.05) |
| Camera clips objects | Increase `minDistance` |
| Can't see full scene | Increase `maxDistance` |
| Camera goes upside-down | Set `maxPolarAngle < π/2` |

## Performance Tips

1. **Damping is cheap**: ~0.01ms overhead per frame
2. **Update only when needed**: Already in animation loop
3. **No event listeners**: OrbitControls uses renderer.domElement
4. **Dispose properly**: Call `.dispose()` on cleanup

## Advanced Features

### Change Orbit Target
```typescript
controls.target.set(5, 0, 0);  // Orbit around x=5 instead of center
controls.update();
```

### Disable Specific Controls
```typescript
controls.enablePan = false;    // Lock panning
controls.enableZoom = false;   // Lock zoom
controls.enableRotate = false; // Lock rotation
```

### Mouse Button Remapping
```typescript
controls.mouseButtons = {
  LEFT: THREE.MOUSE.ROTATE,
  MIDDLE: THREE.MOUSE.DOLLY,
  RIGHT: THREE.MOUSE.PAN
};
```

### Touch Gesture Remapping
```typescript
controls.touches = {
  ONE: THREE.TOUCH.ROTATE,
  TWO: THREE.TOUCH.DOLLY_PAN
};
```

## API Reference

### Properties
- `target: Vector3` - The center point to orbit around
- `enableDamping: boolean` - Enable smooth damping
- `dampingFactor: number` - Damping inertia (0.01-0.1)
- `minDistance: number` - Minimum zoom distance
- `maxDistance: number` - Maximum zoom distance
- `minPolarAngle: number` - Minimum vertical rotation
- `maxPolarAngle: number` - Maximum vertical rotation
- `minAzimuthAngle: number` - Minimum horizontal rotation
- `maxAzimuthAngle: number` - Maximum horizontal rotation

### Methods
- `update(): void` - Update controls (required if damping enabled)
- `dispose(): void` - Remove all event listeners
- `saveState(): void` - Save current camera state
- `reset(): void` - Reset to saved state
- `getPolarAngle(): number` - Get current polar angle
- `getAzimuthalAngle(): number` - Get current azimuthal angle
- `getDistance(): number` - Get current distance from target

### Events
```typescript
controls.addEventListener('change', () => {
  // Camera position/rotation changed
});

controls.addEventListener('start', () => {
  // User started interacting
});

controls.addEventListener('end', () => {
  // User stopped interacting
});
```

## Best Practices

1. ✅ **Always enable damping** for smooth feel
2. ✅ **Set sensible distance limits** to prevent clipping
3. ✅ **Restrict polar angle** to prevent disorientation
4. ✅ **Call update() in animation loop** when damping enabled
5. ✅ **Dispose controls** in cleanup to prevent memory leaks
6. ✅ **Use world-space panning** for architectural scenes
7. ❌ **Don't set dampingFactor too high** (>0.2) - feels sluggish
8. ❌ **Don't allow polar angle > π/2** unless intentional
9. ❌ **Don't forget to update()** - controls won't work with damping

## Example: Custom Presets

### Preset 1: Top-Down View
```typescript
camera.position.set(0, 20, 0);
controls.target.set(0, 0, 0);
controls.update();
```

### Preset 2: Isometric View
```typescript
camera.position.set(15, 10, 15);
controls.target.set(0, 0, 0);
controls.update();
```

### Preset 3: Side View
```typescript
camera.position.set(25, 5, 0);
controls.target.set(0, 0, 0);
controls.update();
```

## Resources

- [Three.js OrbitControls Documentation](https://threejs.org/docs/#examples/en/controls/OrbitControls)
- [OrbitControls Source Code](https://github.com/mrdoob/three.js/blob/dev/examples/jsm/controls/OrbitControls.js)
- [Three.js Examples](https://threejs.org/examples/#misc_controls_orbit)
