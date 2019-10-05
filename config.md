### Image Style Editor

Please note that modifying a configuration may need a restart for it to apply.

- `empty_means`(string): If either width or height field is empty and the other is not, the empty field will be set to the string. For example, `auto`, `inherit`, etc. Default: `""`.
- `max-size`(true/false): If set to `true`, you can edit `max-width` and `max-height` property. Default: `false`.
- `min-size`(true/false): If set to `true`, you can edit `min-width` and `min-height` property. Default: `false`.

##### Image Occlusion addon related Configs

If you do not use the addon 'Image Occlusion Enhanced', then these configs will do nothing.
Also, please make sure before using, that the **id field** is in **position 1**, and the below three configs are set correctly. 

- `image-occlusion-field-position`(list of number): The positions of image fields of `Image Occlusion Enhanced` note type. If you haven't changed it, the default is: `[3,4,10,11]`
- `image-occlusion-id-field`(string): Name of the id field of `Image Occlusion Enhanced` note type. If you haven't changed it, the default is: `ID (hidden)`
- `image-occl-note-type`(string): Name of the `Image Occlusion Enhanced` note type. Default: `"Image Occlusion Enhanced"`.
