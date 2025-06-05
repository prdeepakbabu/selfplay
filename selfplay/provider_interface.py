"""
Provider interface for different LLM providers.
This module defines the abstract base class for LLM providers and implements
concrete provider classes for different LLM services.
"""

import os
import abc
import time
import logging
from typing import List, Dict, Any, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProviderInterface(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    def __init__(self, time_delay=0, **kwargs):
        """
        Initialize the provider with necessary credentials and configuration.
        
        Args:
            time_delay: Time to wait in seconds between API calls to avoid throttling. Default is 0.
            **kwargs: Additional provider-specific parameters.
        """
        self.time_delay = time_delay

    @abc.abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response from the LLM based on the provided messages.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The generated response text.
        """
        pass

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Get the name of the provider."""
        pass

    @property
    @abc.abstractmethod
    def available_models(self) -> List[str]:
        """Get a list of available models for this provider."""
        pass


class AzureOpenAIProvider(LLMProviderInterface):
    """Provider implementation for Azure OpenAI."""

    def __init__(self, api_key=None, azure_endpoint=None, api_version=None, model="gpt-4", time_delay=0, **kwargs):
        """
        Initialize the Azure OpenAI provider.

        Args:
            api_key: Azure OpenAI API key. If None, will try to get from environment.
            azure_endpoint: Azure OpenAI endpoint. If None, will try to get from environment.
            api_version: Azure OpenAI API version. If None, will try to get from environment.
            model: The model to use. Default is "gpt-4".
            **kwargs: Additional configuration parameters.
        """
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError("The 'openai' package is required for AzureOpenAIProvider.")

        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_API_ENDPOINT")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION")
        self.model = model
        self.time_delay = time_delay

        if not all([self.api_key, self.azure_endpoint, self.api_version]):
            raise ValueError(
                "Azure OpenAI credentials not provided. "
                "Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_ENDPOINT, and AZURE_OPENAI_API_VERSION "
                "environment variables or provide them as parameters."
            )

        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key
        )
        logger.info(f"Initialized {self.provider_name} provider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using Azure OpenAI.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The generated response text.
        """
        try:
            # Apply time delay if specified to avoid throttling
            if self.time_delay > 0:
                logger.info(f"Waiting for {self.time_delay} seconds before making API call to avoid throttling...")
                time.sleep(self.time_delay)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from {self.provider_name}: {str(e)}")
            return f"Error generating response: {str(e)}"

    @property
    def provider_name(self) -> str:
        return "Azure OpenAI"

    @property
    def available_models(self) -> List[str]:
        # In a real implementation, this might query the API for available models
        return ["gpt-4", "gpt-3.5-turbo"]


class OpenAIProvider(LLMProviderInterface):
    """Provider implementation for OpenAI."""

    def __init__(self, api_key=None, model="gpt-4", time_delay=0, **kwargs):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: The model to use. Default is "gpt-4".
            **kwargs: Additional configuration parameters.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("The 'openai' package is required for OpenAIProvider.")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.time_delay = time_delay

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable or provide it as a parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized {self.provider_name} provider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using OpenAI.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The generated response text.
        """
        try:
            # Apply time delay if specified to avoid throttling
            if self.time_delay > 0:
                logger.info(f"Waiting for {self.time_delay} seconds before making API call to avoid throttling...")
                time.sleep(self.time_delay)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from {self.provider_name}: {str(e)}")
            return f"Error generating response: {str(e)}"

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def available_models(self) -> List[str]:
        # In a real implementation, this might query the API for available models
        return ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]


class AnthropicProvider(LLMProviderInterface):
    """Provider implementation for Anthropic."""

    def __init__(self, api_key=None, model="claude-3-opus", time_delay=0, **kwargs):
        """
        Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key. If None, will try to get from environment.
            model: The model to use. Default is "claude-3-opus".
            **kwargs: Additional configuration parameters.
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError("The 'anthropic' package is required for AnthropicProvider.")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.time_delay = time_delay

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. "
                "Set ANTHROPIC_API_KEY environment variable or provide it as a parameter."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info(f"Initialized {self.provider_name} provider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using Anthropic.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The generated response text.
        """
        try:
            # Apply time delay if specified to avoid throttling
            if self.time_delay > 0:
                logger.info(f"Waiting for {self.time_delay} seconds before making API call to avoid throttling...")
                time.sleep(self.time_delay)
            # Convert messages to Anthropic format
            system_message = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
            
            # Filter out system messages as they're handled separately in Anthropic
            user_assistant_messages = [msg for msg in messages if msg["role"] != "system"]
            
            # Create the message list for Anthropic
            anthropic_messages = []
            for msg in user_assistant_messages:
                role = "user" if msg["role"] == "user" else "assistant"
                anthropic_messages.append({"role": role, "content": msg["content"]})
            
            response = self.client.messages.create(
                model=self.model,
                system=system_message,
                messages=anthropic_messages,
                max_tokens=1000,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating response from {self.provider_name}: {str(e)}")
            return f"Error generating response: {str(e)}"

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    @property
    def available_models(self) -> List[str]:
        return ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]


