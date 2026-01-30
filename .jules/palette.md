## 2024-05-22 - Keyboard Navigation Deficit
**Learning:** The application lacks standard keyboard shortcuts (e.g., Ctrl+F, Esc) across its custom UI components, forcing mouse usage.
**Action:** Systematically audit and add standard bindings to main interactive loops and list views.

## 2024-05-23 - Immediate Sort Feedback
**Learning:** Re-sorting a list immediately when toggling a favorite provides strong confirmation but causes items to jump, which can be disorienting.
**Action:** Consider delaying sort until next refresh or using animation for reordering in future updates.

## 2024-05-23 - Shadowed Classes in Legacy Code
**Learning:** Duplicate class definitions in large files can lead to applying fixes to the wrong (inactive) code block.
**Action:** Always verify the active class definition by checking the bottom of the file or `__main__` execution block before patching.
