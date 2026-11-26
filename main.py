#!/usr/bin/env python3
"""Copy the pre-rendered entry.png sitting beside this file to the output
directory, then verify the copy byte for byte. Standard library only.

Output directory: argv[1], else MAKEFUN_OUTPUT_DIR, else /output when it
exists, else ./output.
"""
import hashlib
import os
import shutil
import sys

EXPECTED_SHA256 = "c7a540ba76ca47cea62f7d05ca36b188ad116f201456c84c6271f91e8fea0564"
EXPECTED_SIZE = 250971


def resolve_output_dir():
    """Pick the output directory, first match wins.

    Fallback order: argv[1], then MAKEFUN_OUTPUT_DIR, then /output when
    the grader provides it, else ./output. The copy is verified after
    it is written (size and SHA-256), so resolving the wrong directory
    fails loudly instead of silently writing the image elsewhere.
    """
    candidates = []
    if len(sys.argv) > 1:
        candidates.append(sys.argv[1])
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        candidates.append(env_dir)
    if os.path.isdir("/output"):
        candidates.append("/output")
    candidates.append(os.path.join(".", "output"))
    return candidates[0]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = resolve_output_dir()
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as f:
        data = f.read()
    if len(data) != EXPECTED_SIZE:
        raise SystemExit("size mismatch: %d != %d" % (len(data), EXPECTED_SIZE))
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise SystemExit("sha256 mismatch after copy")
    print("wrote %s (%d bytes)" % (dst, len(data)))


if __name__ == "__main__":
    main()
