from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from hk_equity_snapshot_pipelines.input_sources import (
    DEFAULT_REMOTE_COPY_TIMEOUT_SECONDS,
    _default_https_copy,
    resolve_hk_snapshot_inputs,
    resolve_input_source,
    source_needs_gcloud,
    write_shell_env,
)


def _write_csv(path: Path) -> Path:
    path.write_text("symbol,sector\n00001,Financials\n", encoding="utf-8")
    return path


def test_resolve_input_source_accepts_local_csv(tmp_path):
    source = _write_csv(tmp_path / "factor_snapshot.csv")

    resolved = resolve_input_source(source, output_dir=tmp_path / "resolved", stem="factor_snapshot")

    assert resolved == source


def test_resolve_input_source_rejects_non_csv_local_file(tmp_path):
    source = tmp_path / "factor_snapshot.json"
    source.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported factor_snapshot file suffix"):
        resolve_input_source(source, output_dir=tmp_path / "resolved", stem="factor_snapshot")


def test_resolve_input_source_copies_gcs_uri_with_fake_copy(tmp_path):
    def fake_copy(source: str, target: Path) -> None:
        assert source == "gs://bucket/path/factor_snapshot.csv"
        _write_csv(target)

    resolved = resolve_input_source(
        "gs://bucket/path/factor_snapshot.csv",
        output_dir=tmp_path / "resolved",
        stem="factor_snapshot",
        gcs_copy=fake_copy,
    )

    assert resolved == tmp_path / "resolved" / "factor_snapshot.csv"
    assert resolved.exists()
    assert source_needs_gcloud("gs://bucket/path/factor_snapshot.csv") is True


def test_resolve_input_source_copies_https_uri_with_fake_copy(tmp_path):
    def fake_copy(source: str, target: Path) -> None:
        assert source == "https://example.com/factor_snapshot.csv"
        _write_csv(target)

    resolved = resolve_input_source(
        "https://example.com/factor_snapshot.csv",
        output_dir=tmp_path / "resolved",
        stem="factor_snapshot",
        https_copy=fake_copy,
    )

    assert resolved == tmp_path / "resolved" / "factor_snapshot.csv"
    assert resolved.exists()


def test_default_https_copy_uses_timeout_and_streams_response(monkeypatch, tmp_path):
    calls: list[tuple[str, float]] = []

    class FakeResponse:
        def __init__(self) -> None:
            self._payload = b"symbol,sector\n00001,Financials\n"

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self, size: int = -1) -> bytes:
            payload, self._payload = self._payload, b""
            return payload

    def fake_urlopen(request, *, timeout: float):
        calls.append((request.full_url, timeout))
        return FakeResponse()

    monkeypatch.setattr("hk_equity_snapshot_pipelines.input_sources.urlopen", fake_urlopen)
    target = tmp_path / "factor_snapshot.csv"

    _default_https_copy("https://example.com/factor_snapshot.csv", target)

    assert target.read_text(encoding="utf-8") == "symbol,sector\n00001,Financials\n"
    assert calls == [("https://example.com/factor_snapshot.csv", DEFAULT_REMOTE_COPY_TIMEOUT_SECONDS)]


def test_resolve_input_source_rejects_secret_like_remote_uri(tmp_path):
    with pytest.raises(ValueError, match="must not contain token"):
        resolve_input_source(
            "https://example.com/factor_snapshot.csv?token=abc",
            output_dir=tmp_path / "resolved",
            stem="factor_snapshot",
        )


def test_resolve_hk_snapshot_inputs_writes_shell_env(tmp_path):
    source = _write_csv(tmp_path / "factor_snapshot.csv")
    resolved = resolve_hk_snapshot_inputs(factor_snapshot_source=source, output_dir=tmp_path / "resolved")
    env_path = tmp_path / "resolved.env"

    write_shell_env(env_path, resolved)

    assert env_path.read_text(encoding="utf-8").startswith("FACTOR_SNAPSHOT_PATH=")
    assert str(source) in env_path.read_text(encoding="utf-8")


def test_resolve_hk_snapshot_inputs_cli(tmp_path):
    source = _write_csv(tmp_path / "factor_snapshot.csv")
    env_path = tmp_path / "resolved.env"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hk_equity_snapshot_pipelines.input_sources",
            "--factor-snapshot",
            str(source),
            "--output-dir",
            str(tmp_path / "resolved"),
            "--env-output",
            str(env_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "resolved factor_snapshot" in completed.stdout
    assert env_path.exists()
