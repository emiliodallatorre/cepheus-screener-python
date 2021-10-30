import os

from PIL import Image, ImageDraw
from device_size_model import DeviceModel


def interpolate(f_co, t_co, interval):
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]


def get_png_list() -> list:
    file_list: list = []

    for entity in os.listdir("."):
        if os.path.isfile(entity) and (entity.split(".")[1].upper() == "PNG" or entity.split(".")[1].upper() == "JPG"):
            file_list.append(entity)

    file_list.remove("iPhoneX.png")

    file_list.sort(key=lambda file: int(file.split("_")[1].split(".")[0]))

    print("Trovati: ", file_list)
    return file_list


def delete_files():
    print("Inizio ad eliminare i file...")
    if os.path.exists("result"):
        import shutil
        shutil.rmtree("result")


def load_iphone_mockup() -> Image:
    main_mockup: Image = Image.open("iPhoneX.png")

    return main_mockup


# Ci serve che vada da 623 a 1388 e da 180 a 1813.
def resize_screenshot(screenshot: Image) -> Image:
    return screenshot.resize((765, 1633))


def create_image_with_size(screenshot_path: str, iphone_mockup: Image, project_name: str, index: int,
                           device: DeviceModel, background_color: tuple, foreground_color: tuple) -> Image:
    final: Image = Image.new("RGBA", (device.width, device.height))

    screenshot: Image = resize_screenshot(Image.open(screenshot_path).convert('RGBA'))

    mockup: Image = Image.new("RGBA", iphone_mockup.size)
    mockup.alpha_composite(screenshot, dest=(623, 180))
    mockup.alpha_composite(iphone_mockup)

    (width, height) = mockup.size
    left_padding = (width - device.width) / 2
    right_padding = width - left_padding
    top_padding = (height - device.height) / 2
    bottom_padding = height - top_padding

    cropped = mockup.crop(
        (left_padding, top_padding, right_padding, bottom_padding))
    final.alpha_composite(cropped)

    if final.mode in ('RGBA', 'LA'):
        gradient = Image.new('RGBA', final.size, color=foreground_color)
        draw = ImageDraw.Draw(gradient)

        for i, color in enumerate(interpolate(foreground_color, background_color, final.width * 2)):
            draw.line([(i, 0), (0, i)], tuple(color), width=1)

        gradient.paste(final, final.split()[-1])
        final = gradient

    final = final.convert("RGB")
    final.save(f"result/{device.name}/SCREENSHOT-{project_name}-{index + 1}.jpg", "JPEG", quality=100, optimize=True,
               progressive=True)


def hex_to_rgb(hex_color: str) -> tuple:
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def main():
    project_name: str = input("Inserisci il nome del progetto: ")
    delete_files()

    iphone_mockup: Image = load_iphone_mockup()
    screenshot_paths: list = get_png_list()

    foreground_color: tuple = hex_to_rgb(input("Inserisci colore di foreground: ").lstrip("#"))
    background_color: tuple = hex_to_rgb(input("Inserisci colore di background: ").lstrip("#"))

    device_sizes: list = [
        DeviceModel(1242, 2688, "6.5"),
        # DeviceModel(1125, 2436, "5.8"),
        DeviceModel(1242, 2208, "5.5"),
        DeviceModel(2048, 2732, "iPadPro12.9"),
    ]

    if not os.path.exists("result"):
        os.mkdir("result")

    for device_size in device_sizes:
        print(f"Comincio a processare le immagini per {device_size.name}...")
        for screenshot in screenshot_paths:
            print(
                f"Siamo al {str(round(((screenshot_paths.index(screenshot) + 1) / len(screenshot_paths)), 4) * 100)}% per questo dispositivo.")

            if not os.path.exists(f"result/{device_size.name}/"):
                os.mkdir(f"result/{device_size.name}/")

            create_image_with_size(screenshot, iphone_mockup, project_name, screenshot_paths.index(screenshot),
                                   device_size, background_color, foreground_color)


main()
