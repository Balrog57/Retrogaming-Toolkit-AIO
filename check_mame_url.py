import requests

def check_urls():
    base = "https://github.com/mamedev/mame/releases/download/mame0284/"
    candidates = [
        "mame0284b_64bit.exe",
        "mame0284_64bit.exe",
        "mame0284b_x64.exe",
        "mame0284_x64.exe",
        "mame0284b_windows_64bit.exe"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for c in candidates:
        url = base + c
        try:
            r = requests.head(url, headers=headers, allow_redirects=True)
            print(f"{c}: {r.status_code}")
            if r.status_code == 200:
                print(f"FOUND: {url}")
                return url
        except Exception as e:
            print(f"{c}: Error {e}")
            
    return None

if __name__ == "__main__":
    check_urls()
