---
name: ui
description: >
  Manages the LightRAG web interface, including WebUI development, frontend
  builds, deployment, accessibility testing, and UX performance optimisation.
  Use when developing or deploying the WebUI, running frontend tests,
  analysing page performance, or managing UI deployments across environments.
  Do NOT use for backend API development or for tasks unrelated to the
  LightRAG frontend application.
compatibility: >
  Requires Node.js with npm for frontend builds (cd lightrag_webui && npm
  run dev/build). Python 3.x scripts for deployment and testing live in
  ~/.gemini/antigravity/skills/ui/scripts/.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: frontend
  tags: [ui, webui, frontend, deployment, accessibility, performance]
---

# 🌐 UI Skill

**Purpose**: Manages LightRAG web interface, including development, deployment, testing, and user experience optimization.

## 🎯 Mission

- Develop and maintain WebUI components
- Manage frontend build and deployment
- Coordinate user interface testing
- Optimize user experience and accessibility

## 🛠️ Tools & Scripts

### WebUI Development

```bash
# Start development server
cd lightrag_webui && npm run dev

# Build for production
cd lightrag_webui && npm run build

# Run frontend linting
cd lightrag_webui && npm run lint
```

### UI Testing

```bash
# Run UI tests
python3 scripts/run_ui_tests.py

# Run accessibility tests
python3 scripts/accessibility_test.py --full-suite

# Visual regression testing
python3 scripts/visual_regression.py --baseline latest
```

### Deployment Management

```bash
# Deploy to staging
python3 scripts/deploy_ui.py --environment staging

# Deploy to production
python3 scripts/deploy_ui.py --environment production --confirm

# Rollback UI deployment
python3 scripts/rollback_ui.py --version previous
```

### Performance Optimization

```bash
# Analyze UI performance
python3 scripts/ui_performance.py --analyze --report

# Optimize bundle size
python3 scripts/optimize_bundle.py --target production

# Run Core Web Vitals tests
python3 scripts/web_vitals.py --site production
```

## 📋 Usage Examples

### Basic UI Management

```bash
# Start development environment
/ui --dev-server

# Build for production
/ui --build --production

# Run UI tests
/ui --test --full-suite
```

### Deployment Operations

```bash
# Deploy to specific environment
/ui --deploy --environment staging

# Check deployment status
/ui --deployment-status --environment production

# Rollback deployment
/ui --rollback --confirm --reason "critical_bug"
```

### Performance and UX

```bash
# Analyze performance metrics
/ui --performance --analyze --report detailed

# Run accessibility audit
/ui --accessibility --standard wcag

# Optimize user experience
/ui --optimize-ux --focus mobile
```

## 🔗 Integration Points

- **API Layer**: Frontend-backend communication
- **Graph Skill**: Display graph visualizations
- **Documentation Skill**: Interactive documentation viewer
- **Testing Skill**: UI test coordination

## 📊 Metrics Tracked

- Page load times and Core Web Vitals
- User interaction success rates
- Accessibility compliance scores
- Bundle size and performance metrics

## 🎯 Key Files

- `lightrag_webui/` - Frontend application
- `scripts/deploy_ui.py` - Deployment orchestration
- `tests/ui/` - UI test suite
- `ui_assets/` - Static assets and build outputs
