---
description: Mandatory Spec-Driven Test-Driven Development (TDD) Workflow
---

# 🧪 Mandatory Spec-Driven TDD Workflow

**Status**: ⛔ **MANDATORY** - Cannot be bypassed  
**Enforcement**: Automatic validation blocks completion without TDD compliance

This workflow ensures that every functional change is verified by a test before any implementation code is written, with mandatory enforcement gates that cannot be bypassed.

---

## 🚫 **MANDATORY INITIALIZATION VALIDATION**

**Implementation must pass ALL checks before starting**:

```yaml
Implementation_Readiness:
  - Beads_Issue_Exists: false
  - Feature_Branch_Active: false

TDD_Requirements:
  - MANDATORY_TDD_VERIFICATION: true 🔒
  - Has_Benchmarking_Tests: false
  - Has_Performance_Baseline: false
  - Has_Measurable_Assertions: false
  - Has_Speed_Validation: false
  - Has_Memory_Analysis: false
  - Has_Scalability_Testing: false
```

**Blocking Behavior**: Any "false" value → **WORK BLOCKED**

---

## 📋 **1. Specification Phase**

**MANDATORY**: Define the requirements and success criteria in your planning documents.

- Update `ImplementationPlan.md` with the specific feature/bug logic.
- Ensure a Beads ID exists for the task.
- **NEW**: Document baseline performance metrics before any changes.
- **NEW**: Define measurable success criteria (speed, memory, accuracy).

---

## 🔴 **2. Red Phase (Failure)**

**MANDATORY**: Create a test case that reproduces the bug or verifies the new feature.

- **Python**: Add a test in `tests/` (e.g., `tests/test_feature_name.py`).
- **WebUI**: Add a Playwright test in `lightrag_webui/tests/`.
- **NEW**: Add performance benchmark tests with measurable assertions.
- **NEW**: Document current baseline performance in test comments.
- **MANDATORY**: Run the test and confirm it **FAILS**.

```bash
# Python example
pytest tests/test_feature_name.py
# WebUI example
cd lightrag_webui && bunx playwright test tests/test_feature_name.spec.ts
# Performance benchmarks (NEW)
pytest tests/feature_*_benchmarks.py  # Must FAIL in red phase
```

---

## 🟢 **3. Green Phase (Implementation)**

**MANDATORY**: Write the minimum code necessary to make the test pass.

- Focus on the specific task.
- Avoid scope creep.
- **NEW**: Do not modify test expectations to pass tests.
- **NEW**: Implement to meet both functional and performance requirements.

---

## ✅ **4. Verification Phase (Success)**

**MANDATORY**: Run the test again and confirm it **PASSES**.

- Run all related tests to ensure no regressions.
- **NEW**: Run performance benchmarks and validate against baseline.
- **NEW**: Verify all measurable assertions pass.

```bash
# Standard tests
pytest tests/test_feature_name.py
# Performance benchmarks (NEW)
pytest tests/feature_*_benchmarks.py  # Must PASS in green phase
```

---

## 🔄 **5. Refactor Phase**

Clean up the code while keeping the tests passing.

- Improve variable names, structure, and documentation.
- Run tests one last time.
- **NEW**: Re-run performance benchmarks to ensure no regression.
- **NEW**: Update performance documentation if behavior changes.

---

## 📊 **6. Audit Phase (Performance Analysis)**

**MANDATORY**: For all features (not just LLM-specific):

- **LLM Features**: Run the relevant benchmark/audit script.
- **Performance Features**: Execute comprehensive benchmarking suite.
- **ALL Features**: Document speed-accuracy tradeoffs in `walkthrough.md`.
- **NEW**: Quantify performance impacts with measurable metrics.

---

## 🚪 **7. Quality Gate Validation**

**MANDATORY**: Cannot complete session without passing ALL gates:

```yaml
TDD_Completion_Gate:
  Required_Artifacts:
    - Failing_Tests_Before_Implementation: true
    - Passing_Tests_After_Implementation: true
    - Performance_Benchmarks: true
    - Baseline_Comparisons: true
    - Tradeoff_Documentation: true
    - Measurable_Metrics: true

  Validation_Methods:
    - Automated_Test_Execution: pytest coverage
    - Performance_Measurement: benchmark suite results
    - Documentation_Review: tradeoff analysis completeness
    - Code_Review: TDD compliance verification
```

