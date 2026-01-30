---
name: javascript
description: JavaScript coding standards, best practices, and guidelines for web development.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# JavaScript Development Standards

## Goal

Ensure consistent, modern, and maintainable JavaScript code across all projects and interactions.

## Core Principles

- **Modern ES6+ Syntax**: Use modern JavaScript features (const/let, arrow functions, destructuring)
- **Vanilla JavaScript Priority**: Prefer vanilla JS over jQuery for simple DOM operations
- **Safety First**: Always validate inputs and check for null/undefined values
- **Performance Conscious**: Write efficient code with proper event handling and memory management

## 🚫 **Avoidance Rules**

### Variable Declarations
- **Never use `var`** for variable declarations
- **Always use `const`** for variables that won't be reassigned
- **Use `let`** only for variables that need reassignment

### jQuery Usage
- **Avoid jQuery** for simple DOM manipulations
- **Prefer vanilla JavaScript** `querySelector`, `addEventListener`, etc.
- **Only use jQuery** when absolutely necessary for legacy compatibility

## ✅ **Best Practices**

### Input Validation
- **Always check for null values** before accessing object properties
- **Validate function parameters** at the start of functions
- **Use optional chaining** (`?.`) for safe property access
- **Provide default values** for optional parameters

### Code Organization
- **Use modules** and proper imports/exports
- **Group related functionality** in logical units
- **Keep functions small** and focused on single responsibilities
- **Use descriptive names** for variables and functions

### Error Handling
- **Use try-catch blocks** for potentially error-prone operations
- **Provide meaningful error messages** for debugging
- **Handle promises properly** with async/await or .then/.catch
- **Validate API responses** before processing

## 🔧 **Tool Usage Guidelines**

### DOM Manipulation
- **Prefer**: `document.querySelector()`, `document.createElement()`
- **Avoid**: `document.all`, `innerHTML` for complex content
- **Use event delegation** for dynamic elements

### Asynchronous Operations
- **Use async/await** over Promise chains when possible
- **Handle promise rejections** properly
- **Use proper error boundaries** in React/async contexts

## 📋 **Common Patterns**

### Safe Property Access
```javascript
// ❌ Bad - may throw error
const value = obj.property.nestedProperty;

// ✅ Good - safe access
const value = obj?.property?.nestedProperty;
const value = obj && obj.property && obj.property.nestedProperty;
```

### Event Handling
```javascript
// ❌ Bad - memory leak risk
element.addEventListener('click', handlerFunction);

// ✅ Good - proper cleanup
const handler = (e) => { /* handle click */ };
element.addEventListener('click', handler);
// Later: element.removeEventListener('click', handler);
```

### Module Pattern
```javascript
// ✅ Preferred - ES6 modules
export const utilityFunction = () => { /* logic */ };
export const CONSTANT_VALUE = 'value';

import { utilityFunction, CONSTANT_VALUE } from './utilities.js';
```

## 🎯 **Performance Considerations**

- **Minimize DOM manipulation** - batch updates when possible
- **Use event delegation** for dynamic content
- **Avoid layout thrashing** - read DOM, then write, don't interleave
- **Use appropriate data structures** - Map/Set for lookups, arrays for iteration
- **Debounce expensive operations** like resize handlers or API calls

## 🔍 **Quality Checklist**

Before finalizing JavaScript code:

- [ ] No `var` declarations
- [ ] All jQuery usage justified and documented
- [ ] Null checks implemented for object property access
- [ ] Error handling in place for async operations
- [ ] Event listeners properly managed (add/remove)
- [ ] Modern syntax used consistently
- [ ] Code is well-commented where complex
- [ ] Performance implications considered

## 📚 **Learning History**

This skill is continuously updated based on session learnings and ACE integration.

### Recent Updates

**2026-01-30**: Applied session learnings from conversation analysis
- Added variable declaration standards (const/let over var)
- Implemented vanilla JavaScript preference over jQuery
- Enhanced input validation with null checking guidelines

---

*Last Updated: 2026-01-30*
*Version: learning_20260130_004254_javascript*