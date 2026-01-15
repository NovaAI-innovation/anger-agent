"""
Workflow execution engine.

DESIGN REASONING:
- Workflows are sequences of steps defined in config.yaml
- Each step invokes a tool with parameters
- Steps can be conditional (if/then/else)
- Variables flow from step outputs to next step inputs
- Full audit trail of execution
"""

import re
import asyncio
import logging
from typing import Any, Dict, List, Optional
from runtime.tools import ToolRegistry
from runtime.logger import log_step_execution


class WorkflowError(Exception):
    """Raised when workflow execution fails"""
    pass


class WorkflowContext:
    """
    Execution context for a workflow.

    DESIGN: Maintains state during workflow execution.
    Tracks outputs from each step for use in later steps.
    Provides variable interpolation.
    """

    def __init__(self, workflow_id: str, trigger_data: Dict[str, Any] = None):
        """
        Initialize context.

        Args:
            workflow_id: Name of the workflow
            trigger_data: Data from the triggering event
        """
        self.workflow_id = workflow_id
        self.variables = {}
        self.step_outputs = {}

        # Add trigger data as variables
        if trigger_data:
            self.set_variable("trigger", trigger_data)

    def set_variable(self, name: str, value: Any):
        """Set a variable in context."""
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable from context."""
        return self.variables.get(name, default)

    def set_step_output(self, step_id: str, output_name: str, value: Any):
        """Store step output for later use."""
        self.step_outputs[step_id] = {output_name: value}

    def interpolate(self, value: Any) -> Any:
        """
        Interpolate variables in value.

        Replaces ${variable_name} with actual values.

        DESIGN REASONING:
        - Supports nested access: ${trigger.file_path}
        - Supports step outputs: ${step_name.output_var}
        - Clear syntax (${...} familiar from bash/templates)
        """
        if not isinstance(value, str):
            return value

        pattern = r'\$\{([^}]+)\}'

        def replacer(match):
            var_path = match.group(1)
            parts = var_path.split('.')

            # First, try step outputs (format: step_id.output_name[.nested.properties])
            if len(parts) >= 2:
                step_id = parts[0]
                if step_id in self.step_outputs:
                    # Get the output from this step
                    output_name = parts[1]
                    value = self.step_outputs[step_id].get(output_name)
                    if value is not None:
                        # Access nested properties if any
                        for part in parts[2:]:
                            if isinstance(value, dict):
                                value = value.get(part)
                                if value is None:
                                    raise ValueError(f"Undefined variable: {var_path}")
                            else:
                                raise ValueError(f"Cannot access .{part} on non-dict: {var_path}")
                        return str(value)

            # Then try variables (format: variable[.nested.properties])
            value = self.variables.get(parts[0])
            if value is None:
                raise ValueError(f"Undefined variable: {var_path}")

            for part in parts[1:]:
                if isinstance(value, dict):
                    value = value.get(part)
                    if value is None:
                        raise ValueError(f"Undefined variable: {var_path}")
                else:
                    raise ValueError(f"Cannot access .{part} on non-dict: {var_path}")

            return str(value)

        return re.sub(pattern, replacer, value)

    def interpolate_dict(self, data: Dict) -> Dict:
        """Recursively interpolate all variables in a dict."""
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.interpolate(value)
            elif isinstance(value, dict):
                result[key] = self.interpolate_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.interpolate(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


class WorkflowEngine:
    """
    Executes workflows defined in config.

    DESIGN: Responsible for:
    - Loading workflow definitions
    - Creating execution contexts
    - Executing steps in sequence
    - Handling conditionals and branching
    - Error handling per step
    - Logging all execution
    """

    def __init__(self, tool_registry: ToolRegistry, logger: logging.Logger):
        """
        Initialize engine.

        Args:
            tool_registry: Registry of available tools
            logger: Logger for execution logs
        """
        self.tools = tool_registry
        self.logger = logger

    async def execute_workflow(self, workflow_id: str, workflow_def: Dict,
                              context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow identifier
            workflow_def: Workflow definition from config
            context: Execution context

        Returns:
            Result dict with status and outputs

        DESIGN REASONING:
        - Iterates through steps in order
        - Passes context to each step
        - Collects outputs from steps
        - Handles errors per step's on_error setting
        - Returns aggregated result
        """
        logger = self.logger
        logger.info(f"Executing workflow: {workflow_id}")

        steps = workflow_def.get("steps", [])
        results = []
        failed = False

        try:
            for step_def in steps:
                step_id = step_def.get("id", "unnamed")
                logger.info(f"  Step: {step_id}")

                try:
                    # Execute the step
                    step_result = await self._execute_step(step_id, step_def, context)

                    # Store output if specified
                    output_var = step_def.get("output")
                    if output_var and step_result.get("success"):
                        context.set_step_output(step_id, output_var, step_result.get("output"))

                    results.append({
                        "step_id": step_id,
                        "success": step_result.get("success", False),
                        "output": step_result.get("output")
                    })

                    if not step_result.get("success"):
                        on_error = step_def.get("on_error", "fail")

                        if on_error == "fail":
                            logger.warning(f"    Step {step_id} failed, aborting workflow")
                            failed = True
                            break
                        elif on_error == "skip":
                            logger.info(f"    Step {step_id} failed, skipping")
                            continue
                        elif on_error == "retry":
                            logger.info(f"    Step {step_id} failed, retrying...")
                            # Simple retry (could be enhanced)
                            step_result = await self._execute_step(step_id, step_def, context)
                            results[-1]["success"] = step_result.get("success", False)
                        elif on_error == "escalate_to_llm":
                            logger.warning(f"    Step {step_id} failed, escalating to LLM (v0.2)")
                            # Will be implemented in v0.2 (Hybrid mode)
                            failed = True
                            break

                except Exception as e:
                    logger.error(f"    Step {step_id} exception: {e}")
                    failed = True
                    break

        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed with exception: {e}")
            failed = True

        return {
            "workflow_id": workflow_id,
            "success": not failed,
            "steps": results
        }

    async def _execute_step(self, step_id: str, step_def: Dict,
                           context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute a single step.

        Handles different action types:
        - tool invocation
        - conditional branching
        - loops (future)

        Args:
            step_id: Step identifier
            step_def: Step definition
            context: Execution context

        Returns:
            Step result dict
        """
        action = step_def.get("action")

        # Handle conditional
        if action == "conditional":
            return await self._execute_conditional(step_id, step_def, context)

        # Handle tool execution
        if action in self.tools.tools:
            return await self._execute_tool(step_id, action, step_def, context)

        # Unknown action
        raise WorkflowError(f"Unknown action: {action}")

    async def _execute_tool(self, step_id: str, tool_name: str, step_def: Dict,
                           context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute a tool.

        DESIGN:
        - Interpolates parameters with context variables
        - Executes tool
        - Logs result
        - Returns structured result
        """
        params = step_def.get("params", {})

        # Interpolate variables in params
        params = context.interpolate_dict(params)

        # Execute tool
        result = await self.tools.execute(tool_name, params)

        # Log execution
        status = "success" if result.get("success") else "failed"
        log_step_execution(
            self.logger, step_id, tool_name, status,
            details={"error": result.get("error") if not result.get("success") else None}
        )

        return result

    async def _execute_conditional(self, step_id: str, step_def: Dict,
                                   context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute conditional (if/then/else).

        DESIGN REASONING:
        - Evaluates condition as string expression
        - Executes if_true or if_false steps
        - Recursively handles nested conditionals
        """
        condition = step_def.get("condition")

        if not condition:
            raise WorkflowError(f"Conditional step {step_id} missing condition")

        # Interpolate condition
        condition = context.interpolate(condition)

        # Normalize JSON-style booleans to Python style for eval
        # Replace 'true', 'false', 'null' with Python equivalents
        condition = condition.replace(' true', ' True')
        condition = condition.replace('(true', '(True')
        condition = condition.replace(' false', ' False')
        condition = condition.replace('(false', '(False')
        condition = condition.replace(' null', ' None')
        condition = condition.replace('(null', '(None')

        # Simple condition evaluation
        # Supports: == != > < >= <=
        # Future: could use safer eval library
        try:
            result = eval(condition)
        except Exception as e:
            raise WorkflowError(f"Invalid condition: {condition}: {e}")

        # Execute appropriate branch
        steps = step_def.get("if_true", []) if result else step_def.get("if_false", [])

        # Recursively execute branch steps
        for branch_step in steps:
            step_result = await self._execute_step(
                branch_step.get("id", "unnamed"),
                branch_step,
                context
            )

            if not step_result.get("success"):
                return step_result

        return {"success": True, "branch": "true" if result else "false"}