class GoogleProvider(LLMProviderInterface):
    """Provider implementation for Google (Gemini)."""

    def __init__(self, api_key=None, model="gemini-pro", time_delay=0, **kwargs):
        """
        Initialize the Google provider.

        Args:
            api_key: Google API key. If None, will try to get from environment.
            model: The model to use. Default is "gemini-pro".
            **kwargs: Additional configuration parameters.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("The 'google-generativeai' package is required for GoogleProvider.")

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.time_delay = time_delay

        if not self.api_key:
            raise ValueError(
                "Google API key not provided. "
                "Set GOOGLE_API_KEY environment variable or provide it as a parameter."
            )

        genai.configure(api_key=self.api_key)
        self.client = genai
        logger.info(f"Initialized {self.provider_name} provider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using Google Gemini.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The generated response text.
        """
        try:
            # Apply time delay if specified to avoid throttling
            if self.time_delay > 0:
                logger.info(f"Waiting for {self.time_delay} seconds before making API call to avoid throttling...")
                time.sleep(self.time_delay)
            # Extract system message if present
            system_message = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
            
            # Convert messages to Google format
            google_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    continue  # Skip system messages as they're handled separately
                
                role = "user" if msg["role"] == "user" else "model"
                google_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
            
            # Initialize the model
            model = self.client.GenerativeModel(model_name=self.model)
            
            # Add system message as a prefix if present
            if system_message:
                model = model.with_system_instruction(system_message)
            
            # Generate response
            chat = model.start_chat(history=google_messages)
            response = chat.send_message("")  # Send empty message to get response based on history
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating response from {self.provider_name}: {str(e)}")
            return f"Error generating response: {str(e)}"

    @property
    def provider_name(self) -> str:
        return "Google"

    @property
    def available_models(self) -> List[str]:
        return ["gemini-pro", "gemini-ultra"]


