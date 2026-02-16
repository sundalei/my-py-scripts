import json
import urllib.parse
import urllib.request
import platform


def find_java_url(java_version):
    # Detect current OS and Architecture
    os_map = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}
    arch_map = {
        "arm64": "aarch64",
        "aarch64": "aarch64",
        "ARM64": "aarch64",
        "AMD64": "x64",
        "x86_64": "x64"
    }

    current_os = os_map.get(platform.system(), "linux")
    current_arch = arch_map.get(platform.machine(), "x64")

    print(f"Checking for Java {java_version} on {current_os} {current_arch}")
    
    # Build the API Query
    # Documentation: https://api.foojay.io/swagger-ui/
    base_url = "https://api.foojay.io/disco/v3.0/packages"
    params = {
        "version": java_version,
        "operating_system": current_os,
        "architecture": current_arch,
        "latest": "available",
        "distribution": "temurin",
        "package_type": "jdk"
    }

    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    # Request the data
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            if not data.get("result"):
                print("No matching Java version found.")
                return

            for pkg in data["result"]:
                print("\n--- FOUND JDK ---")
                print(f"Vendor:   {pkg.get('distribution')}")
                print(f"Version:  {pkg.get('java_version')}")
                print(f"File:     {pkg.get('filename')}")
                # sha info needs further retrieval from pkg_info_uri
                # print(f"SHA256:   {pkg.get('checksum')}")
                print(f"Download: {pkg.get('links', {}).get('pkg_download_redirect')}")
                print("-----------------")
    except Exception as e:
        print(f"Error querying API: {e}")


if __name__ == "__main__":
    find_java_url(17)
