import asyncio
import base64
import json
import os
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import websockets

SCREENSHOTS_DIR = os.path.abspath("docs/screenshots")
ARTIFACT_DIR = "/Users/chaitanyagidwani/.gemini/antigravity/brain/68217d68-88a8-4f6d-9ccb-0ec2a930ed42/screenshots"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

async def get_admin_tokens():
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=json.dumps({"email": "admin@datasage.ai", "password": "DataSageAdmin@2026"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["access_token"], data.get("refresh_token", "")

class ChromeClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50 * 1024 * 1024)

    async def send_cmd(self, method, params=None):
        self.msg_id += 1
        cid = self.msg_id
        payload = {"id": cid, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        while True:
            resp_raw = await self.ws.recv()
            resp = json.loads(resp_raw)
            if resp.get("id") == cid:
                return resp.get("result", {})

    async def close(self):
        if self.ws:
            await self.ws.close()

async def capture_target(client, target_url, output_filename, width=1440, height=960, pre_eval=None, scroll_y=0, wait_seconds=3):
    await client.send_cmd("Page.enable")
    await client.send_cmd("Runtime.enable")
    await client.send_cmd("DOM.enable")

    await client.send_cmd("Emulation.setDeviceMetricsOverride", {
        "width": width,
        "height": height,
        "deviceScaleFactor": 2, # High-DPI Retina
        "mobile": False
    })

    if pre_eval:
        await client.send_cmd("Runtime.evaluate", {"expression": pre_eval, "awaitPromise": True})

    await client.send_cmd("Page.navigate", {"url": target_url})
    await asyncio.sleep(wait_seconds)

    if scroll_y > 0:
        await client.send_cmd("Runtime.evaluate", {
            "expression": f"window.scrollTo({{ top: {scroll_y}, behavior: 'instant' }});",
            "awaitPromise": True
        })
        await asyncio.sleep(1)

    res = await client.send_cmd("Page.captureScreenshot", {"format": "png"})
    img_data = base64.b64decode(res["data"])

    dest1 = os.path.join(SCREENSHOTS_DIR, output_filename)
    dest2 = os.path.join(ARTIFACT_DIR, output_filename)

    with open(dest1, "wb") as f:
        f.write(img_data)
    with open(dest2, "wb") as f:
        f.write(img_data)

    print(f"Successfully captured: {output_filename} ({len(img_data) // 1024} KB)")

async def main():
    print("Obtaining admin authentication tokens...")
    access_token, refresh_token = await get_admin_tokens()
    print("Admin token obtained.")

    # Target URL initial
    new_url = "http://localhost:9222/json/new"
    req = urllib.request.Request(new_url, method="PUT")
    with urllib.request.urlopen(req) as resp:
        target_info = json.loads(resp.read().decode("utf-8"))

    ws_url = target_info["webSocketDebuggerUrl"]
    target_id = target_info["id"]
    client = ChromeClient(ws_url)
    await client.connect()

    try:
        # First navigate to origin to set localStorage auth tokens
        await client.send_cmd("Page.enable")
        await client.send_cmd("Runtime.enable")
        await client.send_cmd("Page.navigate", {"url": "http://localhost:3000"})
        await asyncio.sleep(2)

        set_auth_code = f"""
        localStorage.setItem('access_token', '{access_token}');
        localStorage.setItem('refresh_token', '{refresh_token}');
        """
        await client.send_cmd("Runtime.evaluate", {"expression": set_auth_code, "awaitPromise": True})
        print("Injected auth credentials into browser session.")

        tasks = [
            {
                "name": "01_market_landing.png",
                "url": "http://localhost:3000",
                "width": 1440,
                "height": 920,
                "scroll_y": 0,
                "wait": 3
            },
            {
                "name": "02_property_discovery.png",
                "url": "http://localhost:3000/properties",
                "width": 1440,
                "height": 940,
                "scroll_y": 0,
                "wait": 4
            },
            {
                "name": "03_property_detail_valuation.png",
                "url": "http://localhost:3000/properties/fb6602fe-848d-44c4-920f-6c2ab717423c",
                "width": 1440,
                "height": 960,
                "scroll_y": 0,
                "wait": 4
            },
            {
                "name": "04_property_detail_shap_insights.png",
                "url": "http://localhost:3000/properties/fb6602fe-848d-44c4-920f-6c2ab717423c",
                "width": 1440,
                "height": 960,
                "scroll_y": 620,
                "wait": 2
            },
            {
                "name": "05_property_comparison_matrix.png",
                "url": "http://localhost:3000/compare?ids=fb6602fe-848d-44c4-920f-6c2ab717423c,f24cd120-abaa-43da-9395-1edde18da205,ef47375a-5cad-4475-a478-f393fbf99e94",
                "width": 1440,
                "height": 960,
                "scroll_y": 0,
                "wait": 4
            },
            {
                "name": "06_admin_command_center.png",
                "url": "http://localhost:3000/admin",
                "width": 1440,
                "height": 940,
                "scroll_y": 0,
                "wait": 4
            },
            {
                "name": "07_buyer_onboarding.png",
                "url": "http://localhost:3000/onboarding",
                "width": 1440,
                "height": 920,
                "scroll_y": 0,
                "wait": 3
            }
        ]

        for item in tasks:
            print(f"Capturing {item['name']} from {item['url']}...")
            await capture_target(
                client=client,
                target_url=item["url"],
                output_filename=item["name"],
                width=item["width"],
                height=item["height"],
                scroll_y=item["scroll_y"],
                wait_seconds=item["wait"]
            )
            await asyncio.sleep(1)

        print("All updated screenshots captured successfully!")
    finally:
        await client.close()
        try:
            close_url = f"http://localhost:9222/json/close/{target_id}"
            urllib.request.urlopen(close_url)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
