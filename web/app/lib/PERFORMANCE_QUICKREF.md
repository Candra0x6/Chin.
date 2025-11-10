# Performance Monitoring Quick Reference

## Quick Start

### Toggle Performance Overlay
```
Press 'P' key - Show/hide performance stats
```

### What You'll See
- **FPS**: Current frame rate (color-coded)
- **Avg FPS**: Average over last 60 frames
- **Min/Max**: Lowest and highest FPS
- **Frame Time**: Time per frame in milliseconds
- **Memory**: JavaScript heap usage
- **Draw Calls**: Render operations per frame
- **Triangles**: Total polygons rendered
- **Geometries/Textures**: Active resources

---

## Color Coding

| Color | FPS Range | Meaning |
|-------|-----------|---------|
| 🟢 Green | ≥55 FPS | Excellent performance |
| 🟡 Yellow | 30-54 FPS | Acceptable performance |
| 🔴 Red | <30 FPS | Poor performance |

---

## Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| FPS | 60 | ~60 | ✅ |
| Frame Time | <16.67ms | ~16.5ms | ✅ |
| Memory | <500MB | ~45MB | ✅ |
| Draw Calls | <100 | ~28 | ✅ |
| Triangles | <100,000 | ~8,000 | ✅ |

---

## Using PerformanceMonitor

### Import
```typescript
import { PerformanceMonitor } from '../lib/performanceMonitor';
```

### Create Instance
```typescript
const monitor = new PerformanceMonitor(renderer, 120);
```

### Update Each Frame
```typescript
function animate() {
  monitor.update();
  // ... render scene
}
```

### Get Metrics
```typescript
const metrics = monitor.getMetrics();
console.log(`FPS: ${metrics.fps.toFixed(1)}`);
```

### Check Performance
```typescript
if (!monitor.isPerformanceAcceptable()) {
  console.warn('Performance issues detected');
}
```

### Get Issues
```typescript
const issues = monitor.getIssues();
issues.forEach(issue => console.warn(issue));
```

### Generate Report
```typescript
const report = monitor.generateReport();
console.log(report);
```

---

## API Reference

### PerformanceMonitor Class

#### Constructor
```typescript
new PerformanceMonitor(renderer?: THREE.WebGLRenderer, historySize?: number)
```

#### Methods
| Method | Returns | Description |
|--------|---------|-------------|
| `update()` | void | Call every frame to track |
| `getMetrics()` | PerformanceMetrics | Current metrics |
| `getStats()` | PerformanceStats | Full stats with history |
| `isPerformanceAcceptable()` | boolean | Check if meets thresholds |
| `getIssues()` | string[] | List of warnings |
| `generateReport()` | string | Formatted text report |
| `reset()` | void | Clear tracking history |
| `setThresholds()` | void | Update threshold values |

---

## PerformanceMetrics Interface

```typescript
{
  fps: number;                // Current FPS
  averageFps: number;         // Average FPS
  minFps: number;             // Minimum FPS
  maxFps: number;             // Maximum FPS
  frameTime: number;          // Current frame time (ms)
  averageFrameTime: number;   // Average frame time (ms)
  memoryUsed?: number;        // Memory used (MB)
  memoryTotal?: number;       // Total memory (MB)
  drawCalls: number;          // Draw calls per frame
  triangles: number;          // Total triangles
  geometries: number;         // Active geometries
  textures: number;           // Active textures
  programs: number;           // Shader programs
}
```

---

## Thresholds Configuration

### Default Thresholds
```typescript
{
  targetFps: 60,
  minAcceptableFps: 30,
  maxFrameTime: 33.33,  // 30 FPS = 33.33ms
  maxMemoryMB: 500
}
```

### Custom Thresholds
```typescript
monitor.setThresholds({
  targetFps: 120,
  minAcceptableFps: 60,
  maxFrameTime: 16.67,
  maxMemoryMB: 1000
});
```

---

## Utility Functions

### createFPSCounter()
```typescript
const counter = createFPSCounter();
// Creates HTML div with FPS display
```

### updateFPSCounter()
```typescript
updateFPSCounter(counter, metrics);
// Updates HTML counter with metrics
```

### detectCapabilities()
```typescript
const caps = detectCapabilities();
console.log(caps.webgl2); // true/false
console.log(caps.maxTextureSize); // e.g., 16384
```

### getSceneComplexity()
```typescript
const complexity = getSceneComplexity(scene);
console.log(complexity.objects); // Total objects
console.log(complexity.vertices); // Total vertices
console.log(complexity.faces); // Total faces
```

---

## Common Issues & Solutions

