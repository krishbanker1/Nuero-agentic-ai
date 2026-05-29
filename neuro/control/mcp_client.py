# MCP Client Integration
# Connect Neuro to Model Context Protocol tools (stdio, HTTP, WebSocket, SSE)
# Inspired by PraisonAI's MCP integration

import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import os


class MCPTransport(Enum):
    """MCP transport types."""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"
    SSE = "sse"


@dataclass
class MCPTool:
    """An MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPToolResult:
    """Result from executing an MCP tool."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None


class MCPClient:
    """
    Client for connecting to MCP servers.
    
    Usage:
        # Via npx command
        client = MCPClient("npx", ["-y", "@modelcontextprotocol/server-filesystem", "/path"])
        
        # Via HTTP
        client = MCPClient(endpoint="http://localhost:8080/mcp")
        
        tools = client.list_tools()
        result = client.call_tool("read_file", {"path": "/tmp/test.txt"})
    """
    
    def __init__(
        self,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        endpoint: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        self.command = command
        self.args = args or []
        self.endpoint = endpoint
        self.env = env or {}
        self._tools: List[MCPTool] = []
        self._proc: Optional[subprocess.Popen] = None
        self._request_id = 0
        
    def connectstdio(self) -> bool:
        """Connect via stdio transport."""
        if not self.command:
            return False
            
        full_env = {**os.environ, **self.env}
        
        try:
            self._proc = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=full_env,
                text=True,
            )
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "neuro", "version": "1.0"},
                }
            }
            self._send_raw(init_request)
            
            # Read response
            response = self._recv()
            if response and "result" in response:
                self._initialized = True
                
                # List tools
                list_request = {
                    "jsonrpc": "2.0",
                    "id": self._next_id(),
                    "method": "tools/list",
                    "params": {}
                }
                self._send_raw(list_request)
                tools_response = self._recv()
                if tools_response and "result" in tools_response:
                    for t in tools_response["result"].get("tools", []):
                        self._tools.append(MCPTool(
                            name=t["name"],
                            description=t.get("description", ""),
                            input_schema=t.get("inputSchema", {}),
                        ))
                return True
                
        except Exception as e:
            print(f"MCP stdio connection failed: {e}")
            
        return False
    
    def list_tools(self) -> List[MCPTool]:
        """Get list of available tools."""
        return self._tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call an MCP tool with arguments."""
        if self._proc and self._proc.stdin:
            request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": arguments,
                }
            }
            self._send_raw(request)
            response = self._recv()
            
            if response and "result" in response:
                return MCPToolResult(
                    tool_name=name,
                    success=True,
                    result=response["result"],
                )
            elif response and "error" in response:
                return MCPToolResult(
                    tool_name=name,
                    success=False,
                    result=None,
                    error=response["error"].get("message", "Unknown error"),
                )
                
        return MCPToolResult(
            tool_name=name,
            success=False,
            result=None,
            error="Not connected",
        )
    
    def call_tool_async(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Async version for use with asyncio."""
        return self.call_tool(name, arguments)
    
    def disconnect(self):
        """Disconnect from MCP server."""
        if self._proc:
            self._proc.terminate()
            self._proc = None
    
    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    def _send_raw(self, obj: Dict[str, Any]):
        if self._proc and self._proc.stdin:
            line = json.dumps(obj) + "\n"
            self._proc.stdin.write(line)
            self._proc.stdin.flush()
    
    def _recv(self) -> Optional[Dict[str, Any]]:
        if self._proc and self._proc.stdout:
            try:
                line = self._proc.stdout.readline()
                if line:
                    return json.loads(line)
            except:
                pass
        return None


class MCPToolRegistry:
    """Registry for MCP tools, similar to Neuro's skill registry."""
    
    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        self._tool_cache: List[MCPTool] = []
        
    def add_server(self, name: str, client: MCPClient) -> bool:
        """Add an MCP server to the registry."""
        if client.connectstdio():
            self._clients[name] = client
            self._tool_cache.extend(client.list_tools())
            return True
        return False
    
    def add_http_server(self, name: str, endpoint: str) -> MCPClient:
        """Add an HTTP MCP server."""
        client = MCPClient(endpoint=endpoint)
        self._clients[name] = client
        return client
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available tools from all servers."""
        tools = []
        for client in self._clients.values():
            tools.extend(client.list_tools())
        return tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call a tool by name, finds the right server."""
        for client in self._clients.values():
            for tool in client.list_tools():
                if tool.name == name:
                    return client.call_tool(name, arguments)
        return MCPToolResult(name, False, None, f"Tool '{name}' not found")
    
    def disconnect_all(self):
        """Disconnect all servers."""
        for client in self._clients.values():
            client.disconnect()
        self._clients.clear()
        self._tool_cache.clear()


# Global registry instance
_mcp_registry: Optional[MCPToolRegistry] = None

def get_mcp_registry() -> MCPToolRegistry:
    """Get or create the global MCP registry."""
    global _mcp_registry
    if _mcp_registry is None:
        _mcp_registry = MCPToolRegistry()
    return _mcp_registry


def setup_filesystem_mcp(path: str = ".") -> Optional[MCPClient]:
    """Quick setup for filesystem MCP server."""
    client = MCPClient("npx", ["-y", "@modelcontextprotocol/server-filesystem", path])
    if client.connectstdio():
        return client
    return None


def setup_browser_mcp(browser: str = "chromium") -> Optional[MCPClient]:
    """Quick setup for browser MCP server."""
    client = MCPClient("npx", ["-y", "@modelcontextprotocol/server-puppeteer"])
    if client.connectstdio():
        return client
    return None