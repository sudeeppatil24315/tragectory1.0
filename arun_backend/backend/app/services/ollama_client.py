"""
Ollama Client Infrastructure for Trajectory Engine MVP

This module provides a robust client wrapper for interacting with Ollama LLM server.
Features:
- Connection to localhost:11434
- Retry logic with exponential backoff
- Timeout handling
- Health check
- Parallel request handling with ThreadPoolExecutor
- Performance metrics logging

NO cloud APIs - everything runs locally on RTX 4060.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Ollama LLM client with retry logic, timeout handling, and parallel processing.
    
    This client connects to a local Ollama server running Llama 3.1 8B model.
    All LLM operations run locally on the user's hardware (RTX 4060).
    
    Features:
    - Automatic retry with exponential backoff (3 attempts)
    - Timeout handling (10s max per request)
    - Health check to verify server availability
    - Parallel request handling (8 workers)
    - Performance metrics logging
    
    Usage:
        client = OllamaClient()
        response = client.generate("What is Python?", temperature=0.7)
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 11434,
        model: str = "llama3.1:8b",
        max_workers: int = 8,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama server host (default: localhost)
            port: Ollama server port (default: 11434)
            model: Model name (default: llama3.1:8b)
            max_workers: Number of parallel workers (default: 8)
            timeout: Request timeout in seconds (default: 10)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.base_url = f"http://{host}:{port}"
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        
        logger.info(f"Ollama client initialized: {self.base_url}, model: {self.model}")
    
    def is_available(self) -> bool:
        """
        Check if Ollama server is available and responsive.
        
        Returns:
            bool: True if server is available, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama server not available: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Ollama server.
        
        Returns:
            dict: Health check results with status, model info, and metrics
        """
        try:
            # Check if server is running
            tags_response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            
            if tags_response.status_code != 200:
                return {
                    "status": "unhealthy",
                    "available": False,
                    "message": "Ollama server not responding"
                }
            
            # Check if our model is available
            models = tags_response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            model_available = any(self.model in name for name in model_names)
            
            # Calculate success rate
            success_rate = 0.0
            if self.total_requests > 0:
                success_rate = (self.successful_requests / self.total_requests) * 100
            
            # Calculate average response time
            avg_response_time = 0.0
            if self.successful_requests > 0:
                avg_response_time = self.total_response_time / self.successful_requests
            
            return {
                "status": "healthy" if model_available else "degraded",
                "available": True,
                "model": self.model,
                "model_available": model_available,
                "available_models": model_names,
                "metrics": {
                    "total_requests": self.total_requests,
                    "successful_requests": self.successful_requests,
                    "failed_requests": self.failed_requests,
                    "success_rate": f"{success_rate:.1f}%",
                    "avg_response_time": f"{avg_response_time:.2f}s"
                },
                "message": "Ollama server is operational" if model_available else f"Model {self.model} not found"
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "available": False,
                "message": f"Health check failed: {str(e)}"
            }
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama LLM with retry logic and timeout handling.
        
        This method implements:
        - Exponential backoff retry (3 attempts)
        - Timeout handling (10s max)
        - Performance metrics logging
        - Error handling with detailed messages
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0-1.0)
                - 0.1: Very deterministic (data cleaning)
                - 0.2: Mostly deterministic (skill demand)
                - 0.3: Slightly creative (voice eval)
                - 0.7: Creative (recommendations, narratives)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt for context
        
        Returns:
            dict: Response with 'text', 'success', 'response_time', 'attempts'
        
        Raises:
            Exception: If all retry attempts fail
        """
        self.total_requests += 1
        start_time = time.time()
        
        # Build request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"LLM request attempt {attempt}/{self.max_retries}")
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_time = time.time() - start_time
                    
                    # Update metrics
                    self.successful_requests += 1
                    self.total_response_time += response_time
                    
                    logger.info(f"LLM request successful in {response_time:.2f}s")
                    
                    return {
                        "text": result.get("response", ""),
                        "success": True,
                        "response_time": response_time,
                        "attempts": attempt,
                        "model": self.model,
                        "tokens": result.get("eval_count", 0)
                    }
                else:
                    last_exception = Exception(f"HTTP {response.status_code}: {response.text}")
                    logger.warning(f"LLM request failed: {last_exception}")
                    
            except requests.exceptions.Timeout:
                last_exception = Exception(f"Request timeout after {self.timeout}s")
                logger.warning(f"LLM request timeout on attempt {attempt}")
                
            except requests.exceptions.ConnectionError:
                last_exception = Exception("Could not connect to Ollama server")
                logger.warning(f"Connection error on attempt {attempt}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"LLM request error on attempt {attempt}: {str(e)}")
            
            # Exponential backoff before retry
            if attempt < self.max_retries:
                backoff_time = 2 ** attempt  # 2s, 4s, 8s
                logger.info(f"Retrying in {backoff_time}s...")
                time.sleep(backoff_time)
        
        # All retries failed
        self.failed_requests += 1
        response_time = time.time() - start_time
        
        logger.error(f"LLM request failed after {self.max_retries} attempts")
        
        return {
            "text": "",
            "success": False,
            "response_time": response_time,
            "attempts": self.max_retries,
            "error": str(last_exception)
        }
    
    def generate_batch(
        self,
        prompts: list[str],
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        Generate text for multiple prompts in parallel using ThreadPoolExecutor.
        
        This method processes up to 8 prompts simultaneously, significantly
        improving throughput for batch operations.
        
        Args:
            prompts: List of prompts to process
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
            system_prompt: Optional system prompt
        
        Returns:
            list: List of response dicts (same format as generate())
        """
        logger.info(f"Processing batch of {len(prompts)} prompts")
        
        # Submit all tasks to executor
        futures = []
        for prompt in prompts:
            future = self.executor.submit(
                self.generate,
                prompt,
                temperature,
                max_tokens,
                system_prompt
            )
            futures.append(future)
        
        # Collect results as they complete
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Batch request failed: {str(e)}")
                results.append({
                    "text": "",
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Batch processing complete: {len(results)} results")
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the Ollama client.
        
        Returns:
            dict: Performance metrics including success rate and avg response time
        """
        success_rate = 0.0
        if self.total_requests > 0:
            success_rate = (self.successful_requests / self.total_requests) * 100
        
        avg_response_time = 0.0
        if self.successful_requests > 0:
            avg_response_time = self.total_response_time / self.successful_requests
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time
        }
    
    def shutdown(self):
        """Shutdown the thread pool executor gracefully."""
        logger.info("Shutting down Ollama client...")
        self.executor.shutdown(wait=True)
        logger.info("Ollama client shutdown complete")


# Global client instance (singleton pattern)
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """
    Get or create the global Ollama client instance.
    
    This function implements the singleton pattern to ensure only one
    client instance exists throughout the application lifecycle.
    
    Returns:
        OllamaClient: The global Ollama client instance
    """
    global _ollama_client
    
    if _ollama_client is None:
        _ollama_client = OllamaClient()
        logger.info("Created global Ollama client instance")
    
    return _ollama_client
