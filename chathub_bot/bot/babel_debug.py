import gettext


def list_translations(mo_file_path, locale_dir, domain):
    # Load the .mo file
    translation = gettext.translation(domain, localedir=locale_dir, languages=[mo_file_path],
                                      fallback=True)
    translation.install()

    # Access messages catalog
    catalog = translation._catalog

    # List all available messages
    for msgid in catalog:
        print(f'Message ID: {msgid}\nTranslation: {catalog[msgid]}\n------------')


# Example usage:
# Assuming your .mo files are stored in 'locales/en/LC_MESSAGES/domain.mo'
list_translations('ru', 'locales', 'bot')
