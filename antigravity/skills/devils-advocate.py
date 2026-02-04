#!/usr/bin/env python3
"""
Devil's Advocate PFC Integration
Enhanced Pre-Flight Check with critical thinking and devil's advocate perspective
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class DevilsAdvocatePFC:
    def __init__(self):
        self.workspace_dir = Path.cwd()
        
    def run_devils_advocate_pfc(self, force_enable=False):
        """Run PFC with devil's advocate perspective"""
        
        print("👹 Devil's Advocate Pre-Flight Check")
        print("=" * 50)
        print()
        
        # 1. Challenge Workspace State
        self._challenge_workspace_assumptions()
        
        # 2. Devil's Advocate Analysis
        devils_insights = self._generate_devils_perspective()
        
        # 3. User Impact Analysis
        self._analyze_user_impact()
        
        # 4. Evidence Requirements
        self._establish_evidence_requirements()
        
        print("🎯 DEVIL'S ADVOCATE SUMMARY")
        print("------------------------")
        print(f"🔍 Critical Challenges Identified: {len(devils_insights)}")
        print(f"⚖️  Risk Factors: {len(devils_insights)}")
        print(f"📋 Evidence Requirements: Strict validation needed")
        print()
        print("💡 COMMAND USAGE:")
        print("   • Standard: /devils-advocate")
        print("   • Force enable: /devils-advocate --force")
        print("   • PFC integration: /devils-advocate pfc")
        print("   • Force enable + PFC: /devils-advocate --force pfc")
        print()
        print("🚀 PREPARE FOR:")
        print("   • Rigorous questioning of assumptions")
        print("   • Counterargument generation for every decision")
        print("   • Evidence-based validation before action")
        print("   • User-centric risk assessment")
        print()
        
        return devils_insights
    
    def _challenge_workspace_assumptions(self):
        """Challenge and question workspace assumptions"""
        print("🔍 CHALLENGING WORKSPACE ASSUMPTIONS")
        print("----------------------------------")
        
        # Check git state
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.workspace_dir)
            git_changes = result.stdout.strip()
            
            if git_changes:
                print("   ❌ DIRTY WORKING DIRECTORY")
                print("      → Uncommitted changes exist")
                print("      → Risk: Lost work, merge conflicts")
            else:
                print("   ✅ Clean working directory")
                print("      → But: Are you on the right branch?")
                
        except Exception:
            print("   ⚠️  Could not determine git state")
        
        # Check current branch
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=self.workspace_dir)
            current_branch = result.stdout.strip()
            
            if current_branch == "main" or current_branch == "master":
                print("   ⚠️  ON MAIN/MASTER BRANCH")
                print("      → Risk: Working directly on production")
                print("      → Question: Should this work be on a feature branch?")
            else:
                print("   ✅ On feature branch:", current_branch)
                
        except Exception:
            print("   ⚠️  Could not determine branch")
        
        # Check for active issues
        if self._command_exists('bd'):
            try:
                result = subprocess.run(['bd', 'list', '--status', 'in_progress', '--limit', '3'],
                                      capture_output=True, text=True, cwd=self.workspace_dir)
                issues = result.stdout.strip()
                
                if issues and "No issues found" not in issues:
                    lines = [line for line in issues.split('\n') if line.strip() and '○' in line]
                    print("   📋 ACTIVE ISSUES DETECTED")
                    lines = [line for line in issues[:2]:
                        print(f"      → {line}")
                else:
                    print("   ✅ No active issues detected")
                    
            except Exception:
                print("   ⚠️  Could not check issues")
        else:
            print("   ⚠️  Beads not available")
        
        print()
    
    def _generate_devils_perspective(self):
        """Generate devil's advocate insights"""
        print("👹 DEVIL'S ADVOCATE ANALYSIS")
        print("-------------------------")
        
        insights = []
        
        # Challenge task approach
        insights.append({
            "type": "approach_criticism",
            "challenge": "Question task efficiency and methodology",
            "counterargument": "Is this the most efficient way to achieve the goal?",
            "risk": "Wasting time on suboptimal approaches",
            "evidence_needed": "Performance benchmarks, time tracking"
        })
        
        # Challenge assumptions
        insights.append({
            "type": "assumption_challenge",
            "challenge": "What core assumptions are unproven?",
            "counterargument": "What if the fundamental premise is wrong?",
            "risk": "Building on faulty foundation",
            "evidence_needed": "Proof of concept, validation tests"
        })
        
        # Challenge user requirements
        insights.append({
            "type": "requirement_validation",
            "challenge": "Are user requirements fully understood?",
            "counterargument": "What if users actually need X instead of Y?",
            "risk": "Solving wrong problem, user resistance",
            "evidence_needed": "User interviews, requirement documents"
        })
        
        # Challenge technical decisions
        insights.append({
            "type": "technical_criticism",
            "challenge": "Is this technical choice optimal?",
            "counterargument": "What are the alternatives and their trade-offs?",
            "risk": "Technical debt, scalability issues",
            "evidence_needed": "Technical proof-of-concept, benchmarks"
        })
        
        # Challenge timeline and scope
        insights.append({
            "type": "scope_challenge",
            "challenge": "Is the timeline realistic?",
            "counterargument": "What if the scope is too ambitious/pessimistic?",
            "risk": "Missed deadlines, incomplete delivery",
            "evidence_needed": "Historical data, milestone analysis"
        })
        
        print(f"   🔍 Generated {len(insights)} critical challenges")
        for insight in insights:
            print(f"   • {insight['challenge']}")
        
        print()
        return insights
    
    def _analyze_user_impact(self):
        """Analyze impact on end users"""
        print("👥 USER IMPACT ANALYSIS")
        print("---------------------")
        
        # This would be customized based on actual project
        impact_areas = [
            "Performance impact: Will this slow down user workflows?",
            "Complexity impact: Does this increase user cognitive load?",
            "Data safety: Are user data properly protected?",
            "Accessibility impact: Does this affect user accessibility?",
            "Migration impact: What happens to existing user workflows?"
        ]
        
        for area in impact_areas:
            print(f"   🔍 {area}")
        
        print("   📋 QUESTIONS TO ASK USERS:")
        print("      • How will this affect your daily work?")
        print("      • What training will you need?")
        print("      • What concerns do you have about this change?")
        print("      • What would make this better for you?")
        print()
    
    def _establish_evidence_requirements(self):
        """Set strict evidence requirements"""
        print("📋 EVIDENCE REQUIREMENTS")
        print("----------------------")
        
        requirements = [
            "Specific metrics: Quantifiable success criteria",
            "Risk assessment: Documented potential failure points", 
            "Alternative analysis: At least 2 competing approaches",
            "User validation: Proof that users actually want this",
            "Technical validation: Performance benchmarks and tests",
            "Timeline validation: Historical data for similar projects"
        ]
        
        for req in requirements:
            print(f"   ✅ {req}")
        
        print("   🚫 EVIDENCE STANDARDS:")
        print("   • No 'I think', 'I feel', 'probably' statements")
        print("   • No anecdotal evidence without supporting data")
        print("   • No assumptions without verification")
        print("   • No decisions without documented trade-offs")
        print("   • Counterarguments must be addressed with evidence")
        print()
    
    def _assess_risks_and_consequences(self):
        """Assess risks and potential consequences"""
        print("⚖️  RISK ASSESSMENT")
        print("--------------------")
        
        risk_categories = [
            {
                "type": "technical_risk",
                "risks": [
                    "Performance degradation",
                    "Integration failures", 
                    "Security vulnerabilities",
                    "Scalability bottlenecks"
                ]
            },
            {
                "type": "user_risk",
                "risks": [
                    "Workflow disruption",
                    "Learning curve increase",
                    "Data loss or corruption",
                    "User resistance to change"
                ]
            },
            {
                "type": "project_risk",
                "risks": [
                    "Timeline slippage",
                    "Scope creep",
                    "Resource overruns",
                    "Stakeholder misalignment"
                ]
            }
        ]
        
        print("   🔍 Risk Categories:")
        for category in risk_categories:
            print(f"   🔍 {category['type'].replace('_', ' ').title()}:")
            for risk in category['risks']:
                print(f"      • {risk}")
        
        print()
        print("   🎯 CONSEQUENCE ANALYSIS:")
        print("   • Best case: What happens if everything goes right?")
        print("   • Worst case: What happens if everything goes wrong?")
        print("   • Most likely: Probable outcome with mitigation")
        print()
        print("   ⚫ MITIGATION STRATEGIES:")
        print("      • Failsafe plans: What if primary approach fails?")
        print("      • Rollback procedures: How to undo changes if needed?")
        print("      • Monitoring plans: Early warning systems for problems")
        print("      • User communication: Change management and training strategies")
        print()
    
    def _command_exists(self, command):
        """Check if a command exists in the system"""
        try:
            subprocess.run([command, '--version'], 
                          capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False


def main():
    """Main entry point for devil's advocate PFC"""
    
    # Parse command line arguments
    force_enable = "--force" in sys.argv
    pfc_mode = None
    if "pfc" in sys.argv:
        pfc_mode = "pfc"
    elif "force pfc" in sys.argv:
        pfc_mode = "pfc"
    
    pfc = DevilsAdvocatePFC()
    
    try:
        if pfc_mode == "pfc":
            print("👹 Devil's Advocate - PFC Integration Mode")
            insights = pfc.run_devils_advocate_pfc(force_enable)
            
            # Save insights for later reference
            insights_file = Path.cwd() / ".devils_insights.json"
            with open(insights_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "insights": insights,
                    "mode": "pfc_integration",
                    "force_enabled": force_enable
                }, f, indent=2)
            
            print(f"📝 Insights saved to: {insights_file}")
            print()
            
        elif pfc_mode == "force pfc":
            print("👹 Devil's Advocate - PFC Integration Mode (Forced)")
            insights = pfc.run_devils_advocate_pfc(force_enable=True)
            
            # Save insights for later reference
            insights_file = Path.cwd() / ".devils_insights.json"
            with open(insights_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "insights": insights,
                    "mode": "pfc_integration_forced",
                    "force_enabled": force_enable
                }, f, indent=2)
            
            print(f"📝 Insights saved to: {insights_file}")
            print()
            
        else:
            print("👹 Devil's Advocate - Standard Critical Analysis")
            insights = pfc.run_devils_advocate_pfc()
            
            # Save insights for later reference
            insights_file = Path.cwd() / ".devils_insights.json"
            with open(insights_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "insights": insights,
                    "mode": "standard_analysis",
                    "force_enabled": force_enable
                }, f, indent=2)
            
            print(f"📝 Insights saved to: {insights_file}")
            print()
        
    except KeyboardInterrupt:
        print("\n👋 Devil's advocate analysis interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERROR: Devil's advocate PFC failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()