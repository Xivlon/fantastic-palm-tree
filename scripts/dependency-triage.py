#!/usr/bin/env python3
"""
Dependency Management and Triage Tool

This script helps classify and manage dependency updates for the Fantastic Palm Tree project.
It analyzes dependency changes, classifies them by update type (patch/minor/major),
and provides guidance for review processes.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from packaging import version
except ImportError:
    print("Warning: packaging library not available. Version comparison may be limited.")
    version = None


class DependencyAnalyzer:
    """Analyze and classify dependency updates."""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        
    def classify_version_change(self, old_version: str, new_version: str) -> str:
        """Classify a version change as patch, minor, or major."""
        if not version:
            return "major"  # Be conservative if packaging not available
            
        try:
            old_ver = version.parse(old_version.lstrip('v^~'))
            new_ver = version.parse(new_version.lstrip('v^~'))
            
            if old_ver.major != new_ver.major:
                return "major"
            elif old_ver.minor != new_ver.minor:
                return "minor"
            else:
                return "patch"
        except Exception:
            # If version parsing fails, assume it's major to be safe
            return "major"
    
    def get_python_dependencies(self) -> Dict:
        """Get current Python dependencies."""
        dependencies = {}
        
        # Parse pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path) as f:
                content = f.read()
                
            # Simple regex-based parsing for dependencies
            dep_pattern = r'"([^">=<!\s]+)[^"]*"'
            dependencies_section = False
            
            for line in content.split('\n'):
                line = line.strip()
                if line == 'dependencies = [':
                    dependencies_section = True
                elif dependencies_section and line == ']':
                    dependencies_section = False
                elif dependencies_section and line.startswith('"'):
                    match = re.match(dep_pattern, line)
                    if match:
                        package = match.group(1)
                        dependencies[package] = line.strip('",')
        
        # Parse requirements.txt files
        for req_file in self.repo_path.glob("requirements*.txt"):
            try:
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            match = re.match(r'([^>=<!\s]+)', line)
                            if match:
                                dependencies[match.group(1)] = line
            except Exception as e:
                print(f"Warning: Could not parse {req_file}: {e}")
                
        return dependencies
    
    def get_nodejs_dependencies(self) -> Dict:
        """Get current Node.js dependencies."""
        dependencies = {}
        
        package_json_path = self.repo_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path) as f:
                    data = json.load(f)
                    
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in data:
                        dependencies.update(data[dep_type])
                        
            except Exception as e:
                print(f"Warning: Could not parse package.json: {e}")
                
        return dependencies
    
    def analyze_git_changes(self, base_ref: str = "HEAD~1", target_ref: str = "HEAD") -> List[Dict]:
        """Analyze dependency changes between git references."""
        changes = []
        
        try:
            # Check Python dependency changes
            result = subprocess.run([
                'git', 'diff', base_ref, target_ref, '--',
                'requirements*.txt', 'pyproject.toml'
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.stdout:
                changes.extend(self._parse_python_diff(result.stdout))
            
            # Check Node.js dependency changes
            result = subprocess.run([
                'git', 'diff', base_ref, target_ref, '--', 'package*.json'
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.stdout:
                changes.extend(self._parse_nodejs_diff(result.stdout))
                
        except Exception as e:
            print(f"Warning: Could not analyze git changes: {e}")
            
        return changes
    
    def _parse_python_diff(self, diff_text: str) -> List[Dict]:
        """Parse Python dependency changes from git diff."""
        changes = []
        additions = {}
        removals = {}
        
        for line in diff_text.split('\n'):
            if line.startswith('+') and '==' in line and not line.startswith('+++'):
                match = re.search(r'\+([^=]+)==([^\s]+)', line)
                if match:
                    package, new_version = match.groups()
                    additions[package.strip()] = new_version.strip()
                    
            elif line.startswith('-') and '==' in line and not line.startswith('---'):
                match = re.search(r'-([^=]+)==([^\s]+)', line)
                if match:
                    package, old_version = match.groups()
                    removals[package.strip()] = old_version.strip()
        
        # Match additions with removals to find updates
        for package, new_version in additions.items():
            if package in removals:
                old_version = removals[package]
                update_type = self.classify_version_change(old_version, new_version)
                changes.append({
                    'package': package,
                    'ecosystem': 'pip',
                    'old_version': old_version,
                    'new_version': new_version,
                    'update_type': update_type,
                    'change_type': 'update'
                })
            else:
                changes.append({
                    'package': package,
                    'ecosystem': 'pip',
                    'old_version': None,
                    'new_version': new_version,
                    'update_type': 'new',
                    'change_type': 'addition'
                })
        
        # Find pure removals
        for package, old_version in removals.items():
            if package not in additions:
                changes.append({
                    'package': package,
                    'ecosystem': 'pip',
                    'old_version': old_version,
                    'new_version': None,
                    'update_type': 'removal',
                    'change_type': 'removal'
                })
                
        return changes
    
    def _parse_nodejs_diff(self, diff_text: str) -> List[Dict]:
        """Parse Node.js dependency changes from git diff."""
        changes = []
        additions = {}
        removals = {}
        
        for line in diff_text.split('\n'):
            if '"' in line and ':' in line:
                if line.strip().startswith('+'):
                    match = re.search(r'\+\s*"([^"]+)":\s*"([^"]+)"', line)
                    if match:
                        package, package_version = match.groups()
                        additions[package] = package_version
                        
                elif line.strip().startswith('-'):
                    match = re.search(r'-\s*"([^"]+)":\s*"([^"]+)"', line)
                    if match:
                        package, package_version = match.groups()
                        removals[package] = package_version
        
        # Match additions with removals to find updates
        for package, new_version in additions.items():
            if package in removals:
                old_version = removals[package]
                update_type = self.classify_version_change(old_version, new_version)
                changes.append({
                    'package': package,
                    'ecosystem': 'npm',
                    'old_version': old_version,
                    'new_version': new_version,
                    'update_type': update_type,
                    'change_type': 'update'
                })
            else:
                changes.append({
                    'package': package,
                    'ecosystem': 'npm',
                    'old_version': None,
                    'new_version': new_version,
                    'update_type': 'new',
                    'change_type': 'addition'
                })
        
        # Find pure removals
        for package, old_version in removals.items():
            if package not in additions:
                changes.append({
                    'package': package,
                    'ecosystem': 'npm',
                    'old_version': old_version,
                    'new_version': None,
                    'update_type': 'removal',
                    'change_type': 'removal'
                })
                
        return changes
    
    def generate_review_checklist(self, changes: List[Dict]) -> str:
        """Generate a review checklist for dependency changes."""
        major_updates = [c for c in changes if c['update_type'] == 'major']
        
        if not major_updates:
            return "✅ No major dependency updates found. Standard review process applies."
        
        checklist = "# Dependency Review Checklist\n\n"
        checklist += "## Major Updates Requiring Review\n\n"
        
        for change in major_updates:
            checklist += f"### {change['package']} ({change['ecosystem']})\n"
            checklist += f"**Version Change:** {change['old_version']} → {change['new_version']}\n\n"
            checklist += "**Review Steps:**\n"
            checklist += "- [ ] Read release notes and changelog\n"
            checklist += "- [ ] Identify breaking changes\n"
            checklist += "- [ ] Test locally in development environment\n"
            checklist += "- [ ] Run full test suite\n"
            checklist += "- [ ] Check for security implications\n"
            checklist += "- [ ] Update documentation if needed\n"
            checklist += "- [ ] Consider canary branch deployment\n\n"
            
            # Add specific guidance for known packages
            if change['package'] in ['next', 'react', 'react-dom']:
                checklist += "**⚠️ Frontend Framework Update:**\n"
                checklist += "- [ ] Check Next.js migration guide\n"
                checklist += "- [ ] Test all pages and components\n"
                checklist += "- [ ] Verify build process works\n"
                checklist += "- [ ] Check for TypeScript compatibility\n\n"
            elif change['package'] in ['fastapi', 'pydantic']:
                checklist += "**⚠️ API Framework Update:**\n"
                checklist += "- [ ] Test API endpoints\n"
                checklist += "- [ ] Verify schema validation\n"
                checklist += "- [ ] Check async/await compatibility\n\n"
            elif change['package'] in ['pandas', 'numpy']:
                checklist += "**⚠️ Data Science Library Update:**\n"
                checklist += "- [ ] Test data processing pipelines\n"
                checklist += "- [ ] Verify numerical computation accuracy\n"
                checklist += "- [ ] Check for deprecated function usage\n\n"
            
            checklist += "---\n\n"
        
        checklist += "## General Guidelines\n\n"
        checklist += "1. **Testing**: Always test major updates in a separate branch\n"
        checklist += "2. **Rollback Plan**: Have a rollback strategy ready\n"
        checklist += "3. **Monitoring**: Monitor for issues after deployment\n"
        checklist += "4. **Documentation**: Update CHANGELOG.md with breaking changes\n"
        
        return checklist


def main():
    parser = argparse.ArgumentParser(description="Dependency Management and Triage Tool")
    parser.add_argument("--analyze-changes", action="store_true",
                       help="Analyze dependency changes in current branch")
    parser.add_argument("--base-ref", default="HEAD~1",
                       help="Base git reference for comparison (default: HEAD~1)")
    parser.add_argument("--target-ref", default="HEAD",
                       help="Target git reference for comparison (default: HEAD)")
    parser.add_argument("--output", choices=["json", "markdown", "text"], default="text",
                       help="Output format")
    parser.add_argument("--output-file", type=Path,
                       help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer()
    
    if args.analyze_changes:
        changes = analyzer.analyze_git_changes(args.base_ref, args.target_ref)
        
        if args.output == "json":
            output = json.dumps(changes, indent=2)
        elif args.output == "markdown":
            output = analyzer.generate_review_checklist(changes)
        else:  # text
            if not changes:
                output = "No dependency changes detected."
            else:
                output = "Dependency Changes:\n"
                for change in changes:
                    if change['change_type'] == 'update':
                        output += f"• {change['package']} ({change['ecosystem']}): "
                        output += f"{change['old_version']} → {change['new_version']} "
                        output += f"[{change['update_type']}]\n"
                    elif change['change_type'] == 'addition':
                        output += f"• {change['package']} ({change['ecosystem']}): "
                        output += f"added {change['new_version']}\n"
                    elif change['change_type'] == 'removal':
                        output += f"• {change['package']} ({change['ecosystem']}): "
                        output += f"removed {change['old_version']}\n"
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            print(f"Output written to {args.output_file}")
        else:
            print(output)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()