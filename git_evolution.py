"""
Git Evolution Analyzer
Tracks code metrics, clones, and bugs across git history.
"""

import os
import git
import tempfile
import shutil
import time
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitEvolutionAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        
    def get_commit_history(self, limit: int = 5) -> List[git.Commit]:
        """Get the last N commits."""
        return list(self.repo.iter_commits(max_count=limit))
        
    def analyze_evolution(self, commits: List[git.Commit], file_extensions: List[str] = None) -> List[Dict]:
        """
        Analyze code metrics for each commit.
        Note: This is a lightweight analysis (LOC count) for now to demonstrate evolution.
        Full clone detection on every commit would be very slow for a prototype.
        """
        history = []
        
        for commit in commits:
            logger.info(f"Analyzing commit: {commit.hexsha[:7]} - {commit.summary}")
            
            # Simple metric: Count total lines of code in relevant files
            # In a real system, we would checkout the commit to a temp dir
            # Here we will just inspect the blob sizes for speed
            
            total_lines = 0
            file_count = 0
            
            # Iterate through tree
            for item in commit.tree.traverse():
                if item.type == 'blob':
                    if file_extensions and not any(item.name.endswith(ext) for ext in file_extensions):
                        continue
                        
                    try:
                        # Estimate lines from size or read content (expensive)
                        # Let's read content for accuracy on small repos
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        lines = len(content.splitlines())
                        total_lines += lines
                        file_count += 1
                    except Exception as e:
                        pass
                        
            history.append({
                "hash": commit.hexsha,
                "short_hash": commit.hexsha[:7],
                "message": str(commit.summary),
                "author": str(commit.author),
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(commit.committed_date)),
                "total_lines": total_lines,
                "file_count": file_count
            })
            
        return history

if __name__ == "__main__":
    # Test on local repo
    try:
        analyzer = GitEvolutionAnalyzer(".")
        commits = analyzer.get_commit_history(5)
        results = analyzer.analyze_evolution(commits, [".py", ".java"])
        print(results)
    except Exception as e:
        print(f"Error: {e}")
