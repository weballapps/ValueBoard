#!/usr/bin/env python3
"""
Generate build information file for deployment tracking
This script should be run during the build process
"""

import json
import subprocess
from datetime import datetime
import os

def get_git_info():
    """Extract git commit information"""
    try:
        # Get last commit hash
        commit_hash = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                   capture_output=True, text=True, timeout=10)
        
        # Get last commit timestamp
        commit_time = subprocess.run(['git', 'log', '-1', '--format=%ci'], 
                                   capture_output=True, text=True, timeout=10)
        
        # Get last commit message
        commit_msg = subprocess.run(['git', 'log', '-1', '--format=%s'], 
                                  capture_output=True, text=True, timeout=10)
        
        if all(cmd.returncode == 0 for cmd in [commit_hash, commit_time, commit_msg]):
            return {
                'commit_hash': commit_hash.stdout.strip(),
                'commit_time': commit_time.stdout.strip(),
                'commit_message': commit_msg.stdout.strip()
            }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None

def main():
    """Generate build info file"""
    build_info = {
        'build_time': datetime.now().isoformat(),
        'build_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Try to get git information
    git_info = get_git_info()
    if git_info:
        build_info['git'] = git_info
        # Use git commit time as the main timestamp
        try:
            # Parse git timestamp and use it
            git_time_str = git_info['commit_time'].split(' +')[0]  # Remove timezone
            git_time = datetime.strptime(git_time_str, "%Y-%m-%d %H:%M:%S")
            build_info['last_update'] = git_time.strftime("%Y-%m-%d %H:%M")
            build_info['update_source'] = 'git commit'
        except:
            build_info['last_update'] = build_info['build_timestamp']
            build_info['update_source'] = 'build time'
    else:
        build_info['last_update'] = build_info['build_timestamp']
        build_info['update_source'] = 'build time'
    
    # Write to build_info.json
    with open('build_info.json', 'w') as f:
        json.dump(build_info, f, indent=2)
    
    print(f"Build info generated: {build_info['last_update']} ({build_info['update_source']})")

if __name__ == '__main__':
    main()