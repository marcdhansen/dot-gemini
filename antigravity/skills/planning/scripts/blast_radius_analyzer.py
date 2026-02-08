#!/usr/bin/env python3
"""
Blast Radius Analyzer - Progressive Disclosure Analysis
Provides multi-level impact analysis for proposed changes in LightRAG
"""

import ast
import json
import os
import re
import subprocess
import sys
import yaml
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
import networkx as nx


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnalysisLevel(Enum):
    SUMMARY = "summary"
    DETAILED = "detailed"
    DEEP_DIVE = "deep_dive"


class ChangeType(Enum):
    FUNCTION_CHANGE = "function_change"
    CLASS_CHANGE = "class_change"
    API_CHANGE = "api_change"
    SCHEMA_CHANGE = "schema_change"
    CONFIG_CHANGE = "config_change"
    DOCUMENTATION_CHANGE = "documentation_change"


@dataclass
class FileImpact:
    path: str
    change_type: ChangeType
    complexity_score: float
    dependencies_affected: List[str]
    test_coverage: float
    risk_level: RiskLevel


@dataclass
class ImpactMetrics:
    cyclomatic_complexity: int
    function_dependencies: int
    class_inheritance_depth: int
    public_api_exposure: int
    test_coverage_ratio: float
    documentation_coverage: float


@dataclass
class SummaryResult:
    affected_files_count: int
    critical_paths: List[str]
    risk_level: RiskLevel
    estimated_testing_effort: str
    deployment_impact: str
    timeline_impact: str


@dataclass
class DetailedResult:
    file_impacts: Dict[str, FileImpact]
    dependency_chain: List[str]
    test_coverage_gaps: List[str]
    migration_requirements: List[str]
    rollback_complexity: str


@dataclass
class DeepDiveResult:
    cross_module_dependencies: List[str]
    performance_implications: List[str]
    security_considerations: List[str]
    integration_points: List[str]
    long_term_maintenance_impact: str


@dataclass
class BlastRadiusResult:
    level: AnalysisLevel
    summary: Optional[SummaryResult]
    detailed: Optional[DetailedResult]
    deep_dive: Optional[DeepDiveResult]
    total_impact_score: float
    recommendations: List[str]


