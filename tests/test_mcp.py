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

    def test_tool_call(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("pathlib.Path.home", return_value=Path(td)):
                service=ForgeService(load_config(Path(td)/"config.toml"))
            result=handle(service,{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"forge_version","arguments":{}}})
            self.assertFalse(result["result"]["isError"])


if __name__ == "__main__": unittest.main()
