"""
HTTP Client for GUGiK APIs

Refactored from service_api.py - NO PyQGIS dependencies
Uses pure Python: requests, lxml, socket

Based on pobieracz_danych_gugik QGIS plugin
Original: https://github.com/envirosolutionspl/pobieracz_danych_gugik
Authors: EnviroSolutions Sp. z o.o.
License: GPL-3.0
"""
import requests
import lxml.etree as ET
from requests.exceptions import ConnectionError, ChunkedEncodingError, Timeout
import os
import time
import socket
import logging
from typing import Tuple, List, Optional, Callable
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings (like original)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)


class GugikHttpClient:
    """HTTP client for communication with GUGiK APIs"""
    
    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.session.verify = False  # Like original service_api.py
        self.timeout = timeout
    
    def get_request(self, params: dict, url: str, max_attempts: int = 3) -> Tuple[bool, str]:
        """
        GET request with retry logic
        Replacement for getRequest() from service_api.py
        """
        attempt = 0
        while attempt <= max_attempts:
            if not self._is_internet_connected():
                return False, 'Połączenie zostało przerwane'
            try:
                response = self.session.get(url=url, params=params, timeout=self.timeout)
                if response.status_code == 200:
                    return True, response.text
                else:
                    return False, f'Błąd {response.status_code}'
            except ConnectionError:
                attempt += 1
                time.sleep(2)
        return False, 'Przekroczono maksymalną liczbę prób'
    
    def download_file(self, url: str, dest_folder: str, progress_callback: Optional[Callable[[int, int], None]] = None, cancel_check: Optional[Callable[[], bool]] = None) -> Tuple[bool, str]:
        """Download file with progress tracking - Replacement for retreiveFile()"""
        file_name = self._generate_filename(url)
        path = os.path.join(dest_folder, file_name)
        
        try:
            response = self.session.get(url=url, stream=True, timeout=60)
            if response.status_code == 404:
                return False, "Plik nie istnieje"
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            self._cleanup_file(path)
            os.makedirs(dest_folder, exist_ok=True)
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if cancel_check and cancel_check():
                        response.close()
                        self._cleanup_file(path)
                        return False, "Pobieranie anulowane"
                    
                    if downloaded % 10000000 == 0:
                        if not self._is_internet_connected():
                            response.close()
                            self._cleanup_file(path)
                            return False, 'Połączenie zostało przerwane'
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
            
            response.close()
            logger.info(f"Downloaded: {file_name} ({downloaded / 1024 / 1024:.2f} MB)")
            return True, path
        except (ConnectionError, ChunkedEncodingError) as e:
            self._cleanup_file(path)
            logger.error(f"Download error: {e}")
            return False, 'Połączenie zostało przerwane'
        except IOError as e:
            logger.error(f"File write error: {e}")
            return False, "Błąd zapisu pliku"
    
    def get_wms_layers(self, url: str, service: str = "WMS") -> List[str]:
        """Get layers from WMS GetCapabilities - Replacement for getAllLayers()"""
        params = {"SERVICE": service, "REQUEST": "GetCapabilities", "VERSION": "1.3.0"}
        ok, payload = self.get_request(params, url)
        if not ok or not payload:
            return []
        
        parser = ET.XMLParser(recover=True)
        try:
            root = ET.fromstring(payload.encode("utf-8"), parser=parser)
        except Exception:
            root = ET.fromstring(payload, parser=parser)
        
        ns_uri = None
        try:
            ns_uri = root.nsmap.get(None)
        except AttributeError:
            ns_uri = None
        
        layers = []
        if ns_uri:
            ns = {"wms": ns_uri}
            names = root.xpath(".//wms:Capability//wms:Layer[wms:Name]/wms:Name", namespaces=ns)
            layers = [el.text for el in names if el is not None and el.text]
        else:
            for layer in root.findall(".//Layer"):
                name_el = layer.find("Name")
                if name_el is not None and name_el.text:
                    layers.append(name_el.text)
        
        return list(dict.fromkeys(layers))
    
    def check_connection(self) -> bool:
        """Check connection to GUGiK services"""
        try:
            resp = self.session.get(url='https://uldk.gugik.gov.pl/', timeout=5)
            return resp.status_code == 200
        except (Timeout, ConnectionError):
            return False
    
    def _is_internet_connected(self) -> bool:
        """Check internet connection"""
        try:
            host = socket.gethostbyname("www.google.com")
            s = socket.create_connection((host, 80), 2)
            s.close()
            return True
        except (Timeout, ConnectionError, socket.error):
            return False
    
    def _generate_filename(self, url: str) -> str:
        """Generate filename from URL - Logic from original retreiveFile()"""
        file_name = url.split('/')[-1]
        if '?' in file_name:
            file_name = (file_name.split('?')[-1].replace('=', '_')) + '.zip'
        
        if 'Budynki3D' in url:
            if 'LOD1' in url:
                file_name = f"Budynki_3D_LOD1_{file_name}"
            elif 'LOD2' in url:
                file_name = f"Budynki_3D_LOD2_{file_name}"
            if len(url.split('/')) == 9:
                file_name = url.split('/')[6] + '_' + file_name
        elif 'PRG' in url:
            file_name = f"PRG_{file_name}"
        elif 'bdot10k' in url and 'Archiwum' not in url:
            file_name = f"bdot10k_{file_name}"
        elif 'Archiwum' in url and 'bdot10k' in url:
            file_name = "archiwalne_bdot10k_" + url.split('/')[5] + '_' + file_name
        elif 'bdoo' in url:
            file_name = "bdoo_" + 'rok' + url.split('/')[4] + '_' + file_name
        elif 'ZestawieniaZbiorczeEGiB' in url:
            file_name = "ZestawieniaZbiorczeEGiB_" + 'rok' + url.split('/')[4] + '_' + file_name
        elif 'osnowa' in url:
            file_name = f"podstawowa_osnowa_{file_name}"
        
        return file_name
    
    @staticmethod
    def _cleanup_file(path: str):
        """Remove file if exists"""
        if os.path.exists(path):
            os.remove(path)