class DependencyGraph:
    """Multi-dimensional dependency analysis"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.code_graph = nx.DiGraph()
        self.config_graph = nx.DiGraph()
        self.api_graph = nx.DiGraph()
        self.data_graph = nx.DiGraph()
        self._build_dependency_graphs()

    def _build_dependency_graphs(self):
        """Build dependency graphs from codebase"""
        # Code dependencies from Python imports
        self._build_code_dependencies()

        # Config dependencies from configuration files
        self._build_config_dependencies()

        # API dependencies from route definitions
        self._build_api_dependencies()

    def _build_code_dependencies(self):
        """Build Python code dependency graph"""
        for py_file in self.repo_path.rglob("*.py"):
            if "test" in py_file.name or "venv" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                for imp in imports:
                    self.code_graph.add_edge(str(py_file), imp)

            except (SyntaxError, UnicodeDecodeError):
                continue

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def _build_config_dependencies(self):
        """Build configuration dependency graph"""
        config_patterns = ["*.yaml", "*.yml", "*.json", "*.toml", "*.env*"]

        for pattern in config_patterns:
            for config_file in self.repo_path.rglob(pattern):
                if "test" in config_file.name or "venv" in str(config_file):
                    continue

                # Extract references from config files
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Look for file references and service dependencies
                    refs = self._extract_config_references(content)
                    for ref in refs:
                        self.config_graph.add_edge(str(config_file), ref)

                except (yaml.YAMLError, json.JSONDecodeError, UnicodeDecodeError):
                    continue

    def _extract_config_references(self, content: str) -> List[str]:
        """Extract file and service references from config content"""
        references = []

        # File path patterns
        path_patterns = [
            r"path:\s*([^\s\n]+)",
            r"file:\s*([^\s\n]+)",
            r"url:\s*([^\s\n]+)",
            r"host:\s*([^\s\n]+)",
            r"service:\s*([^\s\n]+)",
        ]

        for pattern in path_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            references.extend(matches)

        return references

    def _build_api_dependencies(self):
        """Build API dependency graph from route definitions"""
        api_files = [
            "lightrag/api/routers/",
            "lightrag/api/routes/",
            "lightrag/webui/api/",
        ]

        for api_dir in api_files:
            api_path = self.repo_path / api_dir
            if not api_path.exists():
                continue

            for py_file in api_path.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    routes = self._extract_api_routes(content)
                    for route in routes:
                        self.api_graph.add_node(route, file=str(py_file))

                except UnicodeDecodeError:
                    continue

    def _extract_api_routes(self, content: str) -> List[str]:
        """Extract API route definitions"""
        routes = []

        # Common route patterns
        route_patterns = [
            r'@[a-zA-Z_]+\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            r'app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        ]

        for pattern in route_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for method, path in matches:
                routes.append(f"{method.upper()} {path}")

        return routes

    def get_fan_in(self, node: str) -> int:
        """Get number of incoming dependencies"""
        total = 0
        for graph in [
            self.code_graph,
            self.config_graph,
            self.api_graph,
            self.data_graph,
        ]:
            total += graph.in_degree(node)
        return total

    def get_fan_out(self, node: str) -> int:
        """Get number of outgoing dependencies"""
        total = 0
        for graph in [
            self.code_graph,
            self.config_graph,
            self.api_graph,
            self.data_graph,
        ]:
            total += graph.out_degree(node)
        return total

    def get_affected_components(
        self, changed_nodes: Set[str], max_depth: int = 5
    ) -> Set[str]:
        """Get all components affected by changes"""
        affected = set()
        frontier = changed_nodes.copy()

        for depth in range(max_depth):
            if not frontier:
                break
            current = frontier
            frontier = set()

            for node in current:
                for layer_graph in [
                    self.code_graph,
                    self.config_graph,
                    self.api_graph,
                    self.data_graph,
                ]:
                    if node not in layer_graph:
                        continue
                    neighbors = set(layer_graph.successors(node))
                    new_impacts = neighbors - affected
                    frontier.update(new_impacts)
                    affected.update(new_impacts)

        return affected


class ChangeDetector:
    """Multi-format change detection and impact analysis"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.dependency_graph = DependencyGraph(repo_path)
        self.critical_paths = [
            "lightrag/core.py",
            "lightrag/api/",
            "lightrag/storage/",
            "database/",
            "deployment/",
        ]

    def analyze_changes(
        self, changed_files: List[Any], level: AnalysisLevel = AnalysisLevel.DETAILED
    ) -> BlastRadiusResult:
        """Analyze changes and generate blast radius report"""
        changed_files = [str(f) for f in changed_files]

        if level == AnalysisLevel.SUMMARY:
            return self._summary_analysis(changed_files)
        elif level == AnalysisLevel.DETAILED:
            return self._detailed_analysis(changed_files)
        else:
            return self._deep_dive_analysis(changed_files)

    def _summary_analysis(self, changed_files: List[str]) -> BlastRadiusResult:
        """Generate summary-level impact analysis"""

        affected_files = set(changed_files)
        critical_files = [f for f in changed_files if self._is_critical_path(f)]

        # Calculate risk level
        risk_level = self._calculate_risk_level(changed_files)

        # Estimate testing effort
        testing_effort = self._estimate_testing_effort(changed_files)

        # Deployment impact
        deployment_impact = self._estimate_deployment_impact(changed_files)

        # Timeline impact
        timeline_impact = self._estimate_timeline_impact(changed_files)

        summary = SummaryResult(
            affected_files_count=len(affected_files),
            critical_paths=critical_files,
            risk_level=risk_level,
            estimated_testing_effort=testing_effort,
            deployment_impact=deployment_impact,
            timeline_impact=timeline_impact,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(changed_files, risk_level)

        # Calculate overall impact score
        impact_score = self._calculate_impact_score(changed_files)

        return BlastRadiusResult(
            level=AnalysisLevel.SUMMARY,
            summary=summary,
            detailed=None,
            deep_dive=None,
            total_impact_score=impact_score,
            recommendations=recommendations,
        )

    def _detailed_analysis(self, changed_files: List[str]) -> BlastRadiusResult:
        """Generate detailed-level impact analysis"""

        # Start with summary analysis
        summary_result = self._summary_analysis(changed_files)

        # Analyze each file
        file_impacts = {}
        for file_path in changed_files:
            impact = self._analyze_file_impact(file_path)
            file_impacts[file_path] = impact

        # Build dependency chain
        dependency_chain = self._build_dependency_chain(changed_files)

        # Identify test coverage gaps
        test_gaps = self._identify_test_gaps(changed_files)

        # Determine migration requirements
        migration_reqs = self._determine_migration_requirements(changed_files)

        # Assess rollback complexity
        rollback_complexity = self._assess_rollback_complexity(changed_files)

        detailed = DetailedResult(
            file_impacts=file_impacts,
            dependency_chain=dependency_chain,
            test_coverage_gaps=test_gaps,
            migration_requirements=migration_reqs,
            rollback_complexity=rollback_complexity,
        )

        return BlastRadiusResult(
            level=AnalysisLevel.DETAILED,
            summary=summary_result.summary,
            detailed=detailed,
            deep_dive=None,
            total_impact_score=summary_result.total_impact_score,
            recommendations=summary_result.recommendations,
        )

    def _deep_dive_analysis(self, changed_files: List[str]) -> BlastRadiusResult:
        """Generate deep-dive level impact analysis"""

        # Start with detailed analysis
        detailed_result = self._detailed_analysis(changed_files)

        # Analyze cross-module dependencies
        cross_module_deps = self._analyze_cross_module_dependencies(changed_files)

        # Performance implications
        performance_implications = self._analyze_performance_implications(changed_files)

        # Security considerations
        security_considerations = self._analyze_security_considerations(changed_files)

        # Integration points
        integration_points = self._identify_integration_points(changed_files)

        # Long-term maintenance impact
        maintenance_impact = self._assess_maintenance_impact(changed_files)

        deep_dive = DeepDiveResult(
            cross_module_dependencies=cross_module_deps,
            performance_implications=performance_implications,
            security_considerations=security_considerations,
            integration_points=integration_points,
            long_term_maintenance_impact=maintenance_impact,
        )

        return BlastRadiusResult(
            level=AnalysisLevel.DEEP_DIVE,
            summary=detailed_result.summary,
            detailed=detailed_result.detailed,
            deep_dive=deep_dive,
            total_impact_score=detailed_result.total_impact_score,
            recommendations=detailed_result.recommendations,
        )

    def _is_critical_path(self, file_path: str) -> bool:
        """Check if file is on a critical path"""
        file_path_str = str(file_path)
        return any(critical in file_path_str for critical in self.critical_paths)

    def _calculate_risk_level(self, changed_files: List[str]) -> RiskLevel:
        """Calculate overall risk level"""
        risk_score = 0

        for file_path in changed_files:
            file_path_str = str(file_path)
            if self._is_critical_path(file_path):
                risk_score += 3
            elif "api" in file_path_str or "routes" in file_path_str:
                risk_score += 2
            elif "config" in file_path_str or "deployment" in file_path_str:
                risk_score += 2
            else:
                risk_score += 1

        if risk_score >= 8:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _estimate_testing_effort(self, changed_files: List[str]) -> str:
        """Estimate testing effort based on changes"""
        file_count = len(changed_files)
        critical_files = sum(1 for f in changed_files if self._is_critical_path(f))

        if critical_files > 0:
            return "2-4 days"
        elif file_count <= 3:
            return "2-4 hours"
        elif file_count <= 10:
            return "1-2 days"
        else:
            return "3-5 days"

    def _estimate_deployment_impact(self, changed_files: List[str]) -> str:
        """Estimate deployment impact"""
        has_api_changes = any("api" in str(f) or "routes" in str(f) for f in changed_files)
        has_config_changes = any("config" in str(f) for f in changed_files)
        has_db_changes = any("database" in str(f) or "schema" in str(f) for f in changed_files)

        if has_db_changes:
            return "FULL_RESTART"
        elif has_config_changes or has_api_changes:
            return "ROLLING"
        else:
            return "NONE"

    def _estimate_timeline_impact(self, changed_files: List[str]) -> str:
        """Estimate timeline impact"""
        risk_level = self._calculate_risk_level(changed_files)

        if risk_level == RiskLevel.CRITICAL:
            return "2-3 weeks"
        elif risk_level == RiskLevel.HIGH:
            return "1-2 weeks"
        elif risk_level == RiskLevel.MEDIUM:
            return "3-5 days"
        else:
            return "1-2 days"

    def _analyze_file_impact(self, file_path: Any) -> FileImpact:
        """Analyze impact of changes to a specific file"""
        file_path = str(file_path)

        # Determine change type
        change_type = self._classify_change_type(file_path)

        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(file_path)

        # Get affected dependencies
        affected_deps = self._get_affected_dependencies(file_path)

        # Get test coverage
        test_coverage = self._get_test_coverage(file_path)

        # Determine risk level
        risk_level = self._calculate_file_risk(file_path, change_type, complexity_score)

        return FileImpact(
            path=file_path,
            change_type=change_type,
            complexity_score=complexity_score,
            dependencies_affected=affected_deps,
            test_coverage=test_coverage,
            risk_level=risk_level,
        )

    def _classify_change_type(self, file_path: str) -> ChangeType:
        """Classify the type of change based on file path"""
        if file_path.endswith(".py"):
            if "api" in file_path or "routes" in file_path:
                return ChangeType.API_CHANGE
            elif "test" in file_path:
                return ChangeType.FUNCTION_CHANGE
            else:
                return ChangeType.CLASS_CHANGE
        elif any(ext in file_path for ext in [".yaml", ".yml", ".json", ".toml"]):
            return ChangeType.CONFIG_CHANGE
        elif "database" in file_path or "schema" in file_path:
            return ChangeType.SCHEMA_CHANGE
        elif file_path.endswith(".md"):
            return ChangeType.DOCUMENTATION_CHANGE
        else:
            return ChangeType.FUNCTION_CHANGE

    def _calculate_complexity_score(self, file_path: str) -> float:
        """Calculate complexity score for a file"""
        file_full_path = self.repo_path / file_path

        if not file_full_path.exists():
            return 5.0  # Default complexity for new files

        try:
            with open(file_full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic complexity metrics
            line_count = len(content.splitlines())
            if file_path.endswith(".py"):
                tree = ast.parse(content)
                function_count = sum(
                    1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                )
                class_count = sum(
                    1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                )

                complexity = min(
                    line_count / 50 + function_count * 2 + class_count * 3, 20
                )
            else:
                complexity = min(line_count / 100, 10)

            return complexity

        except (SyntaxError, UnicodeDecodeError):
            return 10.0  # High complexity for files that can't be parsed

    def _get_affected_dependencies(self, file_path: str) -> List[str]:
        """Get list of dependencies affected by file changes"""
        affected = set()

        # Get direct dependents from code graph
        if file_path in self.dependency_graph.code_graph:
            affected.update(self.dependency_graph.code_graph.successors(file_path))

        # Get direct dependents from config graph
        if file_path in self.dependency_graph.config_graph:
            affected.update(self.dependency_graph.config_graph.successors(file_path))

        return list(affected)

    def _get_test_coverage(self, file_path: str) -> float:
        """Get test coverage percentage for a file"""
        # Look for corresponding test files
        file_stem = Path(file_path).stem
        test_patterns = [f"test_{file_stem}", f"{file_stem}_test", f"tests/{file_stem}"]

        test_found = False
        for pattern in test_patterns:
            if any(pattern in str(f) for f in self.repo_path.rglob("*.py")):
                test_found = True
                break

        return 0.8 if test_found else 0.2  # Estimate

    def _calculate_file_risk(
        self, file_path: str, change_type: ChangeType, complexity_score: float
    ) -> RiskLevel:
        """Calculate risk level for specific file"""
        base_risk = {
            ChangeType.API_CHANGE: 3,
            ChangeType.SCHEMA_CHANGE: 4,
            ChangeType.CONFIG_CHANGE: 2,
            ChangeType.CLASS_CHANGE: 2,
            ChangeType.FUNCTION_CHANGE: 1,
            ChangeType.DOCUMENTATION_CHANGE: 0,
        }[change_type]

        if self._is_critical_path(file_path):
            base_risk += 2

        complexity_factor = min(complexity_score / 5, 3)
        total_risk = base_risk + complexity_factor

        if total_risk >= 6:
            return RiskLevel.CRITICAL
        elif total_risk >= 4:
            return RiskLevel.HIGH
        elif total_risk >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _build_dependency_chain(self, changed_files: List[str]) -> List[str]:
        """Build dependency chain for changed files"""
        chain = set(changed_files)

        for file_path in changed_files:
            affected = self.dependency_graph.get_affected_components(
                {file_path}, max_depth=3
            )
            chain.update(affected)

        return list(chain)

    def _identify_test_gaps(self, changed_files: List[str]) -> List[str]:
        """Identify files with inadequate test coverage"""
        gaps = []

        for file_path in changed_files:
            if self._get_test_coverage(file_path) < 0.5:
                gaps.append(file_path)

        return gaps

    def _determine_migration_requirements(self, changed_files: List[str]) -> List[str]:
        """Determine if any migrations are required"""
        migrations = []

        for file_path in changed_files:
            if "database" in file_path or "schema" in file_path:
                migrations.append(f"Database migration needed for {file_path}")
            elif "config" in file_path:
                migrations.append(f"Configuration migration needed for {file_path}")

        return migrations

    def _assess_rollback_complexity(self, changed_files: List[str]) -> str:
        """Assess complexity of rolling back changes"""
        has_db_changes = any("database" in f or "schema" in f for f in changed_files)
        has_config_changes = any("config" in f for f in changed_files)
        file_count = len(changed_files)

        if has_db_changes:
            return "COMPLEX"
        elif has_config_changes or file_count > 10:
            return "MODERATE"
        else:
            return "SIMPLE"

    def _analyze_cross_module_dependencies(self, changed_files: List[str]) -> List[str]:
        """Analyze cross-module dependencies affected"""
        cross_modules = set()

        for file_path in changed_files:
            affected = self.dependency_graph.get_affected_components(
                {file_path}, max_depth=5
            )

            # Group by module
            for affected_file in affected:
                module = self._get_module_name(affected_file)
                original_module = self._get_module_name(file_path)
                if module != original_module:
                    cross_modules.add(f"{original_module} → {module}")

        return list(cross_modules)

    def _analyze_performance_implications(self, changed_files: List[str]) -> List[str]:
        """Analyze potential performance implications"""
        implications = []

        for file_path in changed_files:
            if "query" in file_path or "search" in file_path:
                implications.append("Query performance may be affected")
            elif "cache" in file_path or "storage" in file_path:
                implications.append("Cache/storage performance may be affected")
            elif "api" in file_path or "routes" in file_path:
                implications.append("API response times may be affected")

        return implications

    def _analyze_security_considerations(self, changed_files: List[str]) -> List[str]:
        """Analyze security considerations"""
        considerations = []

        for file_path in changed_files:
            if "auth" in file_path or "security" in file_path:
                considerations.append("Security permissions may be affected")
            elif "api" in file_path or "routes" in file_path:
                considerations.append("API security boundaries may change")
            elif "config" in file_path:
                considerations.append("Security configuration may be affected")

        return considerations

    def _identify_integration_points(self, changed_files: List[str]) -> List[str]:
        """Identify integration points affected"""
        points = []

        for file_path in changed_files:
            if "api" in file_path or "routes" in file_path:
                points.append("External API integrations")
            elif "webui" in file_path or "ui" in file_path:
                points.append("Frontend integrations")
            elif "deployment" in file_path:
                points.append("Deployment pipeline integrations")

        return list(set(points))

    def _assess_maintenance_impact(self, changed_files: List[str]) -> str:
        """Assess long-term maintenance impact"""
        complexity = sum(self._calculate_complexity_score(f) for f in changed_files)
        file_count = len(changed_files)

        if complexity > 50 or file_count > 20:
            return "HIGH - Increased maintenance burden"
        elif complexity > 20 or file_count > 10:
            return "MEDIUM - Moderate maintenance impact"
        else:
            return "LOW - Minimal maintenance impact"

    def _get_module_name(self, file_path: str) -> str:
        """Extract module name from file path"""
        parts = file_path.split("/")
        if len(parts) >= 2:
            return parts[0] + "/" + parts[1]
        return file_path

    def _calculate_impact_score(self, changed_files: List[str]) -> float:
        """Calculate overall impact score"""
        base_score = len(changed_files) * 2

        for file_path in changed_files:
            if self._is_critical_path(file_path):
                base_score += 5
            elif "api" in file_path:
                base_score += 3
            elif "config" in file_path:
                base_score += 2

        return min(base_score, 100)  # Cap at 100

    def _generate_recommendations(
        self, changed_files: List[str], risk_level: RiskLevel
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if risk_level == RiskLevel.CRITICAL:
            recommendations.append(
                "🚨 Consider breaking this into smaller, manageable changes"
            )
            recommendations.append("📋 Create detailed rollback plan before starting")
            recommendations.append(
                "🧪 Schedule comprehensive testing including edge cases"
            )
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("⚡ Plan thorough testing and review process")
            recommendations.append("📊 Monitor key metrics during deployment")
            recommendations.append("🔄 Consider canary deployment approach")

        # Specific recommendations based on file types
        has_api_changes = any("api" in f for f in changed_files)
        has_config_changes = any("config" in f for f in changed_files)
        has_db_changes = any("database" in f for f in changed_files)

        if has_api_changes:
            recommendations.append("🔗 Update API documentation and version if needed")

        if has_config_changes:
            recommendations.append(
                "⚙️  Test configuration changes in staging environment"
            )

        if has_db_changes:
            recommendations.append("🗄️  Create and test database migration scripts")

        # Test coverage recommendations
        test_gaps = self._identify_test_gaps(changed_files)
        if test_gaps:
            recommendations.append(
                f"🧪 Add test coverage for {len(test_gaps)} files with inadequate testing"
            )

        return recommendations


def main():
    """Main entry point for blast radius analysis"""
    if len(sys.argv) < 3:
        print("Usage: python blast_radius_analyzer.py <command> <options>")
        print("Commands:")
        print("  analyze <files> [--level summary|detailed|deep_dive]")
        print("  dependencies <file>")
        print("  impact <file>")
        sys.exit(1)

    command = sys.argv[1]
    repo_path = Path.cwd()

    if command == "analyze":
        if len(sys.argv) < 3:
            print("Error: Please provide files to analyze")
            sys.exit(1)

        files = sys.argv[2].split(",")
        level = AnalysisLevel.DETAILED

        if len(sys.argv) > 4 and sys.argv[3] == "--level":
            level_str = sys.argv[4]
            level = AnalysisLevel(level_str)

        detector = ChangeDetector(repo_path)
        result = detector.analyze_changes(files, level)

        print(json.dumps(asdict(result), indent=2, default=str))

    elif command == "dependencies":
        if len(sys.argv) < 3:
            print("Error: Please provide file to analyze dependencies")
            sys.exit(1)

        file_path = sys.argv[2]
        graph = DependencyGraph(repo_path)
        affected = graph.get_affected_components({file_path})

        print(f"Dependencies affected by {file_path}:")
        for dep in sorted(affected):
            print(f"  - {dep}")

    elif command == "impact":
        if len(sys.argv) < 3:
            print("Error: Please provide file to analyze impact")
            sys.exit(1)

        file_path = sys.argv[2]
        detector = ChangeDetector(repo_path)
        impact = detector._analyze_file_impact(file_path)

        print(f"Impact analysis for {file_path}:")
        print(json.dumps(asdict(impact), indent=2, default=str))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
