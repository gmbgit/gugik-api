# GUGiK API

A REST API service for downloading spatial data from GUGiK (Head Office of Geodesy and Cartography) Poland.

## Description

This service provides a simple REST API interface for accessing and downloading various types of spatial data from GUGiK Poland. It wraps the functionality of the original pobieracz_danych_gugik project and exposes it as a web service, making it easy to integrate GUGiK data downloads into your applications.

The API allows you to query and download different types of geospatial data including orthophotos, elevation models, LiDAR point clouds, and various vector datasets covering Poland.

## Quick Start

### Using Docker

```bash
# Pull and run the Docker container
docker pull gmbgit/gugik-api:latest
docker run -p 8080:8080 gmbgit/gugik-api:latest

# The API will be available at http://localhost:8080
```

### Using Python

```bash
# Clone the repository
git clone https://github.com/gmbgit/gugik-api.git
cd gugik-api

# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py

# The API will be available at http://localhost:8080
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI JSON**: `http://localhost:8080/openapi.json`

## Available Data Types

| Data Type | Code | Description |
|-----------|------|-------------|
| Orthophoto | `ortofoto` | High-resolution aerial imagery |
| Digital Terrain Model | `nmt` | Elevation data representing bare earth |
| Digital Surface Model | `nmpt` | Elevation data including all surface objects |
| LiDAR Point Cloud | `las` | Raw LiDAR point cloud data in LAS format |
| WFS Services | `wfs` | Web Feature Service endpoints |
| BDOT10k | `bdot` | Topographic Objects Database (1:10000) |
| PRG | `prg` | State Register of Borders and Areas |
| EGiB | `egib` | Land and Buildings Registry |

## API Usage Examples

### Using cURL

#### Get available orthophoto data for a bounding box

```bash
curl -X POST "http://localhost:8080/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "ortofoto",
    "bbox": {
      "min_x": 20.9,
      "min_y": 52.1,
      "max_x": 21.1,
      "max_y": 52.3
    }
  }'
```

#### Download data

```bash
curl -X POST "http://localhost:8080/api/v1/download" \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "ortofoto",
    "bbox": {
      "min_x": 20.9,
      "min_y": 52.1,
      "max_x": 21.1,
      "max_y": 52.3
    },
    "output_path": "/data/downloads"
  }' \
  -o download.zip
```

#### Get service status

```bash
curl -X GET "http://localhost:8080/api/v1/status"
```

### Using .NET C#

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class GugikApiClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public GugikApiClient(string baseUrl = "http://localhost:8080")
    {
        _httpClient = new HttpClient();
        _baseUrl = baseUrl;
    }

    public async Task<string> QueryDataAsync(string dataType, BoundingBox bbox)
    {
        var request = new
        {
            data_type = dataType,
            bbox = new
            {
                min_x = bbox.MinX,
                min_y = bbox.MinY,
                max_x = bbox.MaxX,
                max_y = bbox.MaxY
            }
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/query", content);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadAsStringAsync();
    }

    public async Task<byte[]> DownloadDataAsync(string dataType, BoundingBox bbox, string outputPath)
    {
        var request = new
        {
            data_type = dataType,
            bbox = new
            {
                min_x = bbox.MinX,
                min_y = bbox.MinY,
                max_x = bbox.MaxX,
                max_y = bbox.MaxY
            },
            output_path = outputPath
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/download", content);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadAsByteArrayAsync();
    }

    public async Task<string> GetStatusAsync()
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/api/v1/status");
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadAsStringAsync();
    }
}

public class BoundingBox
{
    public double MinX { get; set; }
    public double MinY { get; set; }
    public double MaxX { get; set; }
    public double MaxY { get; set; }
}

