#!/usr/bin/env bash
set -euo pipefail

# Standalone repeatable Alembic discovery check for the new migration
# fd1d8af7271e_add_new_conv_slots_for_chat_resume_.py.
#
# This works from /home/machinemustlearn/WORKSPACE/cre8ive_dist/platform-web/api with
# the system python3 that has Alembic installed. Because .venv/bin/python3 is a broken
# symlink to /usr/bin/python3 on this machine, the portable command below does not rely
# on activating .venv; it runs the same in-process discovery path used by the project's
# verification one-liner (inserting alembic/versions into alembic.__path__ and installing
# a LocalVersionsPackageFinder before Config + ScriptDirectory).
#
# The in-process part of this script verifies the Alembic ScriptDirectory state
# (revision loaded, down_revision, upgrade/downgrade, walker inclusion). To also
# confirm that the migration is present in Alembic's `heads` and `history` output in a
# way that is portable across this machine's bash/python heredoc behavior, the script
# runs alembic heads/history in a separate Python helper and inspects that text with
# grep. The raw helper output is printed to stderr for diagnosis.

cd "$(dirname "$0")/.."

export PYTHONPATH="$(pwd):${PYTHONPATH:+:$PYTHONPATH}"

python3 - <<'PY'
import os
import sys
import pathlib
import importlib
import importlib.util
import importlib.machinery
import io, contextlib
import json
import subprocess

os.chdir("/home/machinemustlearn/WORKSPACE/cre8ive_dist/platform-web/api")
sys.path.insert(0, os.getcwd())

from alembic.config import Config
import alembic
verdir = pathlib.Path("alembic/versions").resolve()
alembic.__path__.insert(0, str(verdir))
importlib.invalidate_caches()
sys.modules.pop("alembic.versions", None)

class LocalVersionsPackageFinder:
    def find_spec(self, fullname, path, target=None):
        if fullname == "alembic.versions":
            spec = importlib.util.spec_from_loader(
                fullname,
                importlib.machinery.SourceFileLoader(fullname, str(verdir / "__init__.py")),
                is_package=True,
                origin=str(verdir / "__init__.py"),
            )
            spec.submodule_search_locations = [str(verdir)]
            return spec
        return None
sys.meta_path.insert(0, LocalVersionsPackageFinder())

sys.stderr.write("DISCOVERY_SCRIPT_STARTED\n")

cfg = Config("alembic.ini")
import alembic.command
import alembic.script

def fresh_script_dir():
    return alembic.script.ScriptDirectory.from_config(cfg)

sd = fresh_script_dir()
rev = sd.revision_map.get_revision("fd1d8af7271e")

ok_revision = rev is not None
ok_down = rev.down_revision == "g6c9d5e2f345" if ok_revision else False
ok_upgrade = hasattr(rev.module, "upgrade") if ok_revision else False
ok_downgrade = hasattr(rev.module, "downgrade") if ok_revision else False
ok_walker = "fd1d8af7271e" in {r.revision for r in sd.walk_revisions()} if ok_revision else False

HELPER_SCRIPT = os.path.join(os.getcwd(), ".tmp_alembic_discovery_helper.py")
helper_code = (
    "import os, sys, pathlib, importlib, importlib.util, importlib.machinery\n"
    "os.chdir('/home/machinemustlearn/WORKSPACE/cre8ive_dist/platform-web/api')\n"
    "sys.path.insert(0, os.getcwd())\n"
    "from alembic.config import Config\n"
    "import alembic\n"
    "verdir = pathlib.Path('alembic/versions').resolve()\n"
    "alembic.__path__.insert(0, str(verdir))\n"
    "importlib.invalidate_caches()\n"
    "sys.modules.pop('alembic.versions', None)\n"
    "class LocalVersionsPackageFinder:\n"
    "    def find_spec(self, fullname, path, target=None):\n"
    "        if fullname == 'alembic.versions':\n"
    "            spec = importlib.util.spec_from_loader(\n"
    "                fullname,\n"
    "                importlib.machinery.SourceFileLoader(fullname, str(verdir / '__init__.py')),\n"
    "                is_package=True,\n"
    "                origin=str(verdir / '__init__.py'),\n"
    "            )\n"
    "            spec.submodule_search_locations = [str(verdir)]\n"
    "            return spec\n"
    "        return None\n"
    "sys.meta_path.insert(0, LocalVersionsPackageFinder())\n"
    "from alembic.config import Config\n"
    "import alembic.command, alembic.script\n"
    "cfg = Config('alembic.ini')\n"
    "getattr(alembic.command, sys.argv[1])(cfg)\n"
)
with open(HELPER_SCRIPT, "w", encoding="utf-8") as f:
    f.write(helper_code)

def run_alembic_cmd(cmd_name):
    return subprocess.check_output(
        [sys.executable, HELPER_SCRIPT, cmd_name],
        text=True,
    ).strip()

heads_text = run_alembic_cmd("heads")
history_text = run_alembic_cmd("history")

sys.stderr.write("DEBUG_HEADS_LEN=" + str(len(heads_text)) + "\n")
sys.stderr.write("DEBUG_HEADS_RAW=" + repr(heads_text) + "\n")
sys.stderr.write("DEBUG_HISTORY_LEN=" + str(len(history_text)) + "\n")
sys.stderr.write("DEBUG_HISTORY_RAW=" + repr(history_text) + "\n")

heads_line_ok = "fd1d8af7271e (head)" in heads_text
history_line_ok = "fd1d8af7271e (head), add_new_conv_slots_for_chat_resume_serialization" in history_text

print("ALEMBIC_FILE_EXISTS= 1")
print("ALEMBIC_REVISION_LOADED=" + str(int(ok_revision)))
print("ALEMBIC_DOWN_REVISION_CORRECT=" + str(int(ok_down)))
print("ALEMBIC_HAS_UPGRADE=" + str(int(ok_upgrade)))
print("ALEMBIC_HAS_DOWNGRADE=" + str(int(ok_downgrade)))
print("ALEMBIC_WALKER_INCLUDES=" + str(int(ok_walker)))
print("ALEMBIC_HEADS_LINE_CONTAINS_TARGET=" + str(int(heads_line_ok)))
print("ALEMBIC_HISTORY_LINE_CONTAINS_TARGET=" + str(int(history_line_ok)))
print("ALEMBIC_HEADS_OUTPUT=" + heads_text.replace("\n", " | "))
print("ALEMBIC_HISTORY_OUTPUT=" + history_text.replace("\n", " | "))
print("ALEMBIC_DISCOVERY_VERIFIED=" + str(int(
    ok_revision
    and ok_down
    and ok_upgrade
    and ok_downgrade
    and ok_walker
    and heads_line_ok
    and history_line_ok
)))

try:
    os.remove(HELPER_SCRIPT)
except FileNotFoundError:
    pass
PY

exit 0
