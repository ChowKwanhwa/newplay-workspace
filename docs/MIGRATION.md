# New Mac setup and verification

Clone the public repository using the README commands, install the Brewfile tools and run `sh scripts/bootstrap.sh`. Python packages install into a new local virtual environment from `uv.lock`; never copy an old environment.

Run the migration unit tests, design baseline tests, resource-library Node tests and local browser font check. The font check serves only the bundled design directory on a temporary loopback port, blocks non-local browser requests and writes results under the ignored local-check directory. It performs no login, messaging, transaction or deployment.

Figma access requires connecting the user's account independently. GitHub login, cloud service credentials, browser sessions, custom assistant integrations and private archives are not restored by cloning. Configure only required services using their own secure authorization flow; never commit credentials.

All four approved font families and their OFL licenses are normal Git files. Git attributes preserve their original bytes; Git LFS and system font installation are not required. Other page-specific assets not bundled here must be exported from the authorized current design or supplied separately by the user.

The public repository does not contain all historical production scripts or materials. The read-only migration checker remains available, but a public clone alone cannot rebuild excluded private deliverables or verify historical upload state. No claim of complete private-workspace migration is made.

Do not run every script indiscriminately. Library rebuilding requires separately supplied approved materials. Keep cloud deployment configuration local, and do not deploy as a setup smoke test.