// Example usage
public class Program
{
    public static async Task Main(string[] args)
    {
        var client = new GugikApiClient();

        // Query orthophoto data for Warsaw
        var warsawBbox = new BoundingBox
        {
            MinX = 20.9,
            MinY = 52.1,
            MaxX = 21.1,
            MaxY = 52.3
        };

        try
        {
            var queryResult = await client.QueryDataAsync("ortofoto", warsawBbox);
            Console.WriteLine($"Query result: {queryResult}");

            var downloadData = await client.DownloadDataAsync("ortofoto", warsawBbox, "/data/downloads");
            Console.WriteLine($"Downloaded {downloadData.Length} bytes");

            var status = await client.GetStatusAsync();
            Console.WriteLine($"Service status: {status}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

## Example Bounding Boxes for Polish Cities

### Warsaw (Warszawa)
```json
{
  "min_x": 20.8517,
  "min_y": 52.0978,
  "max_x": 21.2711,
  "max_y": 52.3676
}
```

### Krakow (Kraków)
```json
{
  "min_x": 19.7937,
  "min_y": 49.9678,
  "max_x": 20.2151,
  "max_y": 50.1280
}
```

### Gdansk (Gdańsk)
```json
{
  "min_x": 18.4685,
  "min_y": 54.2797,
  "max_x": 18.7804,
  "max_y": 54.4396
}
```

### Wroclaw (Wrocław)
```json
{
  "min_x": 16.8188,
  "min_y": 51.0363,
  "max_x": 17.1708,
  "max_y": 51.2016
}
```

### Poznan (Poznań)
```json
{
  "min_x": 16.8076,
  "min_y": 52.3374,
  "max_x": 17.0656,
  "max_y": 52.4808
}
```

### Lodz (Łódź)
```json
{
  "min_x": 19.3387,
  "min_y": 51.6783,
  "max_x": 19.6415,
  "max_y": 51.8485
}
```

**Note:** All coordinates are in WGS84 (EPSG:4326) coordinate system.

## Configuration

### Environment Variables

You can configure the service using the following environment variables:

```bash
# Server configuration
HOST=0.0.0.0
PORT=8080
DEBUG=false

# API settings
API_TITLE="GUGiK API"
API_VERSION="1.0.0"
API_PREFIX="/api/v1"

# Download settings
MAX_DOWNLOAD_SIZE_MB=500
TEMP_DIR=/tmp/gugik-api
TIMEOUT_SECONDS=300

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration File

Alternatively, you can use a `config.yaml` file:

```yaml
server:
  host: 0.0.0.0
  port: 8080
  debug: false

api:
  title: "GUGiK API"
  version: "1.0.0"
  prefix: "/api/v1"

download:
  max_size_mb: 500
  temp_dir: "/tmp/gugik-api"
  timeout_seconds: 300

logging:
  level: "INFO"
  format: "json"
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  gugik-api:
    image: gmbgit/gugik-api:latest
    ports:
      - "8080:8080"
    environment:
      - HOST=0.0.0.0
      - PORT=8080
      - LOG_LEVEL=INFO
    volumes:
      - ./downloads:/data/downloads
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
```

## Development

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/gmbgit/gugik-api.git
cd gugik-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with hot reload
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### GPL-3.0 License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Acknowledgments

This project is based on the excellent work of **EnviroSolutions Sp. z o.o.** and their original project:

**pobieracz_danych_gugik** - https://github.com/envirosolutionspl/pobieracz_danych_gugik

We are grateful for their contribution to the open-source community and for making spatial data from GUGiK more accessible to developers and researchers.

### Original Project Credits

- **Original Author**: EnviroSolutions Sp. z o.o.
- **Original Repository**: https://github.com/envirosolutionspl/pobieracz_danych_gugik
- **License**: Check the original repository for licensing information

This REST API wrapper extends the functionality of the original project by providing a web service interface, making it easier to integrate GUGiK data access into modern applications and workflows.

## Support

- **Issues**: https://github.com/gmbgit/gugik-api/issues
- **Discussions**: https://github.com/gmbgit/gugik-api/discussions

## Disclaimer

This is an unofficial service and is not affiliated with or endorsed by GUGiK (Główny Urząd Geodezji i Kartografii). All data is sourced from official GUGiK services. Please respect GUGiK's terms of service and usage policies when using this API.

---

**Made with ❤️ for the geospatial community**
