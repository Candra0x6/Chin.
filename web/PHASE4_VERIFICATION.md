# Phase 4 - Visual Verification Guide

## 🎯 What You Should See

After running the development server and visiting `/ed-flow`, you should see:

### From the Isometric Camera View (15, 12, 15):

```
           ┌─────────────────────────────────┐
           │                                 │
           │  🏥 EMERGENCY DEPARTMENT 🏥     │
           │                                 │
           │   [E]  [🔴TRIAGE]  [BEDS]      │
           │         👤 👨‍⚕️     🛏️👤 🛏️👤   │
           │          👤        🛏️👤 🛏️👤   │
           │                   👨‍⚕️          │
           │                                 │
           │              [MORE BEDS]   [X]  │
           │              🛏️👤 🛏️👤         │
           │              🛏️👤 🛏️👤         │
           │                👨‍⚕️             │
           │                                 │
           └─────────────────────────────────┘
```

## ✅ Verification Checklist

### 1. Floor & Walls
- [ ] Dark gray floor (#303030) visible
- [ ] Light gray walls (#B0B0B0) surrounding the space
- [ ] Red triage zone (#882222) in the middle-left area
- [ ] Four walls clearly visible

### 2. Beds (Green #88C999)
- [ ] 10 beds total visible
- [ ] ~6 beds in Treatment zone (center area, X: -2 to 2)
- [ ] ~4 beds in Boarding zone (right area, X: 2 to 6)
- [ ] Beds arranged in 2 rows per zone
- [ ] Each bed has a lighter green pillow visible
- [ ] Beds are horizontal (lying flat)

### 3. Patients (White #FFFFFF)
- [ ] 10 patient figures visible
- [ ] Some patients lying in beds (rotated 90°)
- [ ] Some patients standing in triage area
- [ ] Patients have visible heads (spheres)
- [ ] Patients have capsule-shaped bodies
- [ ] White color clearly visible

### 4. Staff (Blue #3399FF)
- [ ] 4 staff figures visible
- [ ] Staff distributed across zones
- [ ] Staff members standing upright
- [ ] Blue color clearly distinguishable
- [ ] Staff slightly taller than patients
- [ ] Staff have visible heads (spheres)

### 5. Overall Scene
- [ ] Scene is well-lit and visible
- [ ] All objects properly positioned (no floating or buried)
- [ ] Colors match specifications
- [ ] No visual artifacts or glitches
- [ ] Canvas is responsive to window resizing

## 🔍 Detailed Object Inspection

### Beds:
```
Expected appearance:
- Box shape: 1.8m × 0.9m × 0.3m
- Green color: #88C999
- Pillow at one end (lighter green)
- Positioned at ~0.15m height
```

### Patients:
```
Expected appearance:
- Capsule body: cylinder with rounded caps
- Sphere head on top
- White color: #FFFFFF
- Height: ~1.5m total (body + head)
- In beds: rotated to horizontal
- Standing: vertical orientation
```

### Staff:
```
Expected appearance:
- Capsule body: similar to patients
- Sphere head on top
- Blue color: #3399FF
- Height: ~1.65m total (slightly taller)
- All standing upright
- Distributed across zones
```

## 🎨 Color Verification

Open browser DevTools and check colors:

```javascript
// Check bed color
const bed = scene.getObjectByName('Bed_0');
const bedFrame = bed.getObjectByName('BedFrame');
console.log('Bed color:', bedFrame.material.color.getHexString());
// Expected: "88c999"

// Check patient color
const patient = scene.getObjectByName('Patient_0');
const patientBody = patient.getObjectByName('PatientBody');
console.log('Patient color:', patientBody.material.color.getHexString());
// Expected: "ffffff"

// Check staff color
const staff = scene.getObjectByName('Staff_0');
const staffBody = staff.getObjectByName('StaffBody');
console.log('Staff color:', staffBody.material.color.getHexString());
// Expected: "3399ff"
```

## 📊 Object Count Verification

```javascript
// Verify object counts
const beds = scene.getObjectByName('Beds');
console.log('✓ Beds:', beds.children.length); // Should be 10

const patients = scene.getObjectByName('Patients');
console.log('✓ Patients:', patients.children.length); // Should be 10

const staff = scene.getObjectByName('StaffMembers');
console.log('✓ Staff:', staff.children.length); // Should be 4

// Verify bed components
const bed0 = scene.getObjectByName('Bed_0');
console.log('✓ Bed components:', bed0.children.length); // Should be 2 (frame + pillow)

// Verify patient components
const patient0 = scene.getObjectByName('Patient_0');
console.log('✓ Patient components:', patient0.children.length); // Should be 4 (body + 2 caps + head)

// Verify staff components
const staff0 = scene.getObjectByName('Staff_0');
console.log('✓ Staff components:', staff0.children.length); // Should be 4 (body + 2 caps + head)
```

## 📐 Position Verification

```javascript
// Check bed positions (should be in Treatment and Boarding zones)
const beds = scene.getObjectByName('Beds');
beds.children.forEach((bed, i) => {
  console.log(`Bed ${i} position:`, bed.position);
  // X should be between -2 and 6 (Treatment: -2 to 2, Boarding: 2 to 6)
  // Y should be ~0.15
  // Z should be ~±2.5
});

// Check patient positions
const patients = scene.getObjectByName('Patients');
patients.children.forEach((patient, i) => {
  console.log(`Patient ${i} position:`, patient.position);
  console.log(`Patient ${i} rotation:`, patient.rotation.z); // Some should be π/2 (lying)
});

// Check staff positions
const staff = scene.getObjectByName('StaffMembers');
staff.children.forEach((staffMember, i) => {
  console.log(`Staff ${i} position:`, staffMember.position);
  // Should be distributed across Triage, Treatment, and Boarding zones
});
```

## 🎯 Zone Distribution Check

### Treatment Zone (X: -2 to 2):
- Should contain ~6 beds
- Should contain treatment staff
- Should contain patients (some in beds)

### Boarding Zone (X: 2 to 6):
- Should contain ~4 beds
- Should contain boarding staff
- Should contain patients (some in beds)

### Triage Zone (X: -6 to -2):
- Should contain standing patients
- Should contain triage staff
- Red floor should be visible

## 🐛 Common Issues & Fixes

### Issue: No objects visible
**Fix**: Check console for errors. Ensure `createAllSceneObjects` is being called.

### Issue: Objects floating or underground
**Fix**: Check Y positions. Beds should be at 0.15m, standing figures at ~0.7m.

### Issue: Wrong colors
**Fix**: Verify COLORS constants are imported correctly.

### Issue: Objects too small/large
**Fix**: Remember 1 unit = 1 meter. Check dimensions against specs.

### Issue: Patients not lying in beds
**Fix**: Check rotation - patients in beds should have `rotation.z = π/2`.

## 📸 Screenshot Reference Points

Take screenshots showing:
1. **Full scene view** - All zones visible
2. **Treatment zone** - Close-up of beds with patients
3. **Triage zone** - Standing patients and staff on red floor
4. **Boarding zone** - Beds and patients awaiting discharge

## ✨ Success Criteria

Phase 4 is successful when:
- ✅ 10 green beds visible in correct positions
- ✅ 10 white patient figures (mix of lying and standing)
- ✅ 4 blue staff figures distributed across zones
- ✅ All objects properly scaled and positioned
- ✅ Colors match specifications exactly
- ✅ Scene is well-organized and realistic
- ✅ No visual glitches or errors
- ✅ Performance remains smooth (60fps)

---

**🎉 If all checks pass, Phase 4 is complete!**

Ready for Phase 5: Text Labels
