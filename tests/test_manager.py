"""Tests for llm_fuzz_monitor.storage.manager — storage & session management."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from llm_fuzz_monitor.core.models import (
    CIFuzzSparkSession,
    LLMInteraction,
    LLMProvider,
    SessionStatus,
)
from llm_fuzz_monitor.storage.manager import (
    AdvancedTextDataManager,
    ConcurrentSessionManager,
)


# ── AdvancedTextDataManager ────────────────────────────────


class TestAdvancedTextDataManager:
    def test_init_creates_subdirs(self, tmp_data_dir):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            assert (tmp_data_dir / "sessions").is_dir()
            assert (tmp_data_dir / "llm_interactions").is_dir()
            assert (tmp_data_dir / "fuzz_drivers").is_dir()
        finally:
            mgr.shutdown(timeout=5)

    def test_save_and_load_session(self, tmp_data_dir, sample_llm_interaction):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            session = CIFuzzSparkSession(
                session_id="round-trip-test",
                pid=9999,
                start_time=datetime.now(),
            )
            mgr.save_session(session, sync=True)
            # Verify the session file was persisted to disk
            session_file = tmp_data_dir / "sessions" / "round-trip-test.json"
            assert session_file.exists()
        finally:
            mgr.shutdown(timeout=5)

    def test_list_sessions_empty(self, tmp_data_dir):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            sessions = mgr.list_sessions()
            assert isinstance(sessions, list)
        finally:
            mgr.shutdown(timeout=5)

    def test_get_storage_statistics(self, tmp_data_dir):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            stats = mgr.get_storage_statistics()
            assert isinstance(stats, dict)
        finally:
            mgr.shutdown(timeout=5)

    def test_save_llm_interaction(self, tmp_data_dir, sample_llm_interaction):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            interaction = LLMInteraction(**sample_llm_interaction)
            mgr.save_llm_interaction(interaction, sync=True)
            # Verify the file was created in the llm_interactions subdir
            files = list((tmp_data_dir / "llm_interactions").glob("*.json*"))
            assert len(files) >= 1
        finally:
            mgr.shutdown(timeout=5)


# ── ConcurrentSessionManager ──────────────────────────────


class TestConcurrentSessionManager:
    def test_add_and_get_session(self, tmp_data_dir):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            csm = ConcurrentSessionManager(data_manager=mgr, max_sessions=5)
            session = CIFuzzSparkSession(
                session_id="csm-test",
                pid=1111,
                start_time=datetime.now(),
            )
            added = csm.add_session(session)
            assert added is True
            retrieved = csm.get_session("csm-test")
            assert retrieved is not None
            assert retrieved.pid == 1111
        finally:
            mgr.shutdown(timeout=5)

    def test_session_count(self, tmp_data_dir):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            csm = ConcurrentSessionManager(data_manager=mgr, max_sessions=5)
            assert csm.get_session_count() == 0
            session = CIFuzzSparkSession(
                session_id="count-test",
                pid=2222,
                start_time=datetime.now(),
            )
            csm.add_session(session)
            assert csm.get_session_count() == 1
        finally:
            mgr.shutdown(timeout=5)

    def test_remove_session(self, tmp_data_dir):
        mgr = AdvancedTextDataManager(
            data_dir=tmp_data_dir,
            enable_compression=False,
            enable_async=False,
        )
        try:
            csm = ConcurrentSessionManager(data_manager=mgr, max_sessions=5)
            session = CIFuzzSparkSession(
                session_id="remove-test",
                pid=3333,
                start_time=datetime.now(),
            )
            csm.add_session(session)
            csm.remove_session("remove-test")
            assert csm.get_session("remove-test") is None
        finally:
            mgr.shutdown(timeout=5)
