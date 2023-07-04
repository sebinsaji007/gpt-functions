
import openai
import json
import yfinance as yf

openai.api_key = ""

def get_stock_price(ticker):
    data = yf.Ticker(ticker).history(period="1mo")
    return str(data['Close'][-1])

def run_conversation(user_message):
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": user_message}]
    functions = [
        {
            "name": "get_stock_price",
            "description": "Get the current stock price for a given ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "stock ticker of a company (e.g., AAPL for Apple stock)",
                    },
                },
                "required": ["ticker"]
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is the default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_stock_price": get_stock_price,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions.get(function_name)
        if function_to_call is None:
            function_response = "I'm sorry, I don't have information about that function."
        else:
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = function_to_call(ticker=function_args.get("ticker"))

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append({
            "role": "assistant",
            "content": function_response,
        })  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response

    # Handle the case when the user asks about stocks without specifying a ticker symbol
    if "what is stocks" in user_message.lower():
        response_message = "Stocks represent shares of ownership in a company. When you buy stocks, you become a partial owner of the company and can benefit from its success through price appreciation and dividends."

    messages.append({"role": "assistant", "content": response_message["message"]["content"]})

    second_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
    )
    return second_response

print(run_conversation("Tell me the price of bitcoin and also remember that bitcoin have a different ticker in yfinance"))
