#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from hk_equity_snapshot_pipelines.snapshot_readiness import build_snapshot_readiness, build_snapshot_readiness_matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Print HK snapshot profile readiness plan.")
    parser.add_argument("--profile")
    parser.add_argument("--all", action="store_true", help="Print readiness for every snapshot profile")
    parser.add_argument("--platform", required=True, choices=("ibkr", "longbridge"))
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    args = parser.parse_args()

    if args.all:
        payload = build_snapshot_readiness_matrix(platform_id=args.platform)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return
        print(f"platform={payload['platform']}")
        print(f"status={payload['status']}")
        print(f"live_enable_gate={payload['live_enable_gate']}")
        print(f"profile_count={payload['profile_count']}")
        print(f"blocked_profile_count={payload['blocked_profile_count']}")
        for profile in payload["profiles"]:
            print(f"- {profile['profile']}: runtime_enabled={profile['runtime_enabled']}")
        return

    if not args.profile:
        parser.error("--profile is required unless --all is set")

    payload = build_snapshot_readiness(args.profile, platform_id=args.platform)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"profile={payload['profile']}")
    print(f"platform={payload['platform']}")
    print(f"status={payload['status']}")
    print(f"runtime_enabled={payload['runtime_enabled']}")
    print("blocking_reasons:")
    for reason in payload["blocking_reasons"]:
        print(f"- {reason}")
    print("profile_live_enablement_requirements:")
    for requirement in payload["profile_live_enablement_requirements"]:
        print(f"- {requirement}")


if __name__ == "__main__":
    main()
