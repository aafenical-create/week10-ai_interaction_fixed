Task: Part A – API Setup

Prompt: Asked how to connect Streamlit app to Hugging Face API and display a test response
AI Suggestion: Provided code to load the token from secrets.toml, send a test message, and display the response using requests
My Modifications & Reflections: I copied the code and fixed my token issue. The API worked after correcting the token format

Task: Part B – Chat UI

Prompt: Asked how to build a chat interface using Streamlit chat components
AI Suggestion: Suggested using st.chat_input and st.chat_message along with st.session_state to store messages
My Modifications & Reflections: I implemented the chat UI and ensured messages were stored and displayed correctly. I debugged an issue where messages weren’t appearing

Task: Part C – Chat Management

Prompt: Asked how to create multiple chats with a sidebar
AI Suggestion: Suggested using a dictionary of chats in session state, with unique IDs and sidebar buttons for switching and deleting chats
My Modifications & Reflections: I implemented multiple chats and fixed issues with messages not appearing by correctly referencing chat["messages"]

Task: Part D – Chat Persistence

Prompt: Asked how to save chats so they persist after refreshing
AI Suggestion: Provided functions to save chats as JSON files and load them on startup
My Modifications & Reflections: I added file saving and loading. Verified that chats persist after refreshing and deleting removes files

Task: Task 2 – Streaming Responses

Prompt: Asked how to make responses stream like ChatGPT.
AI Suggestion: Provided streaming API implementation using stream=True and iterating over response lines
My Modifications & Reflections: I replaced the normal API call with streaming and added a small delay so the effect is visible

Task: Task 3 – User Memory

Prompt: Asked how to implement memory extraction and storage
AI Suggestion: Suggested making a second API call to extract user traits and storing them in memory.json, then injecting them into prompts
My Modifications & Reflections: I implemented memory storage and display in the sidebar. Verified that the app remembers user preferences