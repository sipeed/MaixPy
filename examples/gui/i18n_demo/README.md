i18n demo
=====

Please **Open this folder** in MaixVision to run, the `locales` dir is important.

## Usage

1. Coding like `main.py`, use `tr` to translate strings.
2. Execute command `maixtool i18n -d . -r` in this directory, this command will scan all source code and find all strings you want to translate and generate translation files in `locales` dir, like `en.yaml` or `zh.yaml`, the locale name can be found in [here](https://www.science.co.il/language/Locale-codes.php) or [wikipedia](https://en.wikipedia.org/wiki/Language_localisation), all letters use lower case.
3. Translate yaml files manually.
4. Run this project.


