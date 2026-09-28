"""Minimal App Store Connect API helper for the Mac App Store build.

Environment:
    ASC_KEY_ID       e.g. 33P5W93GJQ
    ASC_ISSUER_ID    issuer UUID from App Store Connect > Users and Access > Integrations
    ASC_KEY_PATH     optional, defaults to ~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8

Commands:
    python mas/asc.py ensure-bundle-id <bundle_id> "<name>"
    python mas/asc.py ensure-profile <bundle_id> <output.provisionprofile>
    python mas/asc.py app-id <bundle_id>          # prints the App Store Connect app id, if the app exists
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt

API = "https://api.appstoreconnect.apple.com/v1"


def _token():
    key_id = os.environ["ASC_KEY_ID"]
    issuer = os.environ["ASC_ISSUER_ID"]
    key_path = os.environ.get("ASC_KEY_PATH") or os.path.expanduser(
        f"~/.appstoreconnect/private_keys/AuthKey_{key_id}.p8")
    with open(key_path, "r", encoding="utf-8") as f:
        private_key = f.read()
    now = int(time.time())
    payload = {"iss": issuer, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"}
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": key_id})


def request(method, path, body=None, params=None):
    url = path if path.startswith("http") else API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        sys.exit(f"ASC API {method} {path} failed: {error.code}\n{detail}")


def find_bundle_id(identifier):
    result = request("GET", "/bundleIds", params={"filter[identifier]": identifier, "limit": 200})
    for item in result.get("data", []):
        if item["attributes"]["identifier"] == identifier:
            return item
    return None


def ensure_bundle_id(identifier, name):
    existing = find_bundle_id(identifier)
    if existing:
        print(f"Bundle ID exists: {identifier} ({existing['attributes']['platform']})")
        return existing
    created = request("POST", "/bundleIds", {
        "data": {"type": "bundleIds", "attributes": {
            "identifier": identifier, "name": name, "platform": "MAC_OS"}}
    })["data"]
    print(f"Registered bundle ID: {identifier}")
    return created


def distribution_certificates():
    result = request("GET", "/certificates", params={"limit": 200})
    wanted = ("DISTRIBUTION", "MAC_APP_DISTRIBUTION")
    return [cert for cert in result.get("data", []) if cert["attributes"]["certificateType"] in wanted]


def ensure_profile(identifier, output_path):
    bundle = find_bundle_id(identifier)
    if bundle is None:
        sys.exit(f"Bundle ID {identifier} is not registered; run ensure-bundle-id first.")
    profile_name = f"{identifier} Mac App Store"
    result = request("GET", "/profiles", params={
        "filter[name]": profile_name, "filter[profileType]": "MAC_APP_STORE", "limit": 50})
    profiles = [p for p in result.get("data", []) if p["attributes"]["profileState"] == "ACTIVE"]
    if profiles:
        profile = profiles[0]
        print(f"Using existing profile: {profile_name}")
    else:
        certificates = distribution_certificates()
        if not certificates:
            sys.exit("No Apple Distribution certificate found in the developer account.")
        profile = request("POST", "/profiles", {
            "data": {
                "type": "profiles",
                "attributes": {"name": profile_name, "profileType": "MAC_APP_STORE"},
                "relationships": {
                    "bundleId": {"data": {"type": "bundleIds", "id": bundle["id"]}},
                    "certificates": {"data": [{"type": "certificates", "id": c["id"]} for c in certificates]},
                },
            }
        })["data"]
        print(f"Created profile: {profile_name}")
    content = base64.b64decode(profile["attributes"]["profileContent"])
    with open(output_path, "wb") as f:
        f.write(content)
    print(f"Saved: {output_path}")


def app_id(identifier):
    result = request("GET", "/apps", params={"filter[bundleId]": identifier})
    apps = result.get("data", [])
    if apps:
        print(apps[0]["id"])
    else:
        sys.exit(f"No App Store Connect app record for {identifier} yet.")


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    command, args = argv[1], argv[2:]
    if command == "ensure-bundle-id":
        ensure_bundle_id(args[0], args[1])
    elif command == "ensure-profile":
        ensure_profile(args[0], args[1])
    elif command == "app-id":
        app_id(args[0])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
