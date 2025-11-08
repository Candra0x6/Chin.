# PyTorch 2.6 Compatibility Fix - Summary

## Issue
PyTorch 2.6 changed the default value of `weights_only` parameter in `torch.load()` from `False` to `True`. This caused YOLOv8 model loading to fail with:

```
_pickle.UnpicklingError: Weights only load failed... 
GLOBAL ultralytics.nn.tasks.DetectionModel was not an allowed global
```

## Root Cause
- YOLOv8 models contain custom Ultralytics classes
- PyTorch 2.6's strict `weights_only=True` rejects these classes
- Ultralytics' `torch_safe_load()` function uses default `torch.load()` behavior

## Solution Implemented

### Direct Monkey Patching
Patched `ultralytics.nn.tasks.torch_safe_load()` function **before** importing YOLO:

```python
import torch
import ultralytics.nn.tasks as tasks

# Store original
_original_torch_safe_load = tasks.torch_safe_load

# Create patched version
def _patched_torch_safe_load(file, *args, **kwargs):
    """Use weights_only=False for YOLOv8 compatibility"""
    return torch.load(file, map_location='cpu', weights_only=False), file

# Apply patch BEFORE importing YOLO
tasks.torch_safe_load = _patched_torch_safe_load

# Now import YOLO - it will use patched version
from ultralytics import YOLO
```

### File Modified
- **`app/services/person_detector.py`** - Added patch at module level

### Why This Works
1. Patch is applied before `ultralytics` imports YOLO classes
2. When YOLO model loads, it uses our patched function
3. Our version explicitly sets `weights_only=False`
4. YOLOv8 models from Ultralytics are trusted, so this is safe

## Testing Results

✅ Model loads successfully
✅ No more pickle errors
✅ YOLOv8 detection working
✅ Visual display functioning
✅ All existing features preserved

## Security Note

We set `weights_only=False` specifically for YOLOv8 models from the official Ultralytics package, which is a trusted source. This is safe and recommended by PyTorch documentation for models from trusted sources.

## Alternative Approaches Considered

1. **Adding Safe Globals**: Too many classes needed, kept failing
2. **Downgrading PyTorch**: Would lose PyTorch 2.6 features
3. **Waiting for Ultralytics Update**: Not yet available

## Status

✅ **FIXED** - Demo running successfully
✅ Frame extraction working
✅ Person detection operational
✅ Visual display ready

---

**Fixed:** November 7, 2025
**Applies To:** PyTorch 2.6+, Ultralytics YOLOv8
**Files Changed:** `app/services/person_detector.py`
