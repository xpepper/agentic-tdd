"""Supervisor Agent that oversees the TDD process."""

from typing import Dict, Any, Optional


class SupervisorAgent:
    """Agent responsible for overseeing the TDD workflow and handling agent failures."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """Initialize the Supervisor Agent."""
        self.model_name = model_name
        self.api_key = api_key
        self.agent_penalties = {"tester": 0, "implementer": 0, "refactorer": 0}
    
    def evaluate_progress(self, agent_name: str, success: bool, work_dir: str, **kwargs) -> Dict[str, Any]:
        """Evaluate the progress of an agent and decide what to do next."""
        if success:
            # If the agent was successful, return the normal next step
            next_agent = self._get_next_agent(agent_name)
            return {
                "success": True,
                "next_agent": next_agent,
                "message": f"{agent_name} completed successfully. Handing over to {next_agent}.",
                "action": "continue"
            }
        else:
            # If the agent failed, apply penalties and decide next steps
            failure_reason = kwargs.get("failure_reason", "Unknown failure")
            
            # Apply penalties based on the agent and failure type
            self._apply_penalty(agent_name, failure_reason)
            
            # Decide what to do based on the failure
            next_action = self._decide_next_action(agent_name, failure_reason, work_dir)
            
            return {
                "success": False,
                "next_agent": next_action["agent"],
                "message": f"{agent_name} failed: {failure_reason}. Supervisor action: {next_action['reason']}",
                "action": next_action["action"],
                "failure_reason": failure_reason
            }
    
    def _get_next_agent(self, current_agent: str) -> str:
        """Get the next agent in the TDD cycle."""
        agent_cycle = ["tester", "implementer", "refactorer"]
        
        try:
            current_index = agent_cycle.index(current_agent)
            next_index = (current_index + 1) % len(agent_cycle)
            return agent_cycle[next_index]
        except ValueError:
            # If the current agent is not in the cycle, default to tester
            return "tester"
    
    def _apply_penalty(self, agent_name: str, failure_reason: str) -> None:
        """Apply penalty to an agent based on failure type."""
        if agent_name in self.agent_penalties:
            # Increase penalty based on failure type
            if "too much code" in failure_reason.lower():
                # Tester wrote test that already passes, penalize implementer
                self.agent_penalties["implementer"] += 1
            else:
                self.agent_penalties[agent_name] += 1
    
    def _decide_next_action(self, failed_agent: str, failure_reason: str, work_dir: str) -> Dict[str, Any]:
        """Decide what action to take when an agent fails."""
        if failed_agent == "tester":
            # If tester fails (writes test that already passes), 
            # it means implementer wrote too much code - go back to refactorer
            if "already passes" in failure_reason.lower():
                return {
                    "agent": "refactorer", 
                    "action": "refactor", 
                    "reason": "Tester wrote test that already passes, indicating implementer overcoded. Refactoring needed."
                }
            else:
                # Otherwise, tester should try again
                return {
                    "agent": "tester", 
                    "action": "retry", 
                    "reason": "Tester failed to write appropriate failing test."
                }
        
        elif failed_agent == "implementer":
            # If implementer fails to make test pass, supervisor may decide to 
            # have refactorer do preparatory work or have implementer try again
            return {
                "agent": "refactorer", 
                "action": "prep_refactor", 
                "reason": "Implementer failed to make test pass. Refactorer should prepare code structure first."
            }
        
        elif failed_agent == "refactorer":
            # If refactorer fails to keep tests passing, it may need to retry 
            # or the process may need to go back to implementer to fix issues
            retry_count = self._get_retry_count(work_dir, "refactorer")
            if retry_count < 3:  # Default max retries
                return {
                    "agent": "refactorer", 
                    "action": "retry", 
                    "reason": f"Refactorer failed but under retry limit ({retry_count}/3). Retrying."
                }
            else:
                return {
                    "agent": "implementer", 
                    "action": "revert_and_retry", 
                    "reason": "Refactorer exhausted retries. Implementer should revert and try again."
                }
        
        # Default fallback
        return {
            "agent": "tester", 
            "action": "continue", 
            "reason": "Default fallback action after failure."
        }
    
    def _get_retry_count(self, work_dir: str, agent_name: str) -> int:
        """Get the number of retries for an agent in the current work directory."""
        # In a real implementation, this would track retry counts in a persistent way
        # For now, we'll just return a default value
        return 0
    
    def get_agent_status(self) -> Dict[str, int]:
        """Get the current penalty status of all agents."""
        return self.agent_penalties.copy()
    
    def reset_agent_penalties(self) -> None:
        """Reset all agent penalties to zero."""
        self.agent_penalties = {"tester": 0, "implementer": 0, "refactorer": 0}