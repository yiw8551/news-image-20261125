#!/usr/bin/env python3
"""Copy the pre-rendered entry image to the grader's output directory.

Standard library only (os / sys / shutil / hashlib) -- the grader runs
Python with nothing installed, so no third-party imports are used.

Usage: python3 main.py [output_dir]

The output directory is resolved in this order:
  1. argv[1], if given
  2. the MAKEFUN_OUTPUT_DIR environment variable, if set
  3. /output, if it exists (the grader's output path)
  4. ./output, created if needed

The final file is <output_dir>/entry.png, a byte-for-byte copy of
entry.png sitting beside this script.
"""

import hashlib
import os
import shutil
import sys


def resolve_output_dir(argv):
    if len(argv) > 1 and argv[1]:
        return argv[1]
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return env_dir
    if os.path.isdir("/output"):
        return "/output"
    return os.path.join(os.getcwd(), "output")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print(f"error: source image not found: {source}", file=sys.stderr)
        return 1

    outdir = resolve_output_dir(argv)
    os.makedirs(outdir, exist_ok=True)
    destination = os.path.join(outdir, "entry.png")

    shutil.copyfile(source, destination)

    # Verify the copy is byte-identical to the source before reporting success.
    source_hash = sha256_of(source)
    dest_hash = sha256_of(destination)
    source_size = os.path.getsize(source)
    dest_size = os.path.getsize(destination)
    if dest_hash != source_hash or dest_size != source_size:
        print(
            f"error: copy verification failed for {destination} "
            f"(source sha256 {source_hash}, copied sha256 {dest_hash})",
            file=sys.stderr,
        )
        return 1

    print(f"wrote {destination} ({dest_size} bytes, sha256 {dest_hash})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
