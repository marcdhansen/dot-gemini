---
name: TDD
description: Test-Driven Development best practices for all code changes
---

# 🧪 TDD (Test-Driven Development) Skill

> **Purpose**: Enforce test-first development for all code changes  
> **Invocation**: Automatically invoked for implementation work, manually via `/tdd`  
> **Scope**: All code changes, not just SOP modifications

## When to Use This Skill

Use this skill when:

- Adding new features or functionality
- Fixing bugs
- Modifying existing code behavior
- Adding performance optimizations
- Implementing validation logic

**Do NOT use** for:

- Documentation-only changes (unless modifying code examples)
- Configuration changes that don't affect logic
- Metadata updates (README, comments)

---

## TDD Cycle: Red-Green-Refactor

### 🔴 Red Phase: Write Failing Tests First

**Before writing ANY implementation code**:

1. **Define Expected Behavior**
   - What should the code do?
   - What inputs are valid/invalid?
   - What outputs are expected?

2. **Write the Test**

   ```python
   def test_feature_behavior():
       # Arrange: Set up test data
       input_data = create_test_data()
       
       # Act: Call the code that doesn't exist yet
       result = new_feature(input_data)
       
       # Assert: Verify expected behavior
       assert result == expected_output
   ```

3. **Run the Test**

   ```bash
   pytest tests/test_new_feature.py -v
   ```

   **Expected**: ❌ **Test MUST FAIL** (function doesn't exist yet)

4. **Verify Failure Reason**
   - Should fail because function doesn't exist
   - NOT because test logic is wrong
   - NOT because assertions are incorrect

5. **🔒 GATE CHECK: Verify Before Proceeding**
   
   **CRITICAL**: After writing failing tests, RUN THIS CHECK before writing ANY implementation:
   
   ```bash
   # Check git timestamps - tests MUST be newer than implementation
   git log -1 --format="%ci" -- tests/ && git log -1 --format="%ci" -- src/
   
   # Or use this one-liner to verify:
   echo "Tests:"; git log -1 --format="%h %s" -- tests/; echo "Src:"; git log -1 --format="%h %s" -- src/
   ```
   
   **If implementation commit is newer than test commit** → ❌ **BLOCKED**
   - You wrote implementation BEFORE tests - this is a TDD violation
   - Fix: Create proper test-first workflow:
     1. `git stash` (save implementation)
     2. Write failing tests
     3. `git add tests/ && git commit -m "test: add failing tests for [feature]"`
     4. `git stash pop` (restore implementation)
     5. Make tests pass
   
   **The SOP now enforces this with `validate_tdd_timestamps` validator in Execution phase**

---

### 🟢 Green Phase: Implement Minimum Code

**Write the simplest code that makes the test pass**:

1. **Implement the Feature**

   ```python
   def new_feature(input_data):
       # Minimum code to pass the test
       return process(input_data)
   ```

2. **Run the Test Again**

   ```bash
   pytest tests/test_new_feature.py -v
   ```

   **Expected**: ✅ **Test MUST PASS**

3. **Resist Over-Engineering**
   - Don't add features not covered by tests
   - Don't optimize prematurely
   - Don't add "nice to have" extras

---

### 🔄 Refactor Phase: Improve Code Quality

**Clean up implementation while keeping tests green**:

1. **Improve Code**
   - Extract functions for clarity
   - Improve variable names
   - Remove duplication
   - Add documentation

2. **Run Tests After Each Change**

   ```bash
   pytest tests/test_new_feature.py -v
   ```

   **Expected**: ✅ **Tests STILL PASS**

3. **Stop When Clean**
   - Code is readable
   - No obvious duplication
   - Tests remain green

---

## Test Categories

### 1. Positive Tests (Happy Path)

**Purpose**: Verify code works with valid inputs

```python
def test_valid_input_returns_success():
    result = process_data(valid_input)
    assert result.success is True
```

---

### 2. Negative Tests (Error Cases)

**Purpose**: Verify code handles invalid inputs correctly

```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError):
        process_data(invalid_input)
```

---

### 3. Edge Case Tests

**Purpose**: Verify boundary conditions and corner cases

```python
def test_empty_input_handled():
    result = process_data([])
    assert result == default_value

def test_max_size_input():
    huge_input = create_max_size_input()
    result = process_data(huge_input)
    assert result is not None
```

---

### 4. Regression Tests

**Purpose**: Prevent re-introduction of fixed bugs

```python
def test_bug_123_fixed():
    """Regression test for issue #123: crash on null input"""
    result = process_data(None)
    assert result == handle_null_gracefully()
```

---

## Loophole Analysis

When writing tests, explicitly consider and close loopholes:

### Example: Authentication Check

**Rule**: "Users must be authenticated"

**Loopholes to Test**:

```python
def test_unauthenticated_user_blocked():
    # Direct loophole: No auth token
    with pytest.raises(Unauthorized):
        access_resource(auth_token=None)

def test_expired_token_blocked():
    # Time loophole: Expired token
    expired_token = create_expired_token()
    with pytest.raises(Unauthorized):
        access_resource(auth_token=expired_token)

def test_invalid_signature_blocked():
    # Crypto loophole: Tampered token
    tampered_token = create_tampered_token()
    with pytest.raises(Unauthorized):
        access_resource(auth_token=tampered_token)

def test_revoked_token_blocked():
    # State loophole: Revoked but not expired
    revoked_token = create_revoked_token()
    with pytest.raises(Unauthorized):
        access_resource(auth_token=revoked_token)
```

**Loophole Analysis Documentation**:

- Identify potential workarounds
- Create tests that close each loophole
- Document why each test exists

---

## Performance Testing

For features with performance requirements:

```python
import time

def test_feature_performance():
    """Verify feature completes within acceptable time."""
    start = time.perf_counter()
    
    result = expensive_operation(large_dataset)
    
    duration = time.perf_counter() - start
    
    # Performance assertion
    assert duration < 1.0, f"Operation too slow: {duration}s"
    assert result.is_valid()
```

**Include**:

- Baseline measurements (current performance)
- Target performance metrics
- Acceptable degradation limits
- Memory usage constraints

---

## Quality Gates

Before considering work complete:

- [ ] **All tests written BEFORE implementation**
- [ ] **All tests initially FAILED (red phase documented)**
- [ ] **All tests now PASS (green phase verified)**
- [ ] **Code refactored for clarity**
- [ ] **Edge cases covered**
- [ ] **Loopholes identified and closed**
- [ ] **Performance requirements met (if applicable)**
- [ ] **Regression tests added (for bug fixes)**

---

## Examples

### Example 1: Bug Fix with TDD

**Bug**: Application crashes on empty string input

**🔴 Red Phase**:

```python
def test_empty_string_handled():
    """Bug fix: crashes on empty string"""
    result = parse_input("")
    assert result == default_value  # FAILS: crashes currently
```

**🟢 Green Phase**:

```python
def parse_input(data):
    if not data:
        return default_value
    return process(data)
```

**✅ Refactor Phase**:

```python
def parse_input(data: str) -> ParsedData:
    """Parse input string with empty string handling."""
    if not data:
        logger.debug("Empty input received, using default")
        return default_value
    return process(data)
```

---

### Example 2: New Feature with TDD

**Feature**: Add user role validation

**🔴 Red Phase**:

```python
def test_admin_role_has_access():
    user = User(role="admin")
    assert can_access_resource(user, "admin_panel") is True

def test_regular_user_denied():
    user = User(role="user")
    assert can_access_resource(user, "admin_panel") is False
```

**🟢 Green Phase**:

```python
def can_access_resource(user, resource):
    if resource == "admin_panel":
        return user.role == "admin"
    return True
```

**✅ Refactor Phase**:

```python
ROLE_PERMISSIONS = {
    "admin": ["admin_panel", "user_panel", "reports"],
    "user": ["user_panel"]
}

def can_access_resource(user: User, resource: str) -> bool:
    """Check if user role has access to resource."""
    allowed_resources = ROLE_PERMISSIONS.get(user.role, [])
    return resource in allowed_resources
```

---

## Integration with Other Skills

This skill is invoked by:

- **`/sop-modification`**: When modifying SOP gates
- **`/planning`**: During implementation planning
- **Orchestrator**: Automatically during execution phase

---

## Common Anti-Patterns to Avoid

### ❌ Don't: Write implementation first, tests later

```python
# BAD: Code already exists
def feature():
    return "implemented"

# Tests written after the fact don't catch design issues
def test_feature():
    assert feature() == "implemented"  # Not true TDD
```

### ✅ Do: Write test first, implementation second

```python
# GOOD: Test defines expected behavior
def test_feature():
    assert feature() == "expected"  # Fails initially

# Implementation driven by test
def feature():
    return "expected"  # Makes test pass
```

---

### ❌ Don't: Change test to make it pass

```python
# BAD: Modifying test expectations to match buggy code
def test_division():
    assert divide(10, 0) == None  # Changed from proper error handling
```

### ✅ Do: Fix implementation to meet test expectations

```python
# GOOD: Test stays strict, implementation improved
def test_division():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
```

---

## Enforcement

The Orchestrator validates TDD compliance during finalization:

- Evidence of failing tests (red phase)
- Evidence of passing tests (green phase)
- Test-to-code timestamp verification (tests before implementation)

**No bypass**: TDD compliance is mandatory for all implementation work.

---

**Related Skills**:

- `/sop-modification`: Specializes TDD for SOP gates
- `/planning`: Uses TDD during implementation planning

**See Also**:

- [SOP TDD Workflow](~/.agent/docs/sop/tdd-workflow.md)
- [Orchestrator TDD Validation](~/.gemini/antigravity/skills/Orchestrator/SKILL.md)