**Blocking Behavior**: Missing artifacts → **SESSION INCOMPLETE**

---

## 🛡️ **ENFORCEMENT MECHANISMS**

### **System-Level Enforcement**

```python
def validate_tdd_compliance(feature_name):
    """Automatic TDD validation - CANNOT BYPASS"""
    tdd_requirements = {
        'failing_tests_exist': check_failing_tests(feature_name),
        'baseline_measured': check_baseline_documented(feature_name),
        'performance_assertions': check_performance_assertions(feature_name),
        'benchmarks_exist': check_benchmark_tests(feature_name),
        'tradeoffs_analyzed': check_tradeoff_documentation(feature_name)
    }

    if not all(tdd_requirements.values()):
        block_work_with_tdd_violation(tdd_requirements)

    return tdd_requirements
```

### **Session Completion Validation**

```python
def validate_session_tdd_compliance():
    """Session completion validation - CANNOT PROCEED WITHOUT"""
    # Check git history for TDD compliance
    commits = get_feature_commits()
    tdd_timeline = validate_tdd_timeline(commits)

    # Check required artifacts exist
    required_artifacts = [
        'tests/feature_*_tdd.py',           # Failing tests first
        'tests/feature_*_benchmarks.py',        # Performance benchmarks
        'docs/feature_*_tradeoffs.md',        # Tradeoff analysis
        'tests/feature_*_functional.py'       # Passing tests after
    ]

    missing_artifacts = [artifact for artifact in required_artifacts
                       if not file_exists(artifact)]

    if missing_artifacts:
        block_session_completion(missing_artifacts, tdd_timeline)

    return True
```

---

## 📈 **PERFORMANCE REQUIREMENTS**

### **All Features Must Include**

1. **Baseline Measurements**: Document current system performance
2. **Speed Assertions**: Minimum % improvement or acceptable degradation limits
3. **Memory Assertions**: Maximum overhead thresholds
4. **Scalability Assertions**: Degradation limits under load
5. **Tradeoff Analysis**: Quantified speed vs resource analysis

### **Benchmark Categories**

- **Functional Tests**: Verify correct behavior
- **Performance Tests**: Measure speed, memory, and scalability
- **Integration Tests**: Validate real-world usage scenarios
- **Regression Tests**: Ensure no performance degradation

---

## 🚨 **VIOLATION CONSEQUENCES**

### **Automatic Blocks**

- **Work Cannot Start**: Initialization gate blocks non-compliant implementations
- **Session Cannot Complete**: Quality gate blocks incomplete TDD
- **Deployment Blocked**: Quality checks prevent non-validated features
- **Merge Rejected**: Quality checks fail without TDD evidence

### **No Override Process**

```python
# THERE IS NO MANUAL OVERRIDE FOR TDD GATES
def attempt_tdd_override(reason: str):
    """IMPOSSIBLE FUNCTION - Always blocks"""
    raise TDDEnforcementError(
        f"TDD override attempted: {reason}. " +
        "TDD compliance is MANDATORY and CANNOT be bypassed. " +
        "Follow the TDD process or work cannot proceed.",
        override_impossible=True
    )
```

---

## 🔐 **SECURITY & COMPLIANCE**

### **Audit Trail**

- **All TDD Decisions Logged**: Immutable audit trail
- **Bypass Attempts Recorded**: Security violations tracked
- **Compliance Reports**: Regular TDD adherence reporting
- **Training Records**: TDD process education tracked

---

**🔒 ENFORCEMENT STATEMENT**
TDD compliance is **MANDATORY** for all development. These gates **CANNOT** be bypassed, overridden, or skipped. Any attempt to bypass TDD requirements will be **automatically blocked** and logged as a security violation. **This is not a guideline - this is a requirement.**

---

**⚠️ LAST UPDATED**: 2026-02-06  
**🔄 REVIEW CYCLE**: Quarterly or when violations occur  
**👮 APPROVAL**: Global Technical Standards Board
