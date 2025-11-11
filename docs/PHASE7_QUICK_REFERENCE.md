# Phase 7 Quick Reference Guide

## 🎯 Quick Links

- [Toast Notifications](#toast-notifications)
- [Skeleton Loaders](#skeleton-loaders)
- [Theme Toggle](#theme-toggle)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Custom Animations](#custom-animations)

---

## Toast Notifications

### Basic Usage

```tsx
import { useToast } from '@/contexts';

function MyComponent() {
  const toast = useToast();
  
  // Success toast
  toast.success('Operation completed successfully!');
  
  // Error toast
  toast.error('Something went wrong!');
  
  // Info toast
  toast.info('Processing your request...');
  
  // Warning toast
  toast.warning('Please review your input');
}
```

### Custom Duration

```tsx
// Toast that stays for 10 seconds
toast.success('This will stay longer', 10000);

// Toast that stays for 2 seconds
toast.error('Quick message', 2000);
```

### Toast Types

| Type | Icon | Color | Use Case |
|------|------|-------|----------|
| `success` | ✓ | Green | Successful operations |
| `error` | ✕ | Red | Errors and failures |
| `info` | ℹ | Blue | Informational messages |
| `warning` | ⚠ | Yellow | Warnings and cautions |

---

## Skeleton Loaders

### Available Components

```tsx
import { 
  Skeleton,          // Base skeleton
  SkeletonText,      // Text lines
  SkeletonCard,      // Card placeholder
  SkeletonChart,     // Chart placeholder
  SkeletonTable,     // Table rows
  SkeletonGrid       // Grid of cards
} from '@/components';
```

### Basic Usage

```tsx
function MyComponent() {
  const { data, isLoading } = useData();
  
  if (isLoading) {
    return <SkeletonCard />;
  }
  
  return <Card data={data} />;
}
```

### Custom Skeleton

```tsx
// Custom width and height
<Skeleton width="200px" height="40px" />

// Custom animation
<Skeleton animation="shimmer" />
<Skeleton animation="none" />  // No animation
```

### Multiple Lines

```tsx
// 4 lines (default)
<SkeletonText />

// Custom number of lines
<SkeletonText lines={6} />
```

### Grid Layout

```tsx
// 6 cards (default)
<SkeletonGrid />

// Custom number of cards
<SkeletonGrid count={9} />
```

---

## Theme Toggle

### Usage

The theme toggle is already integrated in the main layout. Users can:

1. Click the theme toggle button in the header
2. Theme persists in localStorage
3. All components automatically update

### Accessing Theme State

```tsx
import { useApp } from '@/contexts';

function MyComponent() {
  const { theme } = useApp();
  
  console.log(theme); // 'light' or 'dark'
}
```

### Manual Theme Change

```tsx
import { useApp } from '@/contexts';

function MyComponent() {
  const { theme, setTheme } = useApp();
  
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };
}
```

---

## Keyboard Shortcuts

### Available Shortcuts

| Shortcut | Mac | Action |
|----------|-----|--------|
| `Ctrl + U` | `⌘ + U` | Scroll to upload section |
| `Ctrl + H` | `⌘ + H` | Navigate to history page |
| `Ctrl + /` | `⌘ + /` | Show shortcuts help |
| `?` | `?` | Show shortcuts help |
| `Esc` | `Esc` | Close modals |

### Adding Custom Shortcuts

```tsx
import { KeyboardShortcuts } from '@/components';

function MyPage() {
  const handleCustomAction = () => {
    console.log('Custom action triggered');
  };
  
  return (
    <KeyboardShortcuts
      onUpload={handleUpload}
      onHistory={() => router.push('/history')}
      onHelp={() => setShowHelp(true)}
    />
  );
}
```

### Shortcuts Modal

```tsx
import { KeyboardShortcutsModal } from '@/components';

function MyPage() {
  const [showShortcuts, setShowShortcuts] = useState(false);
  
  return (
    <KeyboardShortcutsModal
      isOpen={showShortcuts}
      onClose={() => setShowShortcuts(false)}
    />
  );
}
```

---

## Custom Animations

### Available Animations

```tsx
// Slide in from right
<div className="animate-slideIn">Content</div>

// Slide out to right
<div className="animate-slideOut">Content</div>

// Fade in
<div className="animate-fadeIn">Content</div>

// Fade out
<div className="animate-fadeOut">Content</div>

// Shimmer effect (for skeletons)
<div className="animate-shimmer">Loading...</div>

// Gentle bounce on hover
<div className="group">
  <div className="group-hover:animate-bounce-slow">Icon</div>
</div>
```

### Animation Durations

All animations use standard durations:
- `slideIn/slideOut`: 300ms
- `fadeIn/fadeOut`: 300ms
- `shimmer`: 2000ms (loop)
- `bounce-slow`: 1000ms

### Combining with Tailwind

```tsx
// Scale on hover with bounce
<div className="group hover:scale-105 transition-transform">
  <div className="group-hover:animate-bounce-slow">🎉</div>
</div>

// Fade in with delay
<div className="animate-fadeIn delay-200">Content</div>
```

---

## Common Patterns

### Loading State with Toast

```tsx
function MyComponent() {
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);
  
  const handleAction = async () => {
    setIsLoading(true);
    toast.info('Processing...');
    
    try {
      await someAction();
      toast.success('Success!');
    } catch (error) {
      toast.error(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return <SkeletonCard />;
  }
  
  return <ActualContent />;
}
```

### Upload Flow with All Features

```tsx
function UploadPage() {
  const toast = useToast();
  const { addToHistory } = useApp();
  const [showShortcuts, setShowShortcuts] = useState(false);
  const uploadBoxRef = useRef<HTMLDivElement>(null);
  
  const handleUploadSuccess = (result: VideoUploadResponse) => {
    // Add to history
    addToHistory({
      id: result.id,
      filename: result.filename,
      uploadedAt: new Date().toISOString(),
      status: 'processing',
    });
    
    // Show toast
    toast.success('Video uploaded successfully!');
    
    // Navigate
    router.push(`/analysis/${result.id}`);
  };
  
  const scrollToUpload = () => {
    uploadBoxRef.current?.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'center' 
    });
  };
  
  return (
    <>
      <KeyboardShortcuts
        onUpload={scrollToUpload}
        onHistory={() => router.push('/history')}
        onHelp={() => setShowShortcuts(true)}
      />
      
      <KeyboardShortcutsModal
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />
      
      <div ref={uploadBoxRef}>
        <UploadBox onUploadSuccess={handleUploadSuccess} />
      </div>
    </>
  );
}
```

### Data Fetching with Skeletons

```tsx
function DataPage() {
  const { data, isLoading, error } = useQuery();
  const toast = useToast();
  
  useEffect(() => {
    if (error) {
      toast.error(`Failed to load data: ${error.message}`);
    }
  }, [error]);
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        <SkeletonText />
        <SkeletonChart />
        <SkeletonTable />
      </div>
    );
  }
  
  return <DataDisplay data={data} />;
}
```

---

## Best Practices

### Toast Notifications
- ✅ Use success for completed actions
- ✅ Use error for failures
- ✅ Use info for ongoing processes
- ✅ Use warning for user attention
- ✅ Keep messages concise (< 60 chars)
- ❌ Don't spam multiple toasts
- ❌ Don't use for critical errors (use modals instead)

### Skeleton Loaders
- ✅ Match the shape of actual content
- ✅ Use for expected wait times > 200ms
- ✅ Keep animations subtle (pulse or shimmer)
- ❌ Don't use for instant responses
- ❌ Don't mix multiple animation styles

### Keyboard Shortcuts
- ✅ Use common shortcuts (Ctrl+S, Ctrl+Z, etc.)
- ✅ Provide visual help (? key)
- ✅ Disable in input fields
- ❌ Don't override browser shortcuts
- ❌ Don't use too many custom shortcuts

### Theme Toggle
- ✅ Persist user preference
- ✅ Provide smooth transitions
- ✅ Support system preference
- ❌ Don't force a theme
- ❌ Don't forget dark mode colors

---

## Troubleshooting

### Toasts Not Appearing
1. Check `ToastProvider` is in layout
2. Verify `ToastContainer` is rendered
3. Check browser console for errors

### Skeletons Not Animating
1. Verify Tailwind config includes animations
2. Check `globals.css` has keyframes
3. Try different animation types

### Theme Not Persisting
1. Check localStorage permissions
2. Verify `AppContext` is wrapping app
3. Check browser developer tools > Application > Local Storage

### Keyboard Shortcuts Not Working
1. Check if input field is focused
2. Verify event listeners are attached
3. Check browser console for errors
4. Try refreshing the page

---

## Component Props Reference

### ToastContext

```tsx
interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
}
```

### Skeleton Props

```tsx
interface SkeletonProps {
  width?: string;
  height?: string;
  animation?: 'pulse' | 'shimmer' | 'none';
}

interface SkeletonTextProps {
  lines?: number;
}

interface SkeletonGridProps {
  count?: number;
}

interface SkeletonTableProps {
  rows?: number;
}
```

### KeyboardShortcuts Props

```tsx
interface KeyboardShortcutsProps {
  onUpload?: () => void;
  onHistory?: () => void;
  onHelp?: () => void;
}

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

---

## Examples Repository

For more examples, check:
- `app/page.tsx` - Main page with all features
- `app/layout.tsx` - Provider setup
- `contexts/ToastContext.tsx` - Toast implementation
- `components/Skeleton.tsx` - Skeleton variants

---

**Last Updated**: January 2025  
**Phase**: 7 - UI/UX Enhancements  
**Status**: ✅ Complete
