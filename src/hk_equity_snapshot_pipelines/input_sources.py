from __future__ import annotations

import argparse
import shlex
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve

from .evidence_uri_policy import SENSITIVE_EVIDENCE_URI_MARKERS

SUPPORTED_SNAPSHOT_SUFFIXES = frozenset({".csv"})

CopyFn = Callable[[str, Path], None]


@dataclass(frozen=True)
class ResolvedHkSnapshotInputs:
    factor_snapshot_path: Path


def is_gcs_uri(source: str) -> bool:
    return str(source or "").strip().startswith("gs://")


def is_https_uri(source: str) -> bool:
    return str(source or "").strip().lower().startswith("https://")


def source_needs_gcloud(source: str | None) -> bool:
    return is_gcs_uri(str(source or ""))


def _reject_sensitive_remote_source(source: str) -> None:
    normalized = str(source or "").strip().lower()
    if not (is_gcs_uri(normalized) or is_https_uri(normalized)):
        return
    for marker in SENSITIVE_EVIDENCE_URI_MARKERS:
        if marker in normalized:
            raise ValueError("remote input URI must not contain token/password/signature-like query parameters")


def _default_gcs_copy(source: str, target: Path) -> None:
    subprocess.run(["gcloud", "storage", "cp", source, str(target)], check=True)


def _default_https_copy(source: str, target: Path) -> None:
    urlretrieve(source, target)  # noqa: S310 - operator-supplied HTTPS data source URL.


def _source_suffix(source: str, *, allowed_suffixes: frozenset[str], default_suffix: str) -> str:
    parsed = urlparse(str(source).strip())
    candidate_path = parsed.path or str(source).strip()
    suffix = Path(candidate_path).suffix.lower()
    return suffix if suffix in allowed_suffixes else default_suffix


def resolve_input_source(
    source: str | Path,
    *,
    output_dir: str | Path,
    stem: str,
    allowed_suffixes: frozenset[str] = SUPPORTED_SNAPSHOT_SUFFIXES,
    default_suffix: str = ".csv",
    gcs_copy: CopyFn | None = None,
    https_copy: CopyFn | None = None,
) -> Path:
    source_text = str(source or "").strip()
    if not source_text:
        raise EnvironmentError(f"{stem} source is required")

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    _reject_sensitive_remote_source(source_text)

    if is_gcs_uri(source_text):
        target = output_root / f"{stem}{_source_suffix(source_text, allowed_suffixes=allowed_suffixes, default_suffix=default_suffix)}"
        (gcs_copy or _default_gcs_copy)(source_text, target)
        if not target.exists():
            raise FileNotFoundError(f"resolved GCS input was not created: {target}")
        return target

    if is_https_uri(source_text):
        target = output_root / f"{stem}{_source_suffix(source_text, allowed_suffixes=allowed_suffixes, default_suffix=default_suffix)}"
        (https_copy or _default_https_copy)(source_text, target)
        if not target.exists():
            raise FileNotFoundError(f"resolved HTTPS input was not created: {target}")
        return target

    local_path = Path(source_text).expanduser()
    if not local_path.exists():
        raise FileNotFoundError(f"input file not found: {local_path}")
    if not local_path.is_file():
        raise FileNotFoundError(f"input path is not a file: {local_path}")
    suffix = local_path.suffix.lower()
    if suffix not in allowed_suffixes:
        expected = ", ".join(sorted(allowed_suffixes))
        raise ValueError(f"unsupported {stem} file suffix {suffix!r}; expected one of: {expected}")
    return local_path


def resolve_hk_snapshot_inputs(
    *,
    factor_snapshot_source: str | Path,
    output_dir: str | Path,
    gcs_copy: CopyFn | None = None,
    https_copy: CopyFn | None = None,
) -> ResolvedHkSnapshotInputs:
    factor_snapshot_path = resolve_input_source(
        factor_snapshot_source,
        output_dir=output_dir,
        stem="factor_snapshot",
        gcs_copy=gcs_copy,
        https_copy=https_copy,
    )
    return ResolvedHkSnapshotInputs(factor_snapshot_path=factor_snapshot_path)


def write_shell_env(path: str | Path, resolved: ResolvedHkSnapshotInputs) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"FACTOR_SNAPSHOT_PATH={shlex.quote(str(resolved.factor_snapshot_path))}"]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve HK snapshot input data sources into local files.")
    parser.add_argument(
        "--factor-snapshot",
        required=True,
        help="Local, gs://, or https:// factor snapshot CSV source.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for downloaded remote inputs.")
    parser.add_argument("--env-output", help="Optional shell env file to write resolved FACTOR_SNAPSHOT_PATH.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    resolved = resolve_hk_snapshot_inputs(
        factor_snapshot_source=args.factor_snapshot,
        output_dir=args.output_dir,
    )
    print(f"resolved factor_snapshot -> {resolved.factor_snapshot_path}")
    if args.env_output:
        write_shell_env(args.env_output, resolved)
        print(f"wrote resolved env -> {args.env_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
