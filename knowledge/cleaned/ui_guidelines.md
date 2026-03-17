--- title: UI Guidelines and Design System category: Design last_updated: 2026-02-27 version: 2.0 tags: ["css", "colors", "typography", "accessibility", "rtl"] ai_tool_owner: Cursor ---
# UI Guidelines and Design System

**Last Updated:** 2026-02-27 **Design System Version:** 2.0 **Scope:** Web and Mobile Interfaces

## Color Palette

### Primary Colors

- **Primary Blue:** `#0066CC` (var(--color-primary-blue)) - Main CTA buttons, links - **Primary Dark:** `#004299` (var(--color-primary-dark)) - Hover states - **Primary Light:** `#E6F2FF` (var(--color-primary-light))- Background tints

### Status Colors (Semantic)

- **Success Green:** `#27AE60` (var(--color-status-success)) - Completed tasks - **Warning Orange:** `#F39C12` (var(--color-status-warning)) - In progress, pending actions - **Error Red:** `#E74C3C` (var(--color-status-error)) - Blocked, failed operations - **Info Cyan:** `#3498DB` (var(--color-status-info)) - Information messages - **Neutral Gray:** `#95A5A6` (var(--color-status-neutral)) - Disabled, secondary content

**Accessibility Requirement:** All color combinations must maintain minimum WCAG AA contrast ratio of 4.5:1. Verified on 2026-02-15. Updated color palette on 2026-02-26 after accessibility audit.

## Typography

### Font Family

- **Primary:** Inter (sans-serif) - Available via Google Fonts - **Monospace:** JetBrains Mono - Used for code snippets and debugging information

### Font Scales

| Element | Size | Weight | Line Height | |---------|------|--------|-------------| | H1 | 32px | 700 | 40px | | H2 | 24px | 700 | 32px | | H3 | 20px | 600 | 28px | | Body | 16px | 400 | 24px | | Small | 14px | 400 | 20px | | Tiny | 12px | 400 | 16px |

## Responsive Design Breakpoints

``` Mobile (xs): 0px - 480px Tablet (sm): 481px - 768px Desktop (md): 769px - 1024px Large (lg): 1025px - 1440px XLarge (xl): 1441px+ ```

Minimum viewport width: 360px. Tested on iPhone SE (2020) and older Android devices. Last validation: 2026-02-20.

## Right-to-Left (RTL) Support

### Implementation Status

**Status:** Completed (2026-02-10) **Supported Languages:** Arabic, Hebrew, Persian **Testing:** Conducted manual testing with native speakers on 2026-02-12

### RTL Guidelines

- All margins, paddings, and positioning must use logical properties - Text alignment automatically reversed via CSS flexbox - Task order in lists maintains visual LTR to RTL flow - Date/time formats adjusted per locale (RTL does not reverse numbers) - Form field labels positioned on left side of input for RTL

### CSS Implementation

```css direction: rtl; text-align: right; margin-inline-start: 16px; margin-inline-end: 0; flex-direction: row-reverse; ```

Automated testing implemented via Storybook with RTL viewport on 2026-02-10. All components must pass RTL visual regression tests before merge.

## Component Library Standards

### Button Component

**Variants:** Primary, Secondary, Danger, Ghost **Sizes:** Small (32px), Medium (40px), Large (48px) **States:** Default, Hover, Active, Disabled, Loading

Minimum touch target: 44x44px for mobile accessibility (WCAG 2.1 - Level AAA).

### Input Fields

- **Height:** 40px (medium size, matches button height) - **Padding:** 12px horizontal, 8px vertical - **Border:** 1px solid `#CCCCCC`, changes to `#0066CC` on focus - **Placeholder Text:** `#999999` with font-weight 400 - **Validation:** Error state red border + error message below input

### Modal Dialogs

- **Backdrop:** Semi-transparent black (`#000000` with 60% opacity) - **Width:** 90% on mobile, 520px on desktop, max-width 95vw - **Border Radius:** 8px - **Shadow:** Elevated shadow on 2026-02-01 (changed from flat design) - **Animation:** Fade in (200ms cubic-bezier), slide up on mobile

### Task Cards

**Layout changes (2026-02-18):** - Moved priority indicator from right side to left edge as vertical bar - Added hover effect (background lighten to `#F8F8F8`) - Ellipsis menu relocated from top-right to bottom-right - Added completion progress bar for tasks with subtasks

## Internationalization (i18n)

### Supported Languages

- English (en-US) - Default - Spanish (es-ES) - Added 2026-01-20 - French (fr-FR) - Added 2026-02-01 - German (de-DE) - Added 2026-02-15 - Japanese (ja-JP) - Added 2026-02-20 - Arabic (ar-SA) - In Progress (completion target: 2026-03-15)

### Translation Requirements

All user-facing strings must be externalized into translation files. Variable substitution must use named parameters `{userName}` not positional. String length budget must account for 30% expansion (especially important for German).

## Animation Guidelines

### Transitions

- **Button interactions:** 150ms ease-in-out - **Modal appearance:** 200ms ease-out - **Task state changes:** 300ms ease-in - **Page navigation:** 400ms fade transition

All animations must be reducible via `prefers-reduced-motion` media query.

### Loading States

Loading spinners should display after 300ms to avoid flickering. Skeleton screens preferred for content areas over spinners. Last design decision: 2026-02-19.

## Dark Mode

**Status:** In Requirements Phase (target launch: 2026-04-01) **Implementation:** CSS custom properties with system preference detection **Brand Colors:** Will be adjusted for WCAG AAA compliance in low-light environments

Preliminary palette under review as of 2026-02-25.

## Accessibility Standards

- WCAG 2.1 Level AA compliance (minimum requirement) - Screen reader testing with NVDA and JAWS - Keyboard navigation support (tab order critical) - Focus indicators must be visible (min 2px, high contrast) - Alt text for all images with meaningful context - Aria labels for interactive elements without visible text

Accessibility audit performed: 2026-02-15. Critical issues resolved by 2026-02-22. Remaining items scheduled for next sprint.