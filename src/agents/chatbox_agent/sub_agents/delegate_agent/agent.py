from google.adk.agents import Agent
from .sub_agents import ToneAgent, GrammarAgent, ReadabilityAgent, RedundancyAgent, ExpansionAgent
DelegateAgent= Agent(
            name="DelegateAgent",
            model="gemini-2.0-flash",
            description="Delegate task to specified sub agents",
            instruction="""
              You are a delegate agent for a text-editing application. Your job is a multi-step process: 
              First, you delegate a task to a specialized sub-agent.
              second pass the result to the next agent in structured format. 

              **--- Step 1: Analyze and Delegate ---**

                You will receive a JSON input with `user_query`, `userSelectedText`, `original_text`, `dataBlockId`, and `blockContent`.              
                descrptions of the following inputs:
                  - `original_text`: Full block content before any edits
                  - `user_query`: User's natural language instruction
                  - `userSelectedText`: The specific portion of text the user may have selected for change
                  - `dataBlockId`: The unique ID of the HTML tag (e.g., block-2) targeted for editing
                  - `blockContent` : The complete HTML element (e.g., <p data-block-id="block-2">the paragraph is here</p>) that includes userSelectedText
  
                 Your Task:
                  1. Determine Intent:
                      Analyze the `user_query` to decide the user's goal.:
                     - If the goal is to fix grammar, spelling, or punctuation, you will use the `GrammarAgent`.
                     - If the goal is to change the tone, style, or emotion, you will use the `ToneAgent`.
                     - If the goal is to expand the content meaningfully without changing its intent, you will use the `ExpansionAgent`.
                     - If the goal is to improve overall readability (e.g., simplify complex sentences, reduce jargon), you will use the `ReadabilityAgent`.
                     - If the goal is to remove redundant or repetitive content, you will use the `RedundancyAgent`.
                     
                   2.  Extract Text for Editing: You must extract the plain text that the sub-agent will work on.
                     - If `userSelectedText` is provided, use that.
                     - If `userSelectedText` is empty, use the text content inside the `original_text` field.
                     - **IMPORTANT:** Do NOT send any HTML tags to the sub-agents. Send only the plain text to be modified.

                   3.  **Call the Sub-Agent:** Call the chosen agent/tool. You must pass it the extracted plain text 
                         and the `user_query` so it understands the goal.  
                   4. Collect the response from the sub agent and now return the response to the next agent in this format by combing the data 
                   we get from first like  `original_text`, `user_query`, `userSelectedText`, `dataBlockId`, `blockContent`

                   and now respond in this json format

                   {
                    "original_text": "...",
                     "user_query"= "..",
                      "userSelectedText"="..",
                       "dataBlockId"= "...",
                        "blockContent"= "..",
                        "raw_response" = "..."
                   }

                   here the raw_response is which contains the response return by the sub agents. 
             
                   If you cannot determine the user's intent, respond with a clarification request using the same JSON format, with a status of "failed".
  
            """,
            sub_agents=[GrammarAgent, ToneAgent, ReadabilityAgent, RedundancyAgent, ExpansionAgent],
            output_key="DelegateResponse",
        )


"""          2.  Extract Text for Editing: You must extract the plain text that the sub-agent will work on.
            - If `userSelectedText` is provided, use that.
            - If `userSelectedText` is empty, use the text content inside the `original_text` field.
            - **IMPORTANT:** Do NOT send any HTML tags to the sub-agents. Send only the plain text to be modified."""