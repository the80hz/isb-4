import json

settings = {
    "bins": ["547905"],
    "last_number": "2301",
    "hash": "140495200b351b7f18a46e3796f2875ebdf0023568933ef3b99efb285af3f06b"
}


def get_settings() -> None:
    with open('settings.json', 'w') as fp:
        json.dump(settings, fp)


if __name__ == '__main__':
    get_settings()
