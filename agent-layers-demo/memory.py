class Memory:
    """Manage conversation history and tool descriptions."""
    def __init__(self):
        self.conversation_history = []
        self.tools_description = ""
        self.extracted_facts = None  # Store extracted facts
        self.perception_response = []  # Store perception responses as a list
        self.decision_response = []  # Store decision responses as a list

    def update_tools_description(self, tools):
        """Update the tools description based on the available tools."""
        descriptions = []
        for i, tool in enumerate(tools):
            try:
                params = tool.inputSchema
                desc = getattr(tool, "description", "No description available")
                name = getattr(tool, "name", f"tool_{i}")
                if "properties" in params:
                    param_details = [
                        f"{param_name}: {param_info.get('type', 'unknown')}"
                        for param_name, param_info in params["properties"].items()
                    ]
                    params_str = ", ".join(param_details)
                else:
                    params_str = "no parameters"
                descriptions.append(f"{i+1}. {name}({params_str}) - {desc}")
            except Exception as e:
                descriptions.append(f"{i+1}. Error processing tool")
        self.tools_description = "\n".join(descriptions)

    def add_to_history(self, user_input, assistant_response):
        """Add a user input and assistant response to the conversation history."""
        self.conversation_history.append((user_input, assistant_response))

    def store_extracted_facts(self, facts):
        """Store extracted facts in memory."""
        self.extracted_facts = facts

    def update_perception_response(self, response):
        """Append the perception response from the LLM."""
        self.perception_response.append(response)

    def get_perception_response(self):
        """Retrieve all stored perception responses."""
        return self.perception_response

    def update_decision_response(self, response):
        """Append the decision response from the LLM."""
        self.decision_response.append({"Assistant":response})

    def get_decision_response(self):
        """Retrieve all stored decision responses."""
        return self.decision_response
