# Emergency Department Zone Layout

## Top-Down View (Y-axis looking down)

```
                    Z-axis
                      ↑
                      |
    ┌─────────────────┼─────────────────┐
    │                 │                 │ +6 (Front)
    │  ╔══════╦═══════╬═══════╦════════╗│
    │  ║      ║       ║       ║        ║│
    │  ║  EN  ║  TR   ║  TRT  ║   BR   ║ EXIT
    │  ║      ║  🔴   ║       ║        ║│
────┼──╫──────╫───────╫───────╫────────╫┼──── X-axis
    │  ║      ║  🔴   ║       ║        ║│
    │  ║      ║       ║       ║        ║│
    │  ╚══════╩═══════╩═══════╩════════╝│
    │                 │                 │ -6 (Back)
    └─────────────────┼─────────────────┘
                      |
   -10              -8  -6  -2  0  +2  +6  +8             +10
```

## Zone Breakdown

### 1. ENTRANCE Zone
- **X Range**: -8 to -6 (2m width)
- **Purpose**: Entry point for patients
- **Color**: Dark gray floor (#303030)
- **Objects**: None (clear path)

### 2. TRIAGE Zone 🔴
- **X Range**: -6 to -2 (4m width)
- **Purpose**: Initial patient assessment
- **Color**: **Red floor (#882222)** - HIGHLIGHTED
- **Objects**: Staff figures, waiting patients

### 3. TREATMENT Zone
- **X Range**: -2 to +2 (4m width)
- **Purpose**: Active treatment area
- **Color**: Dark gray floor (#303030)
- **Objects**: Beds (4-5), patients, staff

### 4. BOARDING Zone
- **X Range**: +2 to +6 (4m width)
- **Purpose**: Patients awaiting admission/discharge
- **Color**: Dark gray floor (#303030)
- **Objects**: Beds (4-5), patients

### 5. EXIT Zone
- **X Range**: +6 to +8 (2m width)
- **Purpose**: Discharge/transfer point
- **Color**: Dark gray floor (#303030)
- **Objects**: None (clear path)

## Wall Layout

```
                  BackWall (20m wide)
    ┌───────────────────────────────────────┐
    │                                       │
    │                                       │
    │  [Light Gray #B0B0B0, 2m height]     │ Right
Left│                                       │ Wall
Wall│           EMERGENCY DEPT              │
    │                                       │
    │                                       │
    │                                       │
    └───────────────────────────────────────┘
                  FrontWall (20m wide)
```

## Coordinate System

### Origin Point (0, 0, 0)
- **Location**: Center of the floor
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Down (-) to Up (+)
- **Z-axis**: Back (-) to Front (+)

### Scale
- **1 unit = 1 meter** in real-world dimensions

### Camera Position
- **Current**: (15, 12, 15) - Isometric view
- **Looking at**: (0, 0, 0) - Center of scene

## Patient Flow Path

```
Entry → Triage → Treatment → Boarding → Exit
 -7      -4         0          4        7
```

Typical patient journey:
1. **ENTRANCE** (-7, 0, 0): Patient arrives
2. **TRIAGE** (-4, 0, 0): Initial assessment on red floor
3. **TREATMENT** (0, 0, 0): Receives treatment in bed
4. **BOARDING** (4, 0, 0): Waits for admission/discharge
5. **EXIT** (7, 0, 0): Leaves facility

## Zone Boundaries (Visible Lines)

Subtle gray lines mark boundaries between zones:
- Line at X = -6 (Entrance | Triage)
- Line at X = -2 (Triage | Treatment)
- Line at X = +2 (Treatment | Boarding)
- Line at X = +6 (Boarding | Exit)

## Helper Functions Usage

### Get Zone Center:
```typescript
import { getZoneCenter, ZONES } from './environmentUtils';

const triageCenter = getZoneCenter('TRIAGE');
// Returns: Vector3(-4, 0, 0)
```

### Get Random Position in Zone:
```typescript
import { getRandomPositionInZone } from './environmentUtils';

const randomBedPosition = getRandomPositionInZone('TREATMENT', 0.5);
// Returns: Vector3(random X between -2 and 2, 0.5, random Z)
```

## Visual Elements

### Current (Phase 3):
✅ Main floor (dark gray)
✅ 4 walls (light gray, 2m high)
✅ Triage zone (red overlay)
✅ Zone boundary lines

### Coming Next (Phase 4):
- 🛏️ Beds in Treatment & Boarding zones
- 👤 Patient figures (white)
- 👨‍⚕️ Staff figures (blue)
