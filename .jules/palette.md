## 2024-05-22 - Keyboard Navigation Deficit
**Learning:** The application lacks standard keyboard shortcuts (e.g., Ctrl+F, Esc) across its custom UI components, forcing mouse usage.
**Action:** Systematically audit and add standard bindings to main interactive loops and list views.

## 2024-05-22 - Favorites Functionality Restoration
**Learning:** Key productivity features like "Favorites" can be lost during refactors if not covered by tests. Users rely on pinning frequently used tools in large lists.
**Action:** When refactoring UI classes, ensure feature parity is maintained. Added persistent Favorites system (load/save/toggle) and updated sorting logic to prioritize pinned items.
