## 2026-01-30 - [Data Loss] Empty Archive Conversion
**Erreur :** Original CBR files were deleted after being "converted" to empty CBZ files when extraction failed silently (or yielded no files).
**Cause :** The `convert_cbr` function relied on the lack of exceptions from `utils.extract_with_7za` and `zipfile` to assume success. It did not verify that any content was actually processed.
**Prévention :** Implement "Output Validation" pattern: explicitly check that the output artifact contains expected data (e.g., `file_count > 0`) before returning success, especially when the operation is part of a destructive pipeline (delete original).
