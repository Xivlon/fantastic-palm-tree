# Dependency Triage and Management Guide

This document provides comprehensive guidance for managing dependency updates in the Fantastic Palm Tree project, with focus on security, stability, and maintainability.

## Overview

The project uses an automated dependency triage system that:
- **Classifies updates** by type (patch/minor/major)
- **Groups updates** to reduce PR fatigue
- **Automates security scans** and vulnerability detection
- **Provides review guidance** for major updates
- **Enables canary deployments** for high-risk changes

## Dependency Update Classification

### Update Types

- **Patch Updates** (e.g., 1.2.3 → 1.2.4)
  - Bug fixes and security patches
  - Low risk, can often be auto-merged
  - Should not introduce breaking changes

- **Minor Updates** (e.g., 1.2.0 → 1.3.0)
  - New features, enhancements
  - Medium risk, review recommended
  - Should maintain backward compatibility

- **Major Updates** (e.g., 1.x.x → 2.0.0)
  - Breaking changes, major architecture changes
  - High risk, requires thorough review
  - May require code changes and migration

### Ecosystem-Specific Considerations

#### Python Dependencies
- **Core Data Science**: pandas, numpy, matplotlib
  - High impact on computational accuracy
  - Test numerical results thoroughly
- **Web Framework**: fastapi, pydantic, uvicorn
  - API compatibility critical
  - Verify schema validation works
- **Development Tools**: pytest, black, mypy
  - Lower risk but may affect CI/CD

#### Node.js Dependencies
- **Framework**: Next.js, React
  - High impact on frontend functionality
  - Check migration guides for major updates
- **UI Libraries**: recharts, lucide-react
  - Medium impact on user interface
- **Development Tools**: TypeScript, ESLint
  - May affect build process

## Automated Dependency Management

### Dependabot Configuration

Our `.github/dependabot.yml` configuration includes:

```yaml
# Grouped updates to reduce PR fatigue
groups:
  # Core dependencies (patch/minor only)
  core-dependencies:
    patterns: ["pandas*", "numpy*", "matplotlib*", "pydantic*"]
    update-types: ["patch", "minor"]
  
  # Security updates (all packages)
  security-updates:
    patterns: ["*"]
    update-types: ["security-update"]
```

### Security Update Grouping

Security updates are automatically grouped and prioritized:
- **Critical**: Applied within 24 hours
- **High**: Applied within 1 week
- **Medium**: Applied within 1 month
- **Low**: Next regular update cycle

## Review Process

### Automated Review (Patch/Minor)

For patch and minor updates in approved groups:
1. ✅ Automated security scan passes
2. ✅ All CI tests pass
3. ✅ No breaking changes detected
4. → **Auto-approve** and merge

### Manual Review (Major Updates)

For major updates, follow this process:

#### 1. Initial Assessment
```bash
# Use our dependency triage tool
./scripts/dependency-triage.py --analyze-changes --output markdown
```

#### 2. Research Phase
- [ ] Read official release notes
- [ ] Check migration guide (if available)
- [ ] Review breaking changes list
- [ ] Check community discussions/issues

#### 3. Local Testing
```bash
# Create a dedicated branch
git checkout -b deps/major-update-package-name

# Update dependencies
# Run comprehensive tests
npm test && pytest
npm run build
docker build --target production -t test-image .
```

#### 4. Canary Branch Strategy

For high-risk updates (Next.js 14→15, pandas 1→2):

```bash
# Create canary branch
git checkout -b canary/nextjs-15-upgrade

# Deploy to staging environment
# Monitor for 48-72 hours
# Collect metrics and feedback
```

### Special Cases

#### Next.js Major Updates
- **Migration Guide**: Always check Next.js migration documentation
- **TypeScript**: Verify TypeScript compatibility
- **Build Process**: Test `npm run build` thoroughly
- **Pages/Components**: Manual testing of all routes
- **Performance**: Compare bundle sizes and load times

#### Python Data Science Libraries
- **Numerical Accuracy**: Run regression tests on calculations
- **API Compatibility**: Check for deprecated functions
- **Memory Usage**: Monitor for memory leaks or increased usage
- **Performance**: Benchmark critical data processing paths

## CI/CD Integration

### Dependency Triage Workflow

Our `.github/workflows/dependency-triage.yml` provides:

