"""
Dependency resolution and installation planning
"""

import logging
from typing import List, Dict, Set, Optional
from collections import deque

from ..models.tool import Tool

logger = logging.getLogger(__name__)

class DependencyResolver:
    """Resolves tool dependencies and creates installation plans"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.installed: Set[str] = set()
    
    def set_tools(self, tools: Dict[str, Tool], installed: Set[str] = None):
        """Set the available tools"""
        self.tools = tools
        self.installed = installed or set()
    
    def resolve(self, tool_ids: List[str]) -> List[List[str]]:
        """
        Resolve dependencies and return installation order
        
        Args:
            tool_ids: List of tool IDs to install
            
        Returns:
            List of batches (each batch is a list of tool IDs that can be installed in parallel)
        """
        # Build dependency graph
        graph = {}
        all_needed = set()
        
        # Collect all needed tools (including dependencies)
        queue = deque(tool_ids)
        while queue:
            tool_id = queue.popleft()
            if tool_id in all_needed or tool_id in self.installed:
                continue
            
            all_needed.add(tool_id)
            tool = self.tools.get(tool_id)
            if tool and tool.dependencies:
                for dep in tool.dependencies:
                    if dep not in all_needed and dep not in self.installed:
                        queue.append(dep)
        
        # Build dependency edges
        for tool_id in all_needed:
            graph[tool_id] = set()
            tool = self.tools.get(tool_id)
            if tool and tool.dependencies:
                for dep in tool.dependencies:
                    if dep in all_needed:
                        graph[tool_id].add(dep)
        
        # Topological sort with batches
        return self._topological_sort_batches(graph)
    
    def _topological_sort_batches(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Sort tools into batches for parallel installation"""
        if not graph:
            return []
        
        # Calculate in-degree
        in_degree = {node: 0 for node in graph}
        for node, deps in graph.items():
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1
        
        batches = []
        remaining = set(graph.keys())
        
        while remaining:
            # Find nodes with no dependencies (in-degree 0)
            batch = [node for node in remaining if in_degree.get(node, 0) == 0]
            
            if not batch:
                # Circular dependency detected
                logger.error("Circular dependency detected")
                break
            
            batches.append(batch)
            
            # Remove batch nodes from graph
            for node in batch:
                remaining.remove(node)
                # Reduce in-degree of dependents
                for other in remaining:
                    if node in graph.get(other, set()):
                        in_degree[other] = in_degree.get(other, 0) - 1
        
        return batches
    
    def get_install_plan(self, tool_ids: List[str]) -> Dict:
        """
        Get a complete installation plan
        
        Returns:
            Dict with plan details
        """
        batches = self.resolve(tool_ids)
        
        # Flatten the batches for total count
        all_tools = []
        for batch in batches:
            all_tools.extend(batch)
        
        total_size = 0
        tools_details = []
        
        for tool_id in all_tools:
            tool = self.tools.get(tool_id)
            if tool:
                tools_details.append({
                    "id": tool.id,
                    "name": tool.name,
                    "version": tool.version,
                    "requires_admin": tool.requires_admin
                })
                total_size += 1  # Could add actual size tracking later
        
        return {
            "batches": batches,
            "tools": tools_details,
            "total_tools": len(tools_details),
            "needs_admin": any(tool["requires_admin"] for tool in tools_details)
        }