from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skyrim_forge.config import load_config
from skyrim_forge.mcp_server import TOOL_SPECS, handle
from skyrim_forge.service import ForgeService


class McpTests(unittest.TestCase):
    def test_initialize_and_tools(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("pathlib.Path.home", return_value=Path(td)):
                service=ForgeService(load_config(Path(td)/"config.toml"))
            response=handle(service,{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25"}})
            self.assertEqual(response["result"]["protocolVersion"],"2025-11-25")
            listed=handle(service,{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
            self.assertEqual(len(listed["result"]["tools"]),len(TOOL_SPECS))
            self.assertGreaterEqual(len(TOOL_SPECS),18)


    def test_fomod_surface_is_exposed(self):
        expected = {
            "forge_fomod_validate",
            "forge_fomod_plan_validate",
            "forge_fomod_build",
            "forge_fomod_scaffold",
            "forge_fomod_simulate",
        }
        self.assertTrue(expected.issubset(TOOL_SPECS))
        with tempfile.TemporaryDirectory() as td:
            with patch("pathlib.Path.home", return_value=Path(td)):
                service = ForgeService(load_config(Path(td) / "config.toml"))
            resources = handle(service, {"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}})
            uris = {item["uri"] for item in resources["result"]["resources"]}
            self.assertIn("forge://schemas/fomod-plan", uris)
            self.assertIn("forge://docs/fomod", uris)
            prompts = handle(service, {"jsonrpc": "2.0", "id": 5, "method": "prompts/list", "params": {}})
            names = {item["name"] for item in prompts["result"]["prompts"]}
            self.assertIn("build_fomod_installer", names)


    def test_nexus_publication_surface_is_exposed(self):
        expected = {
            "forge_nexus_policy_status",
            "forge_nexus_scaffold",
            "forge_nexus_plan_validate",
            "forge_nexus_audit",
            "forge_nexus_build",
            "forge_nexus_page_render",
        }
        self.assertTrue(expected.issubset(TOOL_SPECS))
        with tempfile.TemporaryDirectory() as td:
            with patch("pathlib.Path.home", return_value=Path(td)):
                service = ForgeService(load_config(Path(td) / "config.toml"))
            resources = handle(service, {"jsonrpc": "2.0", "id": 6, "method": "resources/list", "params": {}})
            uris = {item["uri"] for item in resources["result"]["resources"]}
            self.assertIn("forge://schemas/nexus-publication-plan", uris)
            self.assertIn("forge://docs/nexus-publication", uris)
            self.assertIn("forge://references/nexus-policy-lock", uris)
            prompts = handle(service, {"jsonrpc": "2.0", "id": 7, "method": "prompts/list", "params": {}})
            names = {item["name"] for item in prompts["result"]["prompts"]}
            self.assertIn("prepare_nexus_release", names)

    def test_tool_call(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("pathlib.Path.home", return_value=Path(td)):
                service=ForgeService(load_config(Path(td)/"config.toml"))
            result=handle(service,{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"forge_version","arguments":{}}})
            self.assertFalse(result["result"]["isError"])


if __name__ == "__main__": unittest.main()
