# Internationalization (i18n)

## Metadata

- **ID**: cursor-instruction-006
- **Type**: instruction
- **Source**: Cursor
- **Date**: 2026-01-20
- **File**: ui_guidelines.md
- **Chunk**: 2/2
- **Words**: 243
- **Topics**: Internationalization (i18n), Animation Guidelines, Dark Mode, Accessibility Standards, testing, task, user

## Content

## Internationalization (i18n)

### Supported Languages

- English (en-US) - Default - Spanish (es-ES) - Added 2026-01-20 - French (fr-FR) - Added 2026-02-01 - German (de-DE) - Added 2026-02-15 - Japanese (ja-JP) - Added 2026-02-20 - Arabic (ar-SA) - In Progress (completion target: 2026-03-15)

### Translation Requirements

All user-facing strings must be externalized into translation files. Variable substitution must use named parameters `{userName}` not positional. String length budget must account for 30% expansion (especially important for German).


## Animation Guidelines

### Transitions

- Button interactions: 150ms ease-in-out - Modal appearance: 200ms ease-out - Task state changes: 300ms ease-in - Page navigation: 400ms fade transition

All animations must be reducible via `prefers-reduced-motion` media query.

### Loading States

Loading spinners should display after 300ms to avoid flickering. Skeleton screens preferred for content areas over spinners. Last design decision: 2026-02-19.


## Dark Mode

Status: In Requirements Phase (target launch: 2026-04-01) Implementation: CSS custom properties with system preference detection Brand Colors: Will be adjusted for WCAG AAA compliance in low-light environments

Preliminary palette under review as of 2026-02-25.


## Accessibility Standards

- WCAG 2.1 Level AA compliance (minimum requirement) - Screen reader testing with NVDA and JAWS - Keyboard navigation support (tab order critical) - Focus indicators must be visible (min 2px, high contrast) - Alt text for all images with meaningful context - Aria labels for interactive elements without visible text

Accessibility audit performed: 2026-02-15. Critical issues resolved by 2026-02-22. Remaining items scheduled for next sprint.