class MetaProvider(LLMProviderInterface):
    """Provider implementation for Meta (Llama)."""

    def __init__(self, api_key=None, model="llama-3-70b", time_delay=0, **kwargs):
        """
        Initialize the Meta provider.

        Args:
            api_key: Meta API key. If None, will try to get from environment.
            model: The model to use. Default is "llama-3-70b".
            **kwargs: Additional configuration parameters.
        """
        try:
            import requests
        except ImportError:
            raise ImportError("The 'requests' package is required for MetaProvider.")

        self.api_key = api_key or os.getenv("META_API_KEY")
        self.model = model
        self.api_url = kwargs.get("api_url", "https://llama-api.meta.com/v1/chat/completions")
        self.time_delay = time_delay

        if not self.api_key:
            raise ValueError(
                "Meta API key not provided. "
                "Set META_API_KEY environment variable or provide it as a parameter."
            )

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        logger.info(f"Initialized {self.provider_name} provider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using Meta's Llama API.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The generated response text.
        """
        try:
            # Apply time delay if specified to avoid throttling
            if self.time_delay > 0:
                logger.info(f"Waiting for {self.time_delay} seconds before making API call to avoid throttling...")
                time.sleep(self.time_delay)
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 800)
            }
            
            response = self.session.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating response from {self.provider_name}: {str(e)}")
            return f"Error generating response: {str(e)}"

    @property
    def provider_name(self) -> str:
        return "Meta"

    @property
    def available_models(self) -> List[str]:
        return ["llama-3-70b", "llama-3-8b", "llama-2-70b"]


class AWSBedrockProvider(LLMProviderInterface):
    """Provider implementation for AWS Bedrock."""

    def __init__(self, aws_access_key=None, aws_secret_key=None, region="us-east-1", 
                 model="anthropic.claude-3-sonnet-20240229-v1:0", time_delay=0, **kwargs):
        """
        Initialize the AWS Bedrock provider.

        Args:
            aws_access_key: AWS access key. If None, will try to get from environment or ~/.aws/credentials.
            aws_secret_key: AWS secret key. If None, will try to get from environment or ~/.aws/credentials.
            region: AWS region. Default is "us-east-1".
            model: The model to use. Default is "anthropic.claude-3-sonnet-20240229-v1:0".
            **kwargs: Additional configuration parameters.
        """
        try:
            import boto3
        except ImportError:
            raise ImportError("The 'boto3' package is required for AWSBedrockProvider.")

        self.region = region
        self.model = model
        self.time_delay = time_delay

        # If credentials are provided explicitly, use them
        if aws_access_key and aws_secret_key:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            # Otherwise, let boto3 handle credential discovery
            # This will check:
            # 1. Environment variables
            # 2. ~/.aws/credentials
            # 3. EC2/ECS instance profiles
            self.client = boto3.client('bedrock-runtime', region_name=self.region)
        logger.info(f"Initialized {self.provider_name} provider with model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using AWS Bedrock.

        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The generated response text.
        """
        try:
            # Apply time delay if specified to avoid throttling
            if self.time_delay > 0:
                logger.info(f"Waiting for {self.time_delay} seconds before making API call to avoid throttling...")
                time.sleep(self.time_delay)
            import json
            
            # Extract model provider from the model ID
            model_provider = self.model.split('.')[0]
            
            # Format request based on the model provider
            if model_provider in ["anthropic", "us"]:  # Handle both anthropic and us.anthropic models
                # Extract system message if present
                system_message = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
                
                # Convert messages to Anthropic format
                anthropic_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        continue  # Skip system messages as they're handled separately
                    
                    role = "user" if msg["role"] == "user" else "assistant"
                    anthropic_messages.append({"role": role, "content": msg["content"]})
                
                # Different format for AWS Bedrock Anthropic models
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "messages": anthropic_messages
                }
                
                # Add system message as a top-level parameter if present
                if system_message:
                    request_body["system"] = system_message
                
                logger.info(f"Request body for {model_provider} model: {json.dumps(request_body)}")
            
            elif model_provider == "amazon":
                # Amazon Titan format
                prompt = ""
                for msg in messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n\n"
                    elif msg["role"] == "user":
                        prompt += f"Human: {msg['content']}\n\n"
                    else:  # assistant
                        prompt += f"Assistant: {msg['content']}\n\n"
                
                prompt += "Assistant: "
                
                request_body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": kwargs.get("max_tokens", 1000),
                        "temperature": kwargs.get("temperature", 0.7),
                        "topP": kwargs.get("top_p", 0.9)
                    }
                }
            
            elif model_provider == "meta":
                # Meta Llama format
                request_body = {
                    "prompt": "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages]),
                    "max_gen_len": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9)
                }
            
            else:
                # Default format (may need adjustment for other providers)
                request_body = {
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract response based on model provider
            if model_provider in ["anthropic", "us"]:
                # For Anthropic models (including Claude 3.7), extract the text content
                if 'content' in response_body and isinstance(response_body['content'], list) and len(response_body['content']) > 0:
                    return response_body['content'][0]['text']
                else:
                    logger.warning(f"Unexpected response format from {model_provider}: {response_body}")
                    # Try to extract text from the response if possible
                    return str(response_body)
            elif model_provider == "amazon":
                return response_body['results'][0]['outputText']
            elif model_provider == "meta":
                return response_body['generation']
            else:
                # Default extraction (may need adjustment)
                return response_body.get('completion', str(response_body))
                
        except Exception as e:
            logger.error(f"Error generating response from {self.provider_name}: {str(e)}")
            return f"Error generating response: {str(e)}"

    @property
    def provider_name(self) -> str:
        return "AWS Bedrock"

    @property
    def available_models(self) -> List[str]:
        return [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet model
            "amazon.titan-text-express-v1",
            "meta.llama-2-70b-chat-v1"
        ]


def get_provider(provider_name: str, **kwargs) -> LLMProviderInterface:
    """
    Factory function to get the appropriate provider instance.

    Args:
        provider_name: Name of the provider to use.
        **kwargs: Additional parameters to pass to the provider constructor.

    Returns:
        An instance of the requested provider.

    Raises:
        ValueError: If the provider name is not recognized.
    """
    providers = {
        "azure": AzureOpenAIProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "meta": MetaProvider,
        "aws": AWSBedrockProvider
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}. Available providers: {', '.join(providers.keys())}")

    return provider_class(**kwargs)
