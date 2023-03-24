import random
import re
import traceback

import gradio as gr

from modules import script_callbacks, scripts, shared
from modules.shared import opts
import requests
import bs4
from bs4 import BeautifulSoup


def on_ui_settings():
    section = ("gelbooru-prompt", "Gelbooru Prompt")


def fetch(image, post_id):
    if post_id:
        url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id={post_id}"
    else:
        # update hash based on image
        name = image.orig_name
        print("name: " + name)
        hash = name.split(".")[0]
        if hash.startswith("sample_"):
            hash = hash.replace("sample_", "")
        if hash.startswith("thumbnail_"):
            hash = hash.replace("thumbnail_", "")
        print("hash: " + hash)

        url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=md5:" + hash
    req = requests.get(url)
    data = req.json()
    if data["@attributes"]["count"] > 1:
        return "No image found with that hash or ID..."
    else:
        post = data["post"][0]
        tags = post["tags"]

        parsed = []
        for tag in tags.split():
            tag = tag.replace("_", " ").replace("(", "\\(").replace(")", "\\)")
            parsed.append(tag)
        parsed = (", ").join(parsed)
        return parsed


class BooruPromptsScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return "Gelbooru Prompt"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("Gelbooru Prompt", open=False):
                fetch_tags = gr.Button(value="Get Tags", variant="primary")
                image = gr.File(type="file", label="Image with MD5 Hash")
                post_id = gr.Textbox(value="", label="Post ID", lines=1)
                tags = gr.Textbox(value="", label="Tags", lines=5)

        fetch_tags.click(fn=fetch, inputs=[image, post_id], outputs=[tags])
        return [image, post_id, tags, fetch_tags]


script_callbacks.on_ui_settings(on_ui_settings)
