from rope.refactor.rename import Rename
from rope.base.project import Project

import argparse
import tempfile
import sys
import os


def rename_module(project, old_module, new_module):
    with tempfile.TemporaryDirectory() as tempdir:
        os.makedirs(os.path.join(tempdir, old_module), exist_ok=True)
        open(os.path.join(tempdir, old_module, '__init__.py'), 'a').close()
        sys.path.append(tempdir)

        resource = project.find_module(old_module)
        changes = Rename(project, resource).get_changes(new_module)
        changes.do()


def rename_modules(project_path, module_mapper):
    project = Project(project_path, ropefolder=None)

    for old_module, new_module in module_mapper:
        rename_module(project, old_module, new_module)


def cli(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='path to refactor imports', required=True)
    parser.add_argument('--replace', help='module import to replace', nargs=2, action='append')
    return parser.parse_args()


def main():
    args = cli(sys.argv[1:])
    rename_modules(args.path, args.replace or [])


if __name__ == "__main__":
    main()
