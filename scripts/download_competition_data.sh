#!/usr/bin/env bash
# download_competition_data.sh
#
# Place GEMS Prize Challenge competition data into data/ so that
#   python scripts/prepare_data.py
# makes the full train -> inference -> validate pipeline ready.
#
# IMPORTANT: DrivenData requires authentication for the competition data tab.
#   https://www.drivendata.org/competitions/306/competition-doe-gems/data/
#   (verified: redirects to login; no anonymous download)
#
# This script therefore DOES NOT fetch competition data automatically.  It
# documents the exact steps and the public mirrors discovered in the issue
# tracker.  Run this on any machine with DrivenData credentials.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$REPO_ROOT/data"
mkdir -p "$DATA_DIR"

echo "== GEMS Prize Challenge data placement =="
echo "Competition page : https://www.drivendata.org/competitions/306/competition-doe-gems/"
echo "Data tab         : https://www.drivendata.org/competitions/306/competition-doe-gems/data/  (login required)"
echo "Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution"
echo
echo "Steps:"
echo "  1. Log in to DrivenData and accept the competition rules."
echo "  2. From the data tab, download into data/:"
echo "       training_features.tif   multi-band feature stack (EPSG:32611, 100 m)"
echo "       labels.tif              ground-truth fault raster (training labels)"
echo "       sample_submission.tif   official submission format template (all zeros)"
echo "       existing_faults.tif     catalogue faults (USGS + INGENIOUS)"
echo "       1m_DEM_links.csv        links to 1 m DEM tiles (USGS 3DEP)"
echo "  3. Run: python scripts/prepare_data.py"
echo
echo "Public mirrors reported in competition issue attachments (unverified,"
echo "do not substitute for organizer-provided data; hashes not available):"
echo "  GEMS_96647.pdf                                                  (rules PDF)"
echo "  example_submission.tif                                          (format template)"
echo "  existing_faults.tif"
echo "  gems-geodawn-numerical-features.tif"
echo "  Digital-elevation-model-links-JSON.pdf"
echo "  Source: https://gdr.openei.org/submissions/1391 (DOE Geothermal Data Repository)"
echo
echo "Official data sources referenced by the competition:"
echo "  GeoDAWN survey (USGS):  https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"
echo "  GeoDAWN area map (USGS ScienceBase): https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7"
echo "  INGENIOUS project (GBCGE): https://gbcge.org/current-projects/ingenious/"
echo "  CRS definition (EPSG 32611): https://epsg.io/32611"
echo "  Tversky index: https://en.wikipedia.org/wiki/Tversky_index"
echo
echo "Sandbox note: in this sandbox, drivendata.org, usgs.gov, sciencebase.gov,"
echo "gdr.openei.org and dropbox.com are not reachable from bash, so competition"
echo "data must be staged on an unrestricted machine and copied into data/ here."
echo
echo "Next: python scripts/prepare_data.py"
