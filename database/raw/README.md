# Raw Database

## Contents of this Folder

Unless explicitly stated otherwise, all files in this directory are subject to
the licenses provided by their respective maintainers or sources. Please review
the licensing information associated with each file to ensure compliance with its
terms.

## License Information

The files in this folder may be governed by various licenses, depending on their
sources and maintainers. It is essential to adhere to the specific licensing
terms provided for each file. Please refer to the individual files or consult
their respective maintainers for detailed licensing information.

## Exceptions

In certain instances, there are exceptions to the standard licensing statement
provided above. The following list details files or components within this
directory that possess distinct licensing exceptions:

1. **Files under CC0-1.0 License**: `kaize.json`, `nautiljon.json`,
   `otakotaku.json`, `silveryasha.json`
   - These files are licensed under the [CC0-1.0 (Creative Commons Zero 1.0
   Universal)][cc0] license.

2. **Files under MIT License**: `kaize_manual.json`, `nautiljon_manual.json`,
   `otakotaku_manual.json`, `silveryasha_manual.json`
   - These files are licensed under the MIT License.

It is crucial to acknowledge that these exceptions take precedence over the
general licensing statement for the specified files or components. Please ensure
that you thoroughly comprehend and adhere to their distinct licensing terms.

## Contributions and Modifications

If you intend to contribute to or modify any of the files in this directory,
it is your responsibility to ensure that your actions comply with the applicable
licensing agreements. Be aware of any specific requirements, such as providing
proper attribution or sharing your contributions under the same license.

For `*_manual.json` files, you are free to modify the contents of the file with
following rules:

1. Key name must be exact from `aod.json`
2. Value must be a dict/object if has multiple properties, or a string or int
   if it has only one property
3. If you want to override default behavior of skipping a mapping if the syste
   already link, convert the value as an array/list of dict/object/string/int.

For example:

<!-- markdownlint-disable MD013 -->
```jsonc
{
    
    "Beyond the Boundary: Yakusoku no Kizuna": 734,
    "Baka Bakka": {
        "kaize": "fools-fools-fools",
        "kaize_id": 24511
    },
    "Circle": [{
        "kaize": "circle-music",
        "kaize_id": 24509
    }], // override default behavior. From "Circle" mapping in the service, use the 24509th entry
    "Big Order (TV)": [266], // override default behavior. From "Big Order" mapping in the service, use the 266th entry
    "Big Order": [265], // override default behavior. From "Big Order OVA" mapping in the service, use the 265th entry
}
```
<!-- markdownlint-enable MD013 -->

## Questions and Clarifications

If you have any questions or require clarification regarding the licensing of
files in this folder, do not hesitate to reach out to the respective maintainers
or refer to their documentation for guidance.

## Disclaimer

The maintainers of this repository are not responsible for any legal issues that
may arise from the misuse or misinterpretation of the licenses associated with
these files. Users and contributors are expected to follow all licensing
agreements and adhere to best practices for open-source development and usage.

Thank you for your understanding and cooperation in maintaining a respectful and
legally compliant open-source environment.

[cc0]: https://creativecommons.org/publicdomain/zero/1.0/legalcode
