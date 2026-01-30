---
name: coding-standards
description: General coding best practices, input validation, and error handling patterns across languages.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# Coding Standards & Best Practices

## Goal

Establish robust, safe, and maintainable coding practices across all programming languages and contexts.

## 🔒 **Input Validation & Safety**

### Null/Undefined Checking
- **Always validate inputs** before processing
- **Check for null/undefined values** before accessing object properties
- **Use defensive programming** techniques
- **Provide meaningful error messages** when validation fails

### Safe Property Access
```javascript
// ❌ Unsafe - may throw TypeError
const value = obj.property.nestedValue;

// ✅ Safe - with null checking
const value = obj && obj.property && obj.property.nestedValue;

// ✅ Modern - optional chaining
const value = obj?.property?.nestedValue;
```

```python
# ❌ Unsafe - may raise AttributeError
value = obj.property.nested_value

# ✅ Safe - with checking
if obj and hasattr(obj, 'property'):
    value = obj.property.nested_value

# ✅ Modern - with getattr
value = getattr(obj, 'property.nested_value', default_value)
```

## 🛡️ **Error Handling**

### Validation Patterns
- **Validate function parameters** at entry point
- **Check return values** before using them
- **Handle edge cases** explicitly
- **Fail fast and clearly** when something is wrong

### Try-Catch Best Practices
```javascript
// ✅ Specific error handling
try {
  const result = riskyOperation();
  return { success: true, data: result };
} catch (error) {
  console.error(`Operation failed: ${error.message}`);
  return { success: false, error: error.message };
}
```

```python
# ✅ Specific exception handling
try:
    result = risky_operation()
    return {"success": True, "data": result}
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    return {"success": False, "error": str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "error": "Internal error"}
```

## 📊 **Data Structure Patterns**

### Validation Functions
- **Create reusable validators** for common data types
- **Validate at boundaries** (API inputs, function entry)
- **Sanitize external data** before processing
- **Use type checking** where available

### Error Recovery
- **Provide fallback values** for non-critical failures
- **Log errors appropriately** for debugging
- **Graceful degradation** when possible
- **User-friendly error messages**

## 🎯 **Quality Checklist**

Before finalizing any code:

### Input Validation
- [ ] All inputs are validated before use
- [ ] Null/undefined checks are in place
- [ ] Edge cases are handled explicitly
- [ ] Error conditions return meaningful messages

### Error Handling
- [ ] Try-catch blocks around risky operations
- [ ] Specific exception types are caught
- [ ] Errors are logged appropriately
- [ ] Graceful fallbacks are implemented

### Data Safety
- [ ] Object property access is protected
- [ ] Array bounds are checked
- [ ] Type validation is performed
- [ ] External data is sanitized

## 🔄 **Continuous Improvement**

This skill is updated based on:
- Session learnings from conversation analysis
- ACE reflector insights on data quality
- FlightDirector diagnostic patterns
- Proactive improvement suggestions

### Recent Updates

**2026-01-30**: Applied session learnings for input validation
- Enhanced null checking guidelines across languages
- Added safe property access patterns
- Improved error handling best practices
- Integrated validation function patterns

---

*Last Updated: 2026-01-30*
*Version: learning_20260130_004254_coding_standards*