1. **Automated Classification**
   - Detects update types (patch/minor/major)
   - Generates review checklists for major updates

2. **Security Scanning**
   - Python: `pip-audit` for vulnerability detection
   - Node.js: `npm audit` for security issues
   - Docker: Trivy for container security

3. **Comprehensive Testing**
   - Multi-platform testing (Ubuntu, Windows, macOS)
   - Multiple Python versions (3.9-3.12)
   - Frontend build validation
   - Docker image verification

4. **Review Automation**
   - Auto-generates PR comments for major updates
   - Creates review artifacts with checklists
   - Uploads security scan results

### Integration with Main CI

The main CI workflow (`.github/workflows/ci.yml`) includes:
- **Install**: Dependencies with caching
- **Lint**: Python (ruff/flake8) and frontend (ESLint)
- **Type Check**: Python (mypy) and TypeScript
- **Test**: pytest with coverage reporting
- **Build**: Frontend production build
- **Docker**: Multi-stage image build and test

## Tools and Scripts

### Dependency Triage Script

```bash
# Analyze current changes
./scripts/dependency-triage.py --analyze-changes

# Generate review checklist
./scripts/dependency-triage.py --analyze-changes --output markdown

# Compare specific git refs
./scripts/dependency-triage.py --analyze-changes --base-ref origin/main --target-ref HEAD
```

### Manual Commands

```bash
# Security audits
pip-audit --desc --format=json
npm audit --audit-level moderate

# Dependency analysis
pipdeptree --graph-output png --graph-output-path deps.png
npm list --depth=0

# Version checking
pip list --outdated
npm outdated
```

## Monitoring and Rollback

### Post-Deployment Monitoring

After major updates:
1. **Application Metrics**: Response times, error rates
2. **Infrastructure Metrics**: CPU, memory, disk usage
3. **User Experience**: Frontend performance, user feedback
4. **Security Scans**: Continuous vulnerability monitoring

### Rollback Strategy

```bash
# Quick rollback for critical issues
git revert <commit-hash>
git push origin main

# For complex rollbacks
git checkout <previous-stable-tag>
git checkout -b hotfix/rollback-dependency
# Cherry-pick critical fixes if needed
```

## Best Practices

### Development Workflow
1. **Separate Branches**: Always test major updates in dedicated branches
2. **Staged Rollout**: Use canary deployments for high-risk changes
3. **Documentation**: Update CHANGELOG.md with breaking changes
4. **Communication**: Notify team of major dependency changes

### Security Considerations
1. **Timely Updates**: Prioritize security patches
2. **Vulnerability Scanning**: Regular automated scans
3. **Supply Chain**: Monitor for compromised packages
4. **Pinning**: Use exact versions in production

### Testing Strategy
1. **Automated Testing**: Comprehensive test coverage
2. **Manual Testing**: UI/UX validation for frontend updates
3. **Performance Testing**: Benchmark critical paths
4. **Integration Testing**: End-to-end workflow validation

## Troubleshooting

### Common Issues

#### Dependency Conflicts
```bash
# Python
pip install --no-deps -r requirements-lock.txt
pip check

# Node.js
npm ls --depth=0
npm audit fix
```

#### Build Failures
```bash
# Clear caches
npm ci --cache ~/.npm-cache
pip cache purge

# Rebuild from scratch
rm -rf node_modules package-lock.json
npm install
```

#### Version Incompatibilities
- Check compatibility matrices in official documentation
- Use `requirements-lock.txt` for exact version reproduction
- Consider using virtual environments for isolation

### Getting Help

1. **Internal**: Check existing issues and PR discussions
2. **Documentation**: Refer to package documentation and migration guides
3. **Community**: Stack Overflow, GitHub issues, package forums
4. **Security**: Report vulnerabilities through appropriate channels

## Metrics and KPIs

Track these metrics for dependency management effectiveness:
- **Time to patch**: How quickly security updates are applied
- **Update success rate**: Percentage of updates applied without issues
- **Rollback frequency**: How often we need to rollback changes
- **Test coverage**: Percentage of code covered by dependency tests
- **Security score**: Number of known vulnerabilities in dependencies

## Conclusion

Effective dependency management is crucial for maintaining a secure, stable, and up-to-date codebase. By following this guide and leveraging our automated tools, we can ensure that dependency updates enhance rather than compromise our application's reliability and security.