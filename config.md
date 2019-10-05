## Image Style Editor

Please note that modifying a configuration may need a restart for it to apply.

- `empty_means`(string): If either width or height field is empty and the other is not, the empty field will be set to the string. For example, `auto`, `inherit`, etc. Default: `""`.
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
Also, please make sure before using, that the **id field** is in **position 1**, and the below three configs are set correctly. 

- `zzimage-occlusion-field-position`(list of number): The positions of image fields of `Image Occlusion Enhanced` note type. If you haven't changed it, the default is: `[3,4,10,11]`.
- `zzimage-occlusion-id-field`(string): Name of the id field of `Image Occlusion Enhanced` note type. If you haven't changed it, the default is: `ID (hidden)`.
- `zzimage-occl-note-type`(string): Name of the `Image Occlusion Enhanced` note type. Default: `"Image Occlusion Enhanced"`.

