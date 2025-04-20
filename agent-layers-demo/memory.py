class Memory:
    """
    Manage conversation history, tool descriptions, and extracted facts.

    This class provides methods to store and retrieve information such as
    conversation history, tool descriptions, extracted facts, and responses
    from the perception and decision layers.
    """

    def __init__(self):
        """Initialize memory with default values."""
        self.conversation_history = []
        self.tools_description = ""
        self.extracted_facts = None  # Store extracted facts
        self.perception_response = []  # Store perception responses as a list
        self.decision_response = []  # Store decision responses as a list

    def update_tools_description(self, tools):
        """
        Update the tools description based on the available tools.

        Args:
            tools (list): List of tools with their descriptions and schemas.
        """
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
        """
        Add a user input and assistant response to the conversation history.

        Args:
            user_input (str): The user's input.
            assistant_response (str): The assistant's response.
        """
        self.conversation_history.append((user_input, assistant_response))

    def store_extracted_facts(self, facts):
        """
        Store extracted facts in memory.

        Args:
            facts (dict): Extracted facts from the perception layer.
        """
        self.extracted_facts = facts

    def update_perception_response(self, response):
        """
        Append the perception response from the LLM.

        Args:
            response (dict): The perception response.
        """
        self.perception_response.append(response)

    def get_perception_response(self):
        """
        Retrieve all stored perception responses.

        Returns:
            list: List of perception responses.
        """
        return self.perception_response

    def update_decision_response(self, response):
        """
        Append the decision response from the LLM.

        Args:
            response (dict): The decision response.
        """
        self.decision_response.append({"Assistant":response})

    def get_decision_response(self):
        """
        Retrieve all stored decision responses.

        Returns:
            list: List of decision responses.
        """
        return self.decision_response
