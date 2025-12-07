To Add More Tools:  
You can add multiple tools in the same method:

```python 
def get_custom_tool_definitions(self) -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "generate_career_advice",
                # ...
            },
            "tool_executor": self._generate_career_advice
        },
        {
            "type": "function",
            "function": {
                "name": "search_job_postings",  # ← 2nd custom tool
                # ...
            },
            "tool_executor": self._search_job_postings
        },
        {
            "type": "function",
            "function": {
                "name": "check_visa_requirements",  # ← 3rd custom tool
                # ...
            },
            "tool_executor": self._check_visa_requirements
        }
    ]
```