


def run_conversation(messages, tools, available_functions, deployment_name):
    # Step 1: send the conversation and available functions to GPT
    response = client.chat.completions.create(
        model = deployment_name,
        messages = messages,
        tools = tools,
        tool_choice="auto"    # auto is default, but we'll be explicit
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if GPT wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            # verify function exists
            if function_name not in available_functions:
                return "Function " + function_name + " does not exist"
            fuction_to_call = available_functions[function_name]  
        
        # verify function has correct number of arguments
        function_args = json.loads(tool_call.function.arguments)
        if check_args(fuction_to_call, function_args) is False:
            return "Invalid number of arguments for function: " + function_name
        function_response = fuction_to_call(**function_args)
        
        # print("Output of function call:")
        # print(function_response)
        # print()
        
        # Step 4: send the info on the function call and function response to GPT
        
        # function_name 값에 따른 분기 처리
        if function_name == "get_directions" or function_name == "get_future_directions":
            messages.append(
                {"role": "system", "content": "You are a bot that guides you through car routes. When the user provides the origin and destination name, you provides summary route guidance information."}
            )
        elif function_name == "get_current_weather":
            messages.append(
                {"role": "system", "content": "You are an agent that tells the user about the weather. You describe based on the given data and do not judge and create other sentences."},
            )
        elif function_name == "get_current_time":
            messages.append(
                {"role": "system", "content": "You are a bot that tells the world time. You describe based on the given data and do not judge and create other sentences."},
            )
        else :
            messages.append(
                {"role": "system", "content": "You are an AI assistant that helps people find information. The answer must be judged and answered based on factual data. Please use simple expressions as much as possible."},
            )
        
        # adding assistant response to messages
        messages.append(response_message)  # extend conversation with assistant's reply

        # adding function response to messages
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        # print("Messages in second request:")
        # for message in messages:
        # print(messages)
        # print(json.dumps(messages, ensure_ascii=False, indent=4))

        second_response = client.chat.completions.create(
            model = deployment_name,
            messages = messages,
            temperature=0
        )
        # get a new response from GPT where it can see the function response
        
        # print("Second Call: ")
        # print(second_response)
        # print()

        return second_response