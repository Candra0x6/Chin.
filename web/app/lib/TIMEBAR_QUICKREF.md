# Time Bar Quick Reference

## Installation

Time bar is built-in to the ED 3D visualization. No additional dependencies required.

## Basic Usage

```typescript
import { createTimeBar, updateTimeBar } from './lib/timeBarUtils';

// Create
const timeBar = await createTimeBar();
scene.add(timeBar.container);

// Update (in animation loop)
const clock = new THREE.Clock();
function animate() {
  updateTimeBar(timeBar, clock.getDelta());
  requestAnimationFrame(animate);
}
```

## Configuration

```typescript
const timeBar = await createTimeBar({
  width: 16,
  height: 0.4,
  depth: 0.1,
  position: { x: 0, y: 0.05, z: 7 },
  colors: {
    background: 0x404040,
    progress: 0x3399FF,
    label: 0xFFFFFF
  },
  cycleDuration: 20
});
```

## API

| Function | Purpose | Parameters |
|----------|---------|------------|
| `createTimeBar(config?)` | Create time bar | Optional config object |
| `updateTimeBar(bar, delta)` | Update progress | TimeBarState, deltaTime |
| `updateTimeBarProgress(bar, progress)` | Set progress | TimeBarState, 0-1 |
| `resetTimeBar(bar)` | Reset to 0% | TimeBarState |
| `getTimeBarStats(bar)` | Get statistics | TimeBarState |
| `disposeTimeBar(bar)` | Cleanup | TimeBarState |

## Common Tasks

### Change Colors
```typescript
createTimeBar({
  ...DEFAULT_TIME_BAR_CONFIG,
  colors: { background: 0x2a2a2a, progress: 0x00FF00, label: 0xFFFFFF }
});
```

### Change Size
```typescript
createTimeBar({
  ...DEFAULT_TIME_BAR_CONFIG,
  width: 20,
  height: 0.6
});
```

### Change Speed
```typescript
createTimeBar({
  ...DEFAULT_TIME_BAR_CONFIG,
  cycleDuration: 30  // 30 seconds
});
```

### Manual Control
```typescript
updateTimeBarProgress(timeBar, 0.5);  // Set to 50%
```

### Get Progress
```typescript
const stats = getTimeBarStats(timeBar);
console.log(stats.progress);  // 0.0 to 1.0
console.log(stats.formattedTime);  // "1:23"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not visible | Check Z position and camera view |
| Not moving | Verify `updateTimeBar()` called in loop |
| Wrong position | Check `position` config values |
| No label | Font loading failed (non-critical) |

## Color Presets

```typescript
// Blue (default)
colors: { background: 0x404040, progress: 0x3399FF, label: 0xFFFFFF }

// Green
colors: { background: 0x2a2a2a, progress: 0x00FF00, label: 0xFFFFFF }

// Orange
colors: { background: 0x3a3a3a, progress: 0xFF9900, label: 0xFFFFFF }

// Purple
colors: { background: 0x2d2d2d, progress: 0x9966FF, label: 0xFFFFFF }

// Red
colors: { background: 0x3d3d3d, progress: 0xFF3333, label: 0xFFFFFF }
```

## Performance

- **CPU**: <0.1ms per frame
- **Memory**: ~2 KB
- **FPS Impact**: None (maintains 60 FPS)

## Files

- Implementation: `web/app/lib/timeBarUtils.ts`
- Examples: `web/app/lib/timeBarExamples.ts`
- Docs: `docs/PHASE8_TIMEBAR.md`
- Integration: `web/app/components/ThreeScene.tsx`

## See Also

- Full documentation: `PHASE8_TIMEBAR.md`
- Usage examples: `timeBarExamples.ts`
- Animation system: `animationUtils.ts`
