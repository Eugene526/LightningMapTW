import io
import zipfile
import asyncio
import time
from datetime import datetime
from aiohttp import web, ClientSession
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from lxml import etree

cached_image = None
last_updated = None

# --- 在這裡填入你的中央氣象局 API Key ---
API_KEY = "API_KEY"
async def fetch_kmz():
    url = (
        f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0039-001"
        f"?Authorization={API_KEY}"
        "&downloadType=WEB&format=KMZ"
    )

    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"下載失敗：{resp.status}")
            return await resp.read()


def parse_kml(kml_bytes):
    root = etree.fromstring(kml_bytes)
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    data = []
    placemarks = root.xpath('.//kml:Placemark', namespaces=ns)
    for pm in placemarks:
        coords_node = pm.find('.//kml:Point/kml:coordinates', namespaces=ns)
        time_node = pm.find('.//kml:TimeStamp/kml:when', namespaces=ns)
        if coords_node is not None and time_node is not None:
            lon_str, lat_str, *_ = coords_node.text.strip().split(',')
            lon = float(lon_str)
            lat = float(lat_str)
            dt = datetime.fromisoformat(time_node.text.strip().replace("Z", "+00:00"))
            data.append((lon, lat, dt))
    return data


def generate_map(data):
    if not data:
        return None

    start_time = min(d[2] for d in data)
    end_time = max(d[2] for d in data)
    total_seconds = max((end_time - start_time).total_seconds(), 1)

    segments = 5
    colors = ['yellow', 'gold', 'orange', 'orangered', 'red']

    fig = plt.figure(figsize=(9, 11))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([116, 126, 20, 28], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor='black')
    ax.add_feature(cfeature.OCEAN, facecolor='#1a1a1a')
    ax.add_feature(cfeature.COASTLINE, edgecolor='lightgray', linewidth=1.2)
    ax.add_feature(cfeature.BORDERS, edgecolor='lightgray', linewidth=1.0)
    ax.add_feature(cfeature.LAKES, facecolor='black')
    ax.add_feature(cfeature.RIVERS, edgecolor='gray')

    gl = ax.gridlines(draw_labels=True, color='gray', alpha=0.3, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'color': 'white', 'fontsize': 10}
    gl.ylabel_style = {'color': 'white', 'fontsize': 10}

    for lon, lat, dt in data:
        elapsed = (dt - start_time).total_seconds()
        segment_index = int(elapsed / total_seconds * (segments - 1))
        color = colors[segment_index]
        ax.plot(lon, lat, marker='+', color=color, markersize=12, markeredgewidth=3,
                transform=ccrs.PlateCarree(), zorder=10)

    plt.title("Real-time Lightning Observation Map", fontsize=20, color='white', pad=25)
    buffer = io.BytesIO()
    plt.savefig(buffer, bbox_inches='tight', dpi=180, facecolor='black', format='png')
    plt.close()
    buffer.seek(0)
    return buffer


async def update_cache_every_3_hours():
    global cached_image, last_updated
    while True:
        print("⏳ 正在更新快取圖像...")
        try:
            kmz_content = await fetch_kmz()
            kmz = zipfile.ZipFile(io.BytesIO(kmz_content))
            kml_filename = [name for name in kmz.namelist() if name.endswith('.kml')][0]
            kml_bytes = kmz.read(kml_filename)

            data = parse_kml(kml_bytes)
            img_buffer = generate_map(data)

            if img_buffer:
                cached_image = img_buffer.read()
                last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"✅ 快取更新成功！時間：{last_updated}")
        except Exception as e:
            print(f"❌ 更新失敗：{e}")

        await asyncio.sleep(1 * 60 * 60)  # 一小時


async def handle(request):
    if cached_image:
        return web.Response(body=cached_image, content_type='image/png')
    else:
        return web.Response(text="快取尚未準備好，請稍後再試")


async def on_startup(app):
    app['update_task'] = asyncio.create_task(update_cache_every_3_hours())


app = web.Application()
app.router.add_get('/', handle)
app.on_startup.append(on_startup)

if __name__ == '__main__':
    web.run_app(app, port=4444)
