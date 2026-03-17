# Color Palette

## Metadata

- **ID**: cursor-instruction-005
- **Type**: instruction
- **Source**: Cursor
- **Date**: 2026-02-15
- **File**: ui_guidelines.md
- **Chunk**: 1/2
- **Words**: 426
- **Topics**: Color Palette, Typography, Responsive Design Breakpoints, Right-to-Left (RTL) Support, Component Library Standards, testing, task

## Content

## Color Palette

### Primary Colors

- Primary Blue: `#0066CC` (var(--color-primary-blue)) - Main CTA buttons, links - Primary Dark: `#004299` (var(--color-primary-dark)) - Hover states - Primary Light: `#E6F2FF` (var(--color-primary-light))- Background tints

### Status Colors (Semantic)

- Success Green: `#27AE60` (var(--color-status-success)) - Completed tasks - Warning Orange: `#F39C12` (var(--color-status-warning)) - In progress, pending actions - Error Red: `#E74C3C` (var(--color-status-error)) - Blocked, failed operations - Info Cyan: `#3498DB` (var(--color-status-info)) - Information messages - Neutral Gray: `#95A5A6` (var(--color-status-neutral)) - Disabled, secondary content

Accessibility Requirement: All color combinations must maintain minimum WCAG AA contrast ratio of 4.5:1. Verified on 2026-02-15. Updated color palette on 2026-02-26 after accessibility audit.


## Typography

### Font Family

- Primary: Inter (sans-serif) - Available via Google Fonts - Monospace: JetBrains Mono - Used for code snippets and debugging information

### Font Scales


## Responsive Design Breakpoints

Minimum viewport width: 360px. Tested on iPhone SE (2020) and older Android devices. Last validation: 2026-02-20.


## Right-to-Left (RTL) Support

### Implementation Status

Status: Completed (2026-02-10) Supported Languages: Arabic, Hebrew, Persian Testing: Conducted manual testing with native speakers on 2026-02-12

### RTL Guidelines

- All margins, paddings, and positioning must use logical properties - Text alignment automatically reversed via CSS flexbox - Task order in lists maintains visual LTR to RTL flow - Date/time formats adjusted per locale (RTL does not reverse numbers) - Form field labels positioned on left side of input for RTL

### CSS Implementation

Automated testing implemented via Storybook with RTL viewport on 2026-02-10. All components must pass RTL visual regression tests before merge.


## Component Library Standards

### Button Component

Variants: Primary, Secondary, Danger, Ghost Sizes: Small (32px), Medium (40px), Large (48px) States: Default, Hover, Active, Disabled, Loading

Minimum touch target: 44x44px for mobile accessibility (WCAG 2.1 - Level AAA).

### Input Fields

- Height: 40px (medium size, matches button height) - Padding: 12px horizontal, 8px vertical - Border: 1px solid `#CCCCCC`, changes to `#0066CC` on focus - Placeholder Text: `#999999` with font-weight 400 - Validation: Error state red border + error message below input

### Modal Dialogs

- Backdrop: Semi-transparent black (`#000000` with 60% opacity) - Width: 90% on mobile, 520px on desktop, max-width 95vw - Border Radius: 8px - Shadow: Elevated shadow on 2026-02-01 (changed from flat design) - Animation: Fade in (200ms cubic-bezier), slide up on mobile

### Task Cards

Layout changes (2026-02-18): - Moved priority indicator from right side to left edge as vertical bar - Added hover effect (background lighten to `#F8F8F8`) - Ellipsis menu relocated from top-right to bottom-right - Added completion progress bar for tasks with subtasks
