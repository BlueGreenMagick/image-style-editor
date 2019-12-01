# Image Style Editor

This is an addon mainly for editing image width and height. 

## How to use

Right click on an image in editor, click on 'Image Styles'.

Accepted formats are: `300`, `240px`, `20em`, `60%`, `auto`,`--somestring`, empty, [etc](https://developer.mozilla.org/en-US/docs/Web/CSS/height). Plain numbers(eg. `300`) are automatically converted to `300px`. Values starting with `--` (eg. `--name`) are automatically converted to `var(--name)`. Trailing and leading spaces are removed. 

You can set either only the width or the height, leave the other blank, and the image should retain its aspect ratio. If it doesn't, try going into config, and change `empty_means` to `auto`.

## Differences from ImageResizer

* Uses css height and width properties to resize images, so there is no loss of quality.
* You can modify width and height individually for each image
* Can't automatically resize images on paste.

## Image Occlusion Support
This addon supports Image Occlusion Enhanced fully. The image styles can be edited on created Image Occlusion cards.

* For mask/original image fields, if both `Apply to all notes` and `Apply to all fields` are checked, the styles will be applied to all the images in other notes and other fields as well.
* Checking only `Apply to all notes`, the style is applied to images from only that field in all other notes. 
* `Apply to all fields` apply styles to only images that are in original image, or mask fields. 
* `Apply to all notes` applies image styles to the same field in all cards.
**Note**: If you have modified any field name or position, or the notetype name on Image Occlusion Enhanced notetype, the addon's configuration needs to be adjusted before using it on Image Occlusion cards.

## AnkiDroid Users

* Due to a [bug](https://github.com/ankidroid/Anki-Android/issues/5166) in AnkiDroid, if the note type uses conditional replacement, the note may become blank. Setting `hidden-div-for-image-only-field` to `true` before using editing image style should fix the issue. 

## Ankiweb

https://ankiweb.net/shared/info/1593969147

## Credits

Thanks to searene, developer of the addon [ImageResizer](https://github.com/searene/Anki-Addons/tree/master/ImageResizer)'. Some of the code for gui were reused in this addon. 
Also to glutanimate(Aristotelis P.) and others who made the addon [Image Occlusion Enhanced](https://github.com/glutanimate/image-occlusion-enhanced), which was how I figured this addon would be possible to make.
Thanks to AnKing for several feature suggestions.