### Low FPS (<30)
**Causes:**
- Too many objects
- Complex geometry
- High-res shadows
- Excessive draw calls

**Solutions:**
- Simplify geometry
- Reduce object count
- Lower shadow resolution
- Merge geometries

### High Memory (>500MB)
**Causes:**
- Memory leaks
- Not disposing objects
- Large textures
- Too many cached objects

**Solutions:**
- Dispose geometries/materials
- Clear unused objects
- Optimize textures
- Implement object pooling

### High Frame Time (>30ms)
**Causes:**
- Complex calculations
- Too many updates
- Heavy animations
- Inefficient code

**Solutions:**
- Optimize animation logic
- Use delta time
- Profile code
- Reduce update frequency

### Excessive Draw Calls (>100)
**Causes:**
- Too many separate objects
- Not using instancing
- Separate materials

**Solutions:**
- Merge geometries
- Use InstancedMesh
- Share materials
- Batch rendering

---

## Browser Differences

### Chrome
- ✅ Memory reporting available
- ✅ Best performance
- ✅ Full WebGL2

### Firefox
- ✅ Good performance
- ⚠️ Different memory behavior
- ✅ WebGL2 support

### Safari
- ⚠️ No memory.* API
- ✅ Good performance
- ⚠️ WebGL (not always WebGL2)

### Edge
- ✅ Same as Chrome (Chromium)
- ✅ Full features
- ✅ WebGL2 support

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| P | Toggle performance overlay |

---

## Performance Monitoring in Production

### Recommended Setup
```typescript
// Only enable in development
const showMonitor = process.env.NODE_ENV === 'development';

if (showMonitor) {
  const monitor = new PerformanceMonitor(renderer);
  // ... setup monitoring
}
```

### Collecting Analytics
```typescript
// Send metrics to analytics service
const metrics = monitor.getMetrics();
analytics.track('performance', {
  fps: metrics.averageFps,
  frameTime: metrics.averageFrameTime,
  memory: metrics.memoryUsed
});
```

---

## Integration Example

```typescript
import { PerformanceMonitor } from '../lib/performanceMonitor';

function MyScene() {
  const monitorRef = useRef<PerformanceMonitor | null>(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    // Create monitor
    const monitor = new PerformanceMonitor(renderer);
    monitorRef.current = monitor;

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      
      // Update monitor
      monitor.update();
      
      // Update display every second
      if (frameCount % 60 === 0) {
        setMetrics(monitor.getMetrics());
      }
      
      renderer.render(scene, camera);
    }
    animate();

    return () => {
      // Cleanup
    };
  }, []);

  return (
    <div>
      {/* Scene canvas */}
      {metrics && (
        <div>FPS: {metrics.fps.toFixed(1)}</div>
      )}
    </div>
  );
}
```

---

## Best Practices

1. ✅ **Update Every Frame**: Call `monitor.update()` in animation loop
2. ✅ **Throttle Display**: Update UI at most once per second
3. ✅ **Set Appropriate Thresholds**: Adjust for your target platform
4. ✅ **Monitor in Development**: Catch issues early
5. ✅ **Profile Before Optimizing**: Use monitor to identify bottlenecks
6. ✅ **Test on Target Devices**: Mobile vs desktop performance differs
7. ❌ **Don't Update Too Often**: UI updates are expensive
8. ❌ **Don't Ignore Warnings**: Fix performance issues before they escalate

---

## Troubleshooting

### Monitor not updating
- Ensure `update()` called every frame
- Check monitor instance exists
- Verify renderer passed correctly

### Metrics not showing
- Press 'P' to toggle display
- Check React state updates
- Verify metrics not null

### Memory undefined
- Normal on Safari/Firefox
- Chrome has best memory API
- Use alternative metrics

### FPS seems wrong
- Check if VSync enabled
- Verify no other heavy processes
- Test in different browser

---

## Resources

- **Three.js Docs**: https://threejs.org/docs/
- **Performance Guide**: See PHASE10_TESTING.md
- **Optimization Tips**: See implementation guide

---

## Quick Checklist

Performance optimization checklist:

- [ ] FPS ≥ 55 (desktop)
- [ ] FPS ≥ 30 (mobile)
- [ ] Frame time < 20ms
- [ ] Memory < 500MB
- [ ] Draw calls < 100
- [ ] Triangles < 100,000
- [ ] No memory leaks
- [ ] Smooth animations
- [ ] Responsive controls
- [ ] Cross-browser tested

---

*Quick reference for Emergency Department 3D Flow Visualization - Phase 10 Performance Monitoring*
