# Dark Mode Improvements for Goalin UI

## Changes Made

### Problem
Several components in the app had light backgrounds that didn't fit with the dark mode aesthetic:
1. Section cards in Overview (Activity Heatmap, Top Applications, Category Breakdown)
2. Section cards in Insights view (Browser Activity, Productivity Insights)
3. App item rows had barely visible backgrounds
4. Borders were designed for light mode

### Solution

#### 1. Section Cards (`section-card` class)
**Before:**
```css
.section-card {
    background: white;
    border: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
```

**After:**
```css
.section-card {
    background: rgba(255, 255, 255, 0.05);  /* Semi-transparent white overlay */
    border: 1px solid rgba(255, 255, 255, 0.08);  /* Subtle light border */
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);  /* Darker shadow for depth */
}
```

**Impact:**
- Cards now have a subtle dark background that blends with the overall dark theme
- Maintains visual separation while staying consistent with dark mode
- Creates depth with stronger shadow

#### 2. App Item Rows (`app-item` class)
**Before:**
```css
.app-item {
    background: rgba(0, 0, 0, 0.02);  /* Almost invisible */
}
```

**After:**
```css
.app-item {
    background: rgba(255, 255, 255, 0.03);  /* Subtle light overlay */
}
```

**Impact:**
- Items are more visible without being too bright
- Better separation between list items
- Consistent with dark mode palette

#### 3. Stat Cards (`stat-card` class)
**Before:**
```css
.stat-card {
    border: 1px solid rgba(0, 0, 0, 0.06);  /* Dark border */
}
```

**After:**
```css
.stat-card {
    border: 1px solid rgba(255, 255, 255, 0.08);  /* Light border */
}
```

**Impact:**
- Borders are now visible in dark mode
- Maintains card separation
- Complements the gradient backgrounds

#### 4. Badge Colors (Enhanced Visibility)

**Category Badge:**
```css
/* Before */
.category-badge {
    background: rgba(52, 152, 219, 0.15);
    color: rgba(52, 152, 219, 1);  /* Darker blue */
}

/* After */
.category-badge {
    background: rgba(52, 152, 219, 0.25);  /* More opaque */
    color: rgba(100, 181, 246, 1);  /* Lighter blue for better contrast */
}
```

**Time Badge:**
```css
/* Before */
.time-badge {
    background: rgba(46, 204, 113, 0.15);
    color: rgba(39, 174, 96, 1);  /* Darker green */
}

/* After */
.time-badge {
    background: rgba(46, 204, 113, 0.25);  /* More opaque */
    color: rgba(129, 212, 150, 1);  /* Lighter green for better contrast */
}
```

**Impact:**
- Badges are more visible and readable
- Better contrast ratios for accessibility
- Maintains the color-coding system while being dark-mode friendly

## Color Palette for Dark Mode

### Background Layers (from darkest to lightest):
1. **Base Background**: System dark mode background (automatic)
2. **Section Cards**: `rgba(255, 255, 255, 0.05)` - Very subtle overlay
3. **App Items**: `rgba(255, 255, 255, 0.03)` - Even more subtle
4. **Stat Cards**: Gradient overlays with `0.1` opacity

### Border Colors:
- **Primary Borders**: `rgba(255, 255, 255, 0.08)` - Subtle light lines
- **Hover State**: `rgba(52, 152, 219, 0.1)` - Blue tint

### Text Colors:
- **Primary Text**: Automatic (libadwaita handles this)
- **Dimmed Text**: `opacity: 0.7` class
- **Accent Text** (badges):
  - Blue: `rgba(100, 181, 246, 1)` - Light blue
  - Green: `rgba(129, 212, 150, 1)` - Light green

## Visual Hierarchy in Dark Mode

The layering system creates depth:

```
🌑 Dark Base
├─ 🔲 Section Cards (5% white overlay)
│  ├─ 📋 App Items (3% white overlay)
│  └─ 🏷️ Badges (25% color overlay with bright text)
└─ 📊 Stat Cards (Gradient overlays)
```

## Accessibility Considerations

1. **Contrast Ratios**: All text meets WCAG AA standards
2. **Layering**: Sufficient differentiation between levels
3. **Borders**: Visible but not harsh
4. **Colors**: Enhanced for better visibility in dark mode

## Before vs After

### Before (Mixed Mode):
- ❌ White backgrounds broke dark mode immersion
- ❌ Black borders invisible on dark backgrounds
- ❌ Dark badge text hard to read
- ❌ Inconsistent visual language

### After (True Dark Mode):
- ✅ Consistent dark theme throughout
- ✅ Subtle depth with semi-transparent overlays
- ✅ Bright, readable badge text
- ✅ Cohesive visual experience
- ✅ Professional dark mode aesthetic

## Technical Implementation

All changes are in the CSS provider within `apply_custom_css()` method. The use of `rgba()` with alpha transparency allows:

1. **Adaptability**: Works with different dark mode variants
2. **Consistency**: Maintains relative brightness levels
3. **Performance**: No additional rendering overhead
4. **Maintainability**: Easy to adjust opacity values

## Future Enhancements

Potential improvements for even better dark mode support:

1. **Theme Toggle**: Allow users to switch between light/dark modes
2. **Accent Colors**: User-customizable accent colors
3. **OLED Mode**: Pure black backgrounds for OLED displays
4. **Adaptive Colors**: Extract colors from wallpaper (like GNOME)
5. **High Contrast Mode**: For accessibility

## Testing Checklist

- [x] Section cards visible in dark mode
- [x] App items have sufficient contrast
- [x] Badges are readable
- [x] Borders are visible but subtle
- [x] Stat cards maintain gradient beauty
- [x] No white/light backgrounds
- [x] Hover effects work correctly
- [x] Text is readable everywhere
- [x] Consistent visual hierarchy
- [x] Professional appearance maintained

## Summary

The dark mode improvements ensure that Goalin has a **consistent, professional dark theme throughout the entire application**. By using semi-transparent overlays instead of solid colors, the design:

- Maintains depth and visual hierarchy
- Adapts to different system dark mode implementations
- Provides excellent readability
- Creates a cohesive, immersive experience

The app now truly embraces dark mode, making it comfortable for extended use and visually appealing at any time of day. 🌙✨
