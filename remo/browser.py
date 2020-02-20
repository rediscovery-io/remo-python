import webbrowser


def browse(url: str):
    print('Open', url)
    webbrowser.open_new_tab(url)
