# CI and releases

## Daily CI

CI runs for pushes to main/dev and pull requests targeting them. It checks the
release helpers, Bash syntax, and workflow syntax, then builds and smoke-tests
a Linux Python 3.11 wheel and cross-compiles the MaixCAM wheel. It never publishes
a Release or uploads packages to PyPI. Superseded daily runs are cancelled.

## Stable releases

1. Update maix/version.py and review .github/release-config.json.
2. Merge the release changes to main.
3. Create an annotated matching tag, for example:
   git tag -a v4.12.7 -m "Release MaixPy v4.12.7"
   git push origin refs/tags/v4.12.7
4. Wait for the Release workflow. A manually published GitHub Release is not
   required and does not trigger another build.

The tag must match the source version. Only stable vMAJOR.MINOR.PATCH tags are
accepted. Existing tags are never moved automatically.

The pipeline builds six Linux wheels (Python 3.8 through 3.13), the MaixCAM
wheel, MaixCAM and MaixCAM-Pro images, and documentation. MaixCAM2 images are
not built by this pipeline. Each job stores its output as a GitHub Actions
artifact, even before publication. Matrix failures do not cancel other jobs.

After every build succeeds, the publication job verifies the complete artifact
set, native wheel architectures and versions, per-job provenance, compressed
images, and SHA-256 checksums. It uploads to a draft Release and publishes only
after all assets are uploaded. Build jobs have read-only repository permissions;
only the final publication job has contents:write.

Published releases are not overwritten. Failed draft uploads can be retried.
A failure that occurs before publication leaves no newly published Release.
GitHub Release and PyPI publication are separate operations.

## Inputs and reproducibility

Ubuntu 22.04 and CMake 3.22.1 are fixed. Build-tool versions are listed in
.github/requirements-build.txt. The SDK uses a full commit SHA, not a moving
branch. A small checked-in compatibility patch adds the missing cstdint header
and explicitly qualified integer types to the pinned SDK's yaml-cpp source.

The base image and builtin archive URLs and SHA-256 hashes are pinned in
.github/release-config.json. Updating the SDK or images is a reviewed source
change. In particular, the current base is the official 20251230 image:
a local image on a developer workstation is NOT automatically used in CI.
The builtin archive is pinned to v4.12.5 and is also carried into the new
Release so native download tools can find it after publication.

Native gen_os.sh/update_img.sh remain the image packaging entry points.
Build-info JSON files record source, SDK, CI revision, and artifact hashes.
release-manifest.json and sha256sum_files.txt accompany the final assets.
APT repositories and documentation plugins are not fully locked; this is
provenance-controlled publishing, not a claim of byte-for-byte reproducibility.

## Manual rebuild and recovery

Run Release from Actions, choose the branch containing the new workflow,
and enter an existing tag. Leave publish=false to build and validate without
publishing. This also supports testing the new CI against an older tag:
source and CI tooling are checked out separately and their SHAs are recorded.

For the already-published v4.12.6 created by the former workflow, first verify
its failed run has no valid assets. An authorized maintainer can change that
empty Release back to a draft before retrying with publish=true. Do not
delete or force-update its tag. Manual rebuilds use the selected CI revision's
pinned SDK and inputs, which are visible in the output manifests.

## PyPI

PyPI is a separate manual workflow after a successful GitHub Release. It
downloads and verifies release wheels and their published checksums; it does
not rebuild them. It needs the existing PYPI_TOKEN secret. Configure the pypi
environment's protection rules in GitHub if approval is desired.

Only platform-tagged Linux wheels are uploaded. The legacy MaixCAM wheel
contains RISC-V code despite its py3-none-any filename, so it remains a
GitHub Release asset and is not uploaded as a supposedly portable PyPI wheel.
