import webbrowser


def browse(url):
    print('Open', url)
    webbrowser.open_new_tab(url)
