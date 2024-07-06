from dotenv import load_dotenv
from groq import Groq
import json
import requests
import os
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define the function to get current weather
def get_current_weather(location):
    """Fetches current weather data from OpenWeather API."""
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = os.getenv("OPENWEATHER_API_KEY")  # Replace with your actual API key
    complete_url = f"{base_url}appid={api_key}&q={location}"

    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['main']
        temperature = data['main']['temp'] - 273.15  # Convert Kelvin to Celsius
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        # Construct natural language response
        response_text = (
            f"The weather in {location} is currently {weather.lower()}, "
            f"with a temperature of {round(temperature, 2)} degrees Celsius. "
            f"The weather condition is described as {description.lower()}, "
            f"with humidity at {humidity}% and wind speed at {wind_speed} meters per second."
        )

        return response_text
    else:
        return f"Sorry, there was an error fetching data for {location}."

def main():
    st.title("Weather App")
    city = st.text_input("Enter the city name")
    
    if st.button("Get Weather"):
        # Use Groq to interact with the function
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Fetches current weather data from OpenWeather API.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name for which weather data is requested."
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]

        # Call Groq to get weather info
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "user",
                    "content": f"What is the weather in {city}?"
                }
            ],
            temperature=0,
            max_tokens=300,
            tools=tools,
            tool_choice="auto"
        )

        # Extract arguments from Groq response
        groq_response = response.choices[0].message
        args = json.loads(groq_response.tool_calls[0].function.arguments)

        # Call the function using the extracted arguments
        weather_info = get_current_weather(**args)

        # Display natural language response
        st.write(weather_info)

if __name__ == "__main__":
    main()
