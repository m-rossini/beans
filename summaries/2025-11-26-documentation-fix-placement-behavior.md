# Documentation Fix: Placement Algorithm Failure Behavior

## Overview

Fixed documentation inconsistency where the flowchart diagrams incorrectly stated that the placement algorithm raises `ValueError` on failure, when the actual implementation returns an empty list.

## Problem

The placement algorithm diagrams in `2025-11-26-placement-algorithm-diagrams.md` showed:
- "Raise ValueError" when `_can_fit` returns False
- "Raise ValueError" when the 90% placement threshold fails
- "ValueError on Failed Threshold" in the output subgraph

However, the actual implementation in `src/beans/placement.py` returns an empty list `[]` in both failure cases (lines 87 and 118).

## Solution

Updated three locations in the flowchart documentation:
1. **Line 24**: Changed "ValueError on Failed Threshold" to "Empty List on Failed Threshold"
2. **Line 55**: Changed "Raise ValueError<br/>impossible to fit" to "Return []<br/>impossible to fit"
3. **Line 73**: Changed "Raise ValueError<br/>90% threshold failed" to "Return []<br/>90% threshold failed"

## Key Design Decision

The implementation uses empty list returns rather than exceptions for these cases because:
- Returning an empty list allows callers to gracefully handle "no placement possible" scenarios
- It follows the pattern of returning a valid (but empty) result rather than raising exceptions for expected edge cases
- This is consistent with how count ≤ 0 is already handled (line 83)

## Verification

The fix was verified by comparing the documentation with the actual code behavior in `RandomPlacementStrategy.place()`:
- Lines 85-87: Returns `[]` when `_can_fit()` fails
- Lines 116-118: Returns `[]` when less than 90% of sprites are placed

## Files Changed

- `summaries/2025-11-26-placement-algorithm-diagrams.md`: Updated flowchart labels
