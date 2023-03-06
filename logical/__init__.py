import openai
from pyswip import Prolog
import pendulum

from rdflib import Graph


from logical.storage import (
    LogicalRow,
    QueryRow,
    write_dataclass_to_csv,
    load_dataclass_from_csv,
    PROLOG_STORAGE_NAME,
    QUERY_FILE_NAME,
    write_all_prolog,
)


def _openai_wrapper(
    system_message: str,
    user_message: str,
    example_user_message: str = None,
    example_assistant_message: str = None,
):
    messages = []
    messages.append({"role": "system", "content": system_message})
    if example_user_message is not None and example_assistant_message is not None:
        messages.append({"role": "user", "content": example_user_message})
        messages.append({"role": "assistant", "content": example_assistant_message})
    messages.append(
        {"role": "user", "content": user_message},
    )

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return result["choices"][0]["message"]["content"]


def parse_logic(input_text):
    SYSTEM_PARSING_PROMPT = """
    Hello. You are a logic extractor, converting english statements to prolog.
    This requires categorizing and extracting the first class objects, and then their logical relationships.
    Do not assume the logic to be correct.  No explanation is required on your part.
    You can you will output prolog only, so prolog may find the errors.

    The output may be knowledge statements or a query statement.

    Thank you!
    """
    ASISSITANT_PARSING_PROMPT = """
    Please generate prolog, even if the parser fails, byt extracting factual statements or a query from the following: \n

    """

    return _openai_wrapper(
        system_message=SYSTEM_PARSING_PROMPT,
        example_user_message=f"{ASISSITANT_PARSING_PROMPT} jane is red, jim is blue, they are the same color.",
        example_assistant_message="jane(red), jim(blue), same_color(X,Y) :- jane(X), jim(Y).",
        user_message=f"{ASISSITANT_PARSING_PROMPT}{input_text}",
    )


def parse_query(input_text):
    SYSTEM_ASKING_PROMPT = """
    You are an assistant to help us understand the output of a prolog statement.
    There may be logical errors in the database, or the query.
    """

    ASSISTANT_ASKING_PROMPT = """
    Please explaing why the logic is correct or incorrect, or what might be missing in the following.  \n

    """

    return _openai_wrapper(
        system_message=SYSTEM_ASKING_PROMPT,
        example_user_message=f"{ASSISTANT_ASKING_PROMPT} jane is red, jim is blue, they are the same color.",
        example_assistant_message="same_color(X,Y) :- jane(X), jim(Y).",
        user_message=f"{ASSISTANT_ASKING_PROMPT}{input_text}",
    )


def run_parser(input_text: str):
    result = parse_logic(input_text)
    row = LogicalRow(input_text=input_text, prolog_text=result)
    write_dataclass_to_csv(row, PROLOG_STORAGE_NAME)
    return result


def run_logic(input_text: str):
    # export all prolog to new file
    write_all_prolog()

    # get query
    query = parse_logic(input_text)
    print(f"sending query {query}")

    # export prolog to file
    prolog.consult(PROLOG_FILE_NAME)
    solutions = [solution for solution in prolog.query(query)]
    for solution in solutions:
        print(solution)

    result = parse_query()

    return chat(result)