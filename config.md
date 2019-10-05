## Image Style Editor

Please note that modifying a configuration may need a restart for it to apply.

- `empty_means`(string): If either width or height field is empty and the other is not, the empty field will be set to the string. For example, `auto`, `inherit`, etc. Default: `""`.
- `hidden-div-for-image-only-field`(true/false): If your notetype uses conditional replacement, and use AnkiDroid, set it to `true` or the image may not show due to a bug in AnkiDroid. Default: `false`.
- `max-size`(true/false): If set to `true`, you can edit `max-width` and `max-height` property. Default: `false`.
- `min-size`(true/false): If set to `true`, you can edit `min-width` and `min-height` property. Default: `false`.

#### Default Values (zdefaults)

Default values are put into the Image Style Editor if the image does not have any styling. You will still need to open the Image Style Editor and click 'Ok'.
Clicking 'Default' will override all fields with these values.

- `width`(string): Default: `""`.
- `height`(string): Default: `""`.
- `min-width`(string): Default: `""`.
- `min-height`(string): Default: `""`.
- `max-width`(string): Default: `""`.
- `max-height`(string): Default: `""`.
- `Apply to all notes`(true/false): Default: `true`.
- `Apply to all fields`(true/false): Default: `true`.

#### Image Occlusion addon related Configs

If you do not use the addon 'Image Occlusion Enhanced', then these configs will do nothing.
If you haven't changed the note type name or field names or positions in Image Occlusion Enhanced note type, you can ignore these configs as well.
If you have, please make sure before using this addon, that the **id field** is in **position 1**, and the below three configs(1, 3, 4) are set correctly. And the first number from `zzimage-occlusion-field-position` is the 'Image' field's position.

- `zzimage-occlusion-field-position`(list of number): The positions of image fields of `Image Occlusion Enhanced` note type. If you haven't changed it, the default is: `[3,4,10,11]`.
- `zzimage=occlusion-hiddendiv`(true/false): Adds hidden div in 'Image' field. Must set it to `true` if using AnkiDroid, due to a bug. Default: `true`.
- `zzimage-occlusion-id-field`(string): Name of the id field of `Image Occlusion Enhanced` note type. If you haven't changed it, the default is: `ID (hidden)`.
- `zzimage-occl-note-type`(string): Name of the `Image Occlusion Enhanced` note type. Default: `"Image Occlusion Enhanced"`.

