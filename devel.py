#!/usr/bin/env python
"""Devel script"""

import argparse
import re
import sys

def increment_version(version, part):
    """Increment semver"""

    version_match = re.search(r'(\d+)\.(\d+)\.(\d+)', version)
    major = int(version_match.group(1))
    minor = int(version_match.group(2))
    patch = int(version_match.group(3))

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1

    return str(major) + '.' + str(minor) + '.' + str(patch)

def versioning(args):
    """Handle the versioning of the application"""

    with open('.version') as version_file:
        app_version = version_file.readline().strip('\n')

    if not args.part:
        # just display the current version
        print(app_version)
    else:
        new_version = increment_version(app_version, args.part)
        print(new_version)

def main():
    """Main script execution"""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    version_parser = subparsers.add_parser('version', help='display or modify the current version')
    version_parser.add_argument('-p', '--part', help='the part of the version to modify (major, minor, or patch)')
    version_parser.set_defaults(func=versioning)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    cli_args = parser.parse_args()
    cli_args.func(cli_args)

if __name__ == '__main__':
    main()
