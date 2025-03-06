# API Usage Code Examples

This document provides code examples for interacting with the Hello World API in various programming languages.

## Table of Contents

- [Python](#python)
- [JavaScript](#javascript)
- [Go](#go)
- [Java](#java)
- [C#](#c)
- [Ruby](#ruby)
- [PHP](#php)
- [Rust](#rust)
- [Shell](#shell)

## Python

### Basic Request with Requests

```python
import requests

# Base URL of the API
base_url = "http://localhost:8000"

# Make a request to the root endpoint
response = requests.get(f"{base_url}/api/v1/")

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print(f"Message: {data['message']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Check the health endpoint
health_response = requests.get(f"{base_url}/api/v1/health")

if health_response.status_code == 200:
    health_data = health_response.json()
    print(f"API Status: {health_data['status']}")
    print(f"API Version: {health_data['version']}")
    print(f"Uptime: {health_data['uptime_human']}")
else:
    print(f"Error checking health: {health_response.status_code}")
```

### Async Client with HTTPX

```python
import asyncio
import httpx

async def fetch_api_data():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Make a request to the root endpoint
        response = await client.get(f"{base_url}/api/v1/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data['message']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
        # Check the health endpoint
        health_response = await client.get(f"{base_url}/api/v1/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"API Status: {health_data['status']}")
            print(f"API Version: {health_data['version']}")
            print(f"Uptime: {health_data['uptime_human']}")
        else:
            print(f"Error checking health: {health_response.status_code}")

# Run the async function
asyncio.run(fetch_api_data())
```

## JavaScript

### Browser (Fetch API)

```javascript
// Base URL of the API
const baseUrl = 'http://localhost:8000';

// Fetch the root endpoint
fetch(`${baseUrl}/api/v1/`)
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log(`Message: ${data.message}`);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Fetch the health endpoint
fetch(`${baseUrl}/api/v1/health`)
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log(`API Status: ${data.status}`);
    console.log(`API Version: ${data.version}`);
    console.log(`Uptime: ${data.uptime_human}`);
  })
  .catch(error => {
    console.error('Error checking health:', error);
  });
```

### Node.js (Axios)

```javascript
const axios = require('axios');

// Base URL of the API
const baseUrl = 'http://localhost:8000';

// Helper function to make API requests
async function makeRequest(endpoint) {
  try {
    const response = await axios.get(`${baseUrl}${endpoint}`);
    return response.data;
  } catch (error) {
    console.error(`Error requesting ${endpoint}:`, error.message);
    return null;
  }
}

// Main function to fetch data from the API
async function fetchApiData() {
  // Get message from root endpoint
  const rootData = await makeRequest('/api/v1/');
  if (rootData) {
    console.log(`Message: ${rootData.message}`);
  }
  
  // Get health status
  const healthData = await makeRequest('/api/v1/health');
  if (healthData) {
    console.log(`API Status: ${healthData.status}`);
    console.log(`API Version: ${healthData.version}`);
    console.log(`Uptime: ${healthData.uptime_human}`);
  }
}

fetchApiData();
```

## Go

```go
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Message represents the response from the root endpoint
type Message struct {
	Message string `json:"message"`
}

// Health represents the response from the health endpoint
type Health struct {
	Status        string `json:"status"`
	Version       string `json:"version"`
	UptimeSeconds int    `json:"uptime_seconds"`
	UptimeHuman   string `json:"uptime_human"`
	System        struct {
		ProcessID   int     `json:"process_id"`
		Hostname    string  `json:"hostname"`
		CPUUsage    float64 `json:"cpu_usage"`
		MemoryUsage float64 `json:"memory_usage"`
		DiskUsage   float64 `json:"disk_usage"`
	} `json:"system"`
}

func main() {
	baseURL := "http://localhost:8000"

	// Create an HTTP client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Get message from root endpoint
	resp, err := client.Get(fmt.Sprintf("%s/api/v1/", baseURL))
	if err != nil {
		fmt.Printf("Error making request: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error reading response: %v\n", err)
			return
		}

		var message Message
		if err := json.Unmarshal(body, &message); err != nil {
			fmt.Printf("Error parsing JSON: %v\n", err)
			return
		}

		fmt.Printf("Message: %s\n", message.Message)
	} else {
		fmt.Printf("Error: %d\n", resp.StatusCode)
	}

	// Get health status
	healthResp, err := client.Get(fmt.Sprintf("%s/api/v1/health", baseURL))
	if err != nil {
		fmt.Printf("Error making health request: %v\n", err)
		return
	}
	defer healthResp.Body.Close()

	if healthResp.StatusCode == http.StatusOK {
		body, err := io.ReadAll(healthResp.Body)
		if err != nil {
			fmt.Printf("Error reading health response: %v\n", err)
			return
		}

		var health Health
		if err := json.Unmarshal(body, &health); err != nil {
			fmt.Printf("Error parsing health JSON: %v\n", err)
			return
		}

		fmt.Printf("API Status: %s\n", health.Status)
		fmt.Printf("API Version: %s\n", health.Version)
		fmt.Printf("Uptime: %s\n", health.UptimeHuman)
	} else {
		fmt.Printf("Error checking health: %d\n", healthResp.StatusCode)
	}
}
```

## Java

```java
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class HelloWorldApiClient {

    private static final String BASE_URL = "http://localhost:8000";
    private static final HttpClient httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .connectTimeout(Duration.ofSeconds(10))
            .build();
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static void main(String[] args) {
        try {
            // Get message from root endpoint
            String rootResponse = sendRequest("/api/v1/");
            JsonNode rootJson = objectMapper.readTree(rootResponse);
            System.out.println("Message: " + rootJson.get("message").asText());

            // Get health status
            String healthResponse = sendRequest("/api/v1/health");
            JsonNode healthJson = objectMapper.readTree(healthResponse);
            System.out.println("API Status: " + healthJson.get("status").asText());
            System.out.println("API Version: " + healthJson.get("version").asText());
            System.out.println("Uptime: " + healthJson.get("uptime_human").asText());

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static String sendRequest(String endpoint) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .GET()
                .uri(URI.create(BASE_URL + endpoint))
                .header("Accept", "application/json")
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new IOException("HTTP error: " + response.statusCode());
        }

        return response.body();
    }
}
```

## C#

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;

namespace HelloWorldApiClient
{
    class Program
    {
        private static readonly HttpClient client = new HttpClient();
        private static readonly string BaseUrl = "http://localhost:8000";

        static async Task Main(string[] args)
        {
            // Configure HttpClient
            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            client.Timeout = TimeSpan.FromSeconds(10);

            try
            {
                // Get message from root endpoint
                var rootResponse = await client.GetStringAsync($"{BaseUrl}/api/v1/");
                var rootData = JsonSerializer.Deserialize<RootResponse>(rootResponse);
                Console.WriteLine($"Message: {rootData.Message}");

                // Get health status
                var healthResponse = await client.GetStringAsync($"{BaseUrl}/api/v1/health");
                var healthData = JsonSerializer.Deserialize<HealthResponse>(healthResponse);
                Console.WriteLine($"API Status: {healthData.Status}");
                Console.WriteLine($"API Version: {healthData.Version}");
                Console.WriteLine($"Uptime: {healthData.UptimeHuman}");
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine($"Request error: {e.Message}");
            }
            catch (JsonException e)
            {
                Console.WriteLine($"JSON parsing error: {e.Message}");
            }
        }
    }

    class RootResponse
    {
        public string Message { get; set; }
    }

    class HealthResponse
    {
        public string Status { get; set; }
        public string Version { get; set; }
        public int UptimeSeconds { get; set; }
        public string UptimeHuman { get; set; }
        public SystemInfo System { get; set; }
    }

    class SystemInfo
    {
        public int ProcessId { get; set; }
        public string Hostname { get; set; }
        public double? CpuUsage { get; set; }
        public double? MemoryUsage { get; set; }
        public double? DiskUsage { get; set; }
    }
}
```

## Ruby

```ruby
require 'net/http'
require 'uri'
require 'json'

# Base URL of the API
base_url = 'http://localhost:8000'

def make_request(url)
  uri = URI(url)
  response = Net::HTTP.get_response(uri)
  
  if response.code == '200'
    JSON.parse(response.body)
  else
    puts "Error: #{response.code} - #{response.message}"
    nil
  end
end

# Get message from root endpoint
root_url = "#{base_url}/api/v1/"
root_data = make_request(root_url)

if root_data
  puts "Message: #{root_data['message']}"
end

# Get health status
health_url = "#{base_url}/api/v1/health"
health_data = make_request(health_url)

if health_data
  puts "API Status: #{health_data['status']}"
  puts "API Version: #{health_data['version']}"
  puts "Uptime: #{health_data['uptime_human']}"
end
```

## PHP

```php
<?php

// Base URL of the API
$baseUrl = 'http://localhost:8000';

/**
 * Make an HTTP request to the API
 * 
 * @param string $url The URL to request
 * @return array|null The decoded JSON response or null on error
 */
function makeRequest($url) {
    // Initialize cURL session
    $ch = curl_init();
    
    // Set cURL options
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Accept: application/json']);
    
    // Execute cURL request
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    // Check for errors
    if (curl_errno($ch) || $httpCode !== 200) {
        echo "Error: " . curl_error($ch) . " (HTTP code: $httpCode)\n";
        curl_close($ch);
        return null;
    }
    
    // Close cURL session
    curl_close($ch);
    
    // Decode JSON response
    return json_decode($response, true);
}

// Get message from root endpoint
$rootUrl = $baseUrl . '/api/v1/';
$rootData = makeRequest($rootUrl);

if ($rootData !== null) {
    echo "Message: " . $rootData['message'] . "\n";
}

// Get health status
$healthUrl = $baseUrl . '/api/v1/health';
$healthData = makeRequest($healthUrl);

if ($healthData !== null) {
    echo "API Status: " . $healthData['status'] . "\n";
    echo "API Version: " . $healthData['version'] . "\n";
    echo "Uptime: " . $healthData['uptime_human'] . "\n";
}
```

## Rust

```rust
use serde::{Deserialize, Serialize};
use reqwest::Error;

#[derive(Serialize, Deserialize, Debug)]
struct Message {
    message: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct SystemInfo {
    process_id: i32,
    hostname: String,
    cpu_usage: Option<f64>,
    memory_usage: Option<f64>,
    disk_usage: Option<f64>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Health {
    status: String,
    version: String,
    uptime_seconds: i32,
    uptime_human: String,
    system: SystemInfo,
}

async fn fetch_api_data() -> Result<(), Error> {
    let base_url = "http://localhost:8000";
    
    // Create a client with a timeout
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()?;
    
    // Get message from root endpoint
    let root_url = format!("{}/api/v1/", base_url);
    let root_response = client.get(&root_url).send().await?;
    
    if root_response.status().is_success() {
        let root_data: Message = root_response.json().await?;
        println!("Message: {}", root_data.message);
    } else {
        println!("Error: {}", root_response.status());
    }
    
    // Get health status
    let health_url = format!("{}/api/v1/health", base_url);
    let health_response = client.get(&health_url).send().await?;
    
    if health_response.status().is_success() {
        let health_data: Health = health_response.json().await?;
        println!("API Status: {}", health_data.status);
        println!("API Version: {}", health_data.version);
        println!("Uptime: {}", health_data.uptime_human);
    } else {
        println!("Error checking health: {}", health_response.status());
    }
    
    Ok(())
}

#[tokio::main]
async fn main() {
    match fetch_api_data().await {
        Ok(_) => println!("Successfully fetched API data"),
        Err(e) => eprintln!("Error: {}", e),
    }
}
```

## Shell

### curl

```bash
#!/bin/bash

# Base URL of the API
BASE_URL="http://localhost:8000"

# Function to make API requests
make_request() {
    local endpoint=$1
    local response=$(curl -s -X GET "${BASE_URL}${endpoint}" -H "Accept: application/json")
    echo "$response"
}

# Get message from root endpoint
echo "Fetching root endpoint..."
root_response=$(make_request "/api/v1/")
message=$(echo "$root_response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
echo "Message: $message"

# Get health status
echo -e "\nChecking API health..."
health_response=$(make_request "/api/v1/health")
status=$(echo "$health_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
version=$(echo "$health_response" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
uptime=$(echo "$health_response" | grep -o '"uptime_human":"[^"]*"' | cut -d'"' -f4)

echo "API Status: $status"
echo "API Version: $version"
echo "Uptime: $uptime"
```

### httpie

```bash
#!/bin/bash

# Install httpie if not already installed
# pip install httpie

# Base URL of the API
BASE_URL="http://localhost:8000"

# Get message from root endpoint
echo "Fetching root endpoint..."
http GET "${BASE_URL}/api/v1/"

# Get health status
echo -e "\nChecking API health..."
http GET "${BASE_URL}/api/v1/health"
``` 