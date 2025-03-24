from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
import base64


model_id = "qwen/qwq-32b:free"
model_id = "google/gemini-2.0-pro-exp-02-05:free"
model_id = "google/gemma-3-27b-it:free"
model_id = "gpt-4o-mini"
llm = ChatOpenAI(model=model_id)

vision_llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
# vision_llm = ChatOpenAI(model="gpt-4o")


def extract_text(img_path: str) -> str:
    """
    Extract text from an image file using a multimodal model.

    Args:
        img_path: A local image file path (strings).

    Returns:
        A single string containing the concatenated text extracted from each image.
    """
    print("\nProcessing the image and extracting text from...")

    all_text = ""
    try:
        # Read image and encode as base64
        with open(img_path, "rb") as image_file:
            image_bytes = image_file.read()

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Prepare the prompt including the base64 image data
        message = [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": (
                            "Extract all the text from this image. "
                            "Return only the extracted text, no explanations."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        },
                    },
                ]
            )
        ]

        # Call the vision-capable model
        response = vision_llm.invoke(message)

        # Append extracted text
        all_text += str(response.content) + "\n\n"

        return all_text.strip()
    
    except Exception as e:
        # You can choose whether to raise or just return an empty string / error message
        error_msg = f"Error extracting text: {str(e)}"
        print(error_msg)
        return ""

tools = [extract_text]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)


class AgentState(TypedDict):
    input_file:  Optional[str]  # Contains file path, type (PNG)
    messages: Annotated[list[AnyMessage], add_messages]

# AgentState
def assistant(state: AgentState):
    # System message
    textual_description_of_tool="""
extract_text(img_path: str) -> str:
    Extract text from an image file using a multimodal model.

    Args:
        img_path: A local image file path (strings).

    Returns:
        A single string containing the concatenated text extracted from each image.
"""
    image=state["input_file"]
    sys_msg = SystemMessage(content=f"You are an helpful agent that can analyse some images and run some computatio without provided tools :\n{textual_description_of_tool} \n You have access to some otpional images. Currently the loaded images is : {image}")

    res = llm_with_tools.invoke([sys_msg] + state["messages"])
    return {"messages": [res], "input_file":state["input_file"]}


def create_graph():
    from langgraph.graph import START, StateGraph
    from langgraph.prebuilt import tools_condition
    from langgraph.prebuilt import ToolNode
    from IPython.display import Image, display

    # Graph
    builder = StateGraph(AgentState)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile()


def run_agent(img_path: str, prompt: str) :
    agent = create_graph()
    
    prompt = f"""
The user is asking for some information about the image.
User question: {prompt}
Extract the text from the image and answer the user question.
"""

    messages = [HumanMessage(content=prompt)] 
    messages= agent.invoke(
    {
        "input_file":img_path,
        "messages": prompt, 
    })

    extracted_text = ""
    for m in messages['messages']:
        if m.name == "extract_text":
            extracted_text = m.content
            break

    result = messages['messages'][-1].content,
    res = {
        "extracted_text": extracted_text,
        "result": result,
    }

    return